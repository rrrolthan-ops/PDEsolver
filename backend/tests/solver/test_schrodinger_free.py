"""Tests for the free-particle Schrödinger equation on the real line."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _free_problem(psi0: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="i*hbar*u_t = -hbar^2/(2*m) * u_{xx}",
        equation_kind="schrodinger",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],  # unbounded line, no BCs
        initial_conditions=[InitialCondition(order=0, value=psi0)],
        parameters={"hbar": "positive", "m": "positive"},
    )


X = sp.Symbol("x", real=True)
T = sp.Symbol("t", real=True, nonnegative=True)
HBAR = sp.Symbol("hbar", positive=True)
M = sp.Symbol("m", positive=True)


def test_routes_to_free():
    resp = solve(_free_problem("exp(-x^2)"))
    assert resp.method == "schrodinger_free"


def test_oscillator_still_routes_to_oscillator():
    """The omega²x² signature must still pick the oscillator, not free."""
    oscillator = PDEProblem(
        equation_latex="i*hbar*u_t = -hbar^2/(2*m) * u_{xx} + (1/2)*m*omega^2*x^2 * u",
        equation_kind="schrodinger",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],
        initial_conditions=[InitialCondition(order=0, value="exp(-x^2/2)")],
        parameters={"hbar": "positive", "m": "positive", "omega": "positive"},
    )
    resp = solve(oscillator)
    assert resp.method == "schrodinger_oscillator"


def test_well_still_routes_to_well():
    """Bounded interval + Dirichlet must still pick the well, not free."""
    well = PDEProblem(
        equation_latex="i*hbar*u_t = -hbar^2/(2*m) * u_{xx}",
        equation_kind="schrodinger",
        domain=Domain(x=["0", "L"], t=["0", "infty"]),
        boundary_conditions=[
            {"type": "dirichlet", "where": "x=0", "value": "0"},
            {"type": "dirichlet", "where": "x=L", "value": "0"},
        ],
        initial_conditions=[InitialCondition(order=0, value="sqrt(2/L)*sin(pi*x/L)")],
        parameters={"L": "positive", "hbar": "positive", "m": "positive"},
    )
    resp = solve(well)
    assert resp.method == "schrodinger_well"


def test_propagator_satisfies_schrodinger_equation():
    """K(x, t) = √(m/(2π i ℏ t)) exp(i m x² / (2 ℏ t)) satisfies
    iℏ K_t = -(ℏ²/2m) K_xx. This is what the verification step checks.
    """
    K = sp.sqrt(M / (2 * sp.pi * sp.I * HBAR * T)) * sp.exp(
        sp.I * M * X**2 / (2 * HBAR * T)
    )
    lhs = sp.simplify(sp.I * HBAR * sp.diff(K, T))
    rhs = sp.simplify(-(HBAR**2) / (2 * M) * sp.diff(K, X, 2))
    assert sp.simplify(lhs - rhs) == 0


def test_solution_has_imaginary_unit():
    """ψ for Schrödinger is complex; the formula must carry an i."""
    resp = solve(_free_problem("exp(-x^2)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    assert sol.has(sp.I)


def test_solution_depends_on_x_t_hbar_m():
    resp = solve(_free_problem("exp(-x^2)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    free_symbols_names = {s.name for s in sol.free_symbols}
    assert "x" in free_symbols_names
    assert "t" in free_symbols_names
    assert "hbar" in free_symbols_names
    assert "m" in free_symbols_names


def test_pedagogy_mentions_fourier_and_propagator():
    resp = solve(_free_problem("exp(-x^2)"))
    all_text = " ".join(
        s.title + " " + s.explanation_md for s in resp.steps
    ).lower()
    assert "fourier" in all_text
    assert "propagador" in all_text
    # Convolution should appear too.
    assert "convoluc" in all_text


def test_pedagogy_mentions_dispersion_or_spreading():
    resp = solve(_free_problem("exp(-x^2)"))
    interp = next(s for s in resp.steps if s.kind == "interpretation")
    txt = interp.explanation_md.lower()
    assert "dispers" in txt or "ensanch" in txt


def test_pedagogy_contrasts_with_heat_via_wick():
    """The Wick rotation is one of the marquee teaching points."""
    resp = solve(_free_problem("exp(-x^2)"))
    all_text = " ".join(
        s.title + " " + s.explanation_md for s in resp.steps
    ).lower()
    # Either the explicit "Wick" term in observations or the heat-vs-
    # Schrödinger contrast in templates should appear.
    has_wick = "wick" in all_text
    has_contrast = "calor" in all_text and (
        "schr" in all_text or "cuánt" in all_text
    )
    assert has_wick or has_contrast


def test_method_choice_mentions_dispersion_relation():
    resp = solve(_free_problem("exp(-x^2)"))
    pde_to_ode_steps = [s for s in resp.steps if s.kind == "development"]
    text = " ".join(s.explanation_md for s in pde_to_ode_steps).lower()
    assert "dispers" in text or "omega(k)" in text or "\\omega(k)" in text


def test_response_has_verification_step():
    resp = solve(_free_problem("exp(-x^2)"))
    verif_steps = [s for s in resp.steps if s.kind == "verification"]
    # Intro + propagator-PDE check + unitarity argument.
    assert len(verif_steps) >= 3


def test_plot_is_density_xt():
    resp = solve(_free_problem("exp(-x^2)"))
    plot = resp.plot_data
    assert plot is not None
    assert plot.get("kind") == "surface_xt"
    # |ψ|² is non-negative everywhere.
    for row in plot["u"]:
        for v in row:
            assert v >= -1e-9, f"negative density: {v}"
            assert v == v  # not NaN


def test_plot_density_total_decreases_at_center():
    """Wave packet spreading: peak density at x=0 should *decrease* with t.

    This is the qualitative signature of dispersion: the maximum height of
    |ψ|² goes down as the packet broadens.
    """
    resp = solve(_free_problem("exp(-x^2)"))
    plot = resp.plot_data
    # plot["u"] is indexed [t][x]. Find peak across x for first and last t.
    peak_at_t0 = max(plot["u"][0])
    peak_at_tend = max(plot["u"][-1])
    assert peak_at_tend < peak_at_t0
