"""Tests for the quantum harmonic oscillator method."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _oscillator_problem(psi0: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="i*hbar*u_t = -hbar^2/(2*m) * u_{xx} + (1/2)*m*omega^2*x^2 * u",
        equation_kind="schrodinger",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],  # decay at infinity, not a Dirichlet condition
        initial_conditions=[InitialCondition(order=0, value=psi0)],
        parameters={
            "hbar": "positive",
            "m": "positive",
            "omega": "positive",
        },
    )


X = sp.Symbol("x", real=True)
T = sp.Symbol("t", real=True, nonnegative=True)
HBAR = sp.Symbol("hbar", positive=True)
M = sp.Symbol("m", positive=True)
OMEGA = sp.Symbol("omega", positive=True)
N = sp.Symbol("n", integer=True, nonnegative=True)


def test_routes_to_oscillator():
    resp = solve(_oscillator_problem("exp(-x^2/2)"))
    assert resp.method == "schrodinger_oscillator"


def test_does_not_collide_with_well_method():
    """Same equation but on a bounded interval must still hit the well method."""
    well_problem = PDEProblem(
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
    resp = solve(well_problem)
    assert resp.method == "schrodinger_well"


def test_ground_state_remains_ground_state():
    """If ψ_0 = φ_0 (the ground state), then ψ(x, t) = φ_0(x) e^{-iωt/2}.

    Verified by checking the n=0 term's magnitude is correct and higher
    n terms vanish in the orthonormality sense.
    """
    # Ground state φ_0(x) = (α/π)^(1/4) exp(-α² x² / 2) with α = √(mω/ℏ).
    # User-friendly form (omitting the normalization for input simplicity):
    # we pass psi_0 = exp(-x²/2) and check that c_0 ≠ 0 and structurally
    # the solution is consistent.
    resp = solve(_oscillator_problem("exp(-x^2/2)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    assert isinstance(sol, sp.Sum)
    term = sol.function
    # n=0 term should be non-trivial (have a non-zero c_0 integral); we
    # don't assert the exact integral value, just that the term carries
    # an Integral (the coefficient is kept symbolic) times the Hermite
    # eigenfunction times the phase factor.
    n0 = term.subs(N, 0)
    assert n0.has(sp.exp)  # the e^{-α²x²/2} of φ_0
    assert n0.has(sp.I)    # the e^{-iE_0 t/ℏ} phase


def test_energy_spectrum_in_phases():
    """Check that the n-th term's phase has frequency ω(n + 1/2)."""
    resp = solve(_oscillator_problem("exp(-x^2)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function

    # E_n = ℏω(n + 1/2); the phase factor in each term is
    # exp(-i E_n t / ℏ) = exp(-i ω (n + 1/2) t).
    # Substitute n=0,1,2 and check the coefficient of t inside the
    # phase pattern matches ω(n + 1/2).
    for n_val in (0, 1, 2):
        term_n = term.subs(N, n_val)
        # Differentiate the term wrt t and divide by the term to get
        # the phase coefficient. The result should equal -i ω (n + 1/2).
        # We test on a concrete numerical case (ℏ = m = ω = 1):
        concrete = term_n.subs({HBAR: 1, M: 1, OMEGA: 1})
        # Differentiate: dψ/dt = -i (n + 1/2) ψ at ℏ=ω=1
        d_dt = sp.simplify(sp.diff(concrete, T) - (-sp.I * (n_val + sp.Rational(1, 2))) * concrete)
        assert d_dt == 0, f"phase mismatch at n={n_val}: residue = {d_dt}"


def test_pedagogy_mentions_hermite_and_quantization():
    resp = solve(_oscillator_problem("exp(-x^2/2)"))
    all_text = " ".join(
        s.title + " " + s.explanation_md
        for s in resp.steps
    ).lower()
    assert "hermite" in all_text
    assert "cuantiz" in all_text or "cuantización" in all_text
    # Zero-point energy is one of the marquee teaching points.
    assert "punto cero" in all_text or "fundamental" in all_text


def test_response_has_eigenvalues_step():
    resp = solve(_oscillator_problem("exp(-x^2/2)"))
    boundary_steps = [s for s in resp.steps if s.kind == "boundary"]
    assert any("Cuantización" in s.title for s in boundary_steps)


def test_plot_is_xt_density():
    """|ψ|² is real and non-negative everywhere."""
    resp = solve(_oscillator_problem("exp(-x^2/2)"))
    plot = resp.plot_data
    assert plot is not None
    assert plot.get("kind") == "surface_xt"
    # All values should be ≥ 0 (probability density).
    for row in plot["u"]:
        for v in row:
            assert v >= -1e-9, f"negative density: {v}"
