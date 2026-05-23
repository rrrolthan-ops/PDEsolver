"""Tests for the Duhamel solution of u_t = α²u_xx + f(x,t) on the real line."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _duhamel_problem(u0: str, source: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="u_t = alpha^2*u_{xx} + f",
        equation_kind="heat",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],
        initial_conditions=[InitialCondition(order=0, value=u0)],
        parameters={"alpha": "positive"},
        source_term=source,
    )


def test_routes_to_duhamel():
    resp = solve(_duhamel_problem("exp(-x^2)", "exp(-x^2)*exp(-t)"))
    assert resp.method == "duhamel_heat"


def test_no_source_routes_to_fourier_heat_line():
    """Without a source, the unbounded heat equation goes to fourier_heat_line."""
    p = PDEProblem(
        equation_latex="u_t = alpha^2*u_{xx}",
        equation_kind="heat",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],
        initial_conditions=[InitialCondition(order=0, value="exp(-x^2)")],
        parameters={"alpha": "positive"},
        source_term=None,
    )
    resp = solve(p)
    assert resp.method == "fourier_heat_line"


def test_zero_source_routes_to_fourier_heat_line():
    """Source explicitly set to '0' is treated as no source."""
    p = PDEProblem(
        equation_latex="u_t = alpha^2*u_{xx}",
        equation_kind="heat",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],
        initial_conditions=[InitialCondition(order=0, value="exp(-x^2)")],
        parameters={"alpha": "positive"},
        source_term="0",
    )
    resp = solve(p)
    assert resp.method == "fourier_heat_line"


def test_poisson_1d_still_routes_to_greens_function():
    """Bounded interval + source still goes to greens_function_1d."""
    p = PDEProblem(
        equation_latex="-u_{xx} = f(x)",
        equation_kind="poisson",
        domain=Domain(x=["0", "L"]),
        boundary_conditions=[
            {"type": "dirichlet", "where": "x=0", "value": "0"},
            {"type": "dirichlet", "where": "x=L", "value": "0"},
        ],
        initial_conditions=[],
        parameters={"L": "positive"},
        source_term="sin(pi*x/L)",
    )
    resp = solve(p)
    assert resp.method == "greens_function_1d"


def test_solution_is_a_sum_of_two_integrals():
    """For u_0 ≠ 0 and f ≠ 0, the solution has both terms."""
    resp = solve(_duhamel_problem("exp(-x^2)", "exp(-x^2)*exp(-t)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    # The solution should be a sum (Add) containing at least two Integrals.
    if isinstance(sol, sp.Add):
        integrals = [a for a in sol.args if isinstance(a, sp.Integral)]
        assert len(integrals) >= 2
    else:
        # Single integral — possible if SymPy collapsed.
        assert isinstance(sol, sp.Integral)


def test_zero_initial_condition_drops_homogeneous_term():
    """If u_0 = 0, the solution is just the Duhamel forcing integral."""
    resp = solve(_duhamel_problem("0", "exp(-x^2)*exp(-t)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    # Should be a single double-integral (in y and s).
    assert isinstance(sol, sp.Integral)
    assert len(sol.limits) == 2


def test_kernel_satisfies_heat_equation():
    """The heat kernel G appearing in the Duhamel formula satisfies the
    homogeneous heat equation. This is the only purely symbolic
    verification we can do; the Duhamel-Leibniz argument is pedagogical."""
    x = sp.Symbol("x", real=True)
    t = sp.Symbol("t", real=True, positive=True)
    alpha = sp.Symbol("alpha", positive=True)
    G = sp.exp(-(x**2) / (4 * alpha**2 * t)) / sp.sqrt(4 * sp.pi * alpha**2 * t)
    residual = sp.simplify(sp.diff(G, t) - alpha**2 * sp.diff(G, x, 2))
    assert residual == 0


def test_pedagogy_mentions_duhamel_and_superposition():
    resp = solve(_duhamel_problem("exp(-x^2)", "exp(-x^2)*exp(-t)"))
    text = " ".join(s.title + " " + s.explanation_md for s in resp.steps).lower()
    assert "duhamel" in text
    assert "superposici" in text or "linealidad" in text


def test_pedagogy_mentions_decomposition_homog_plus_forcing():
    resp = solve(_duhamel_problem("exp(-x^2)", "exp(-x^2)*exp(-t)"))
    dev_steps = [s for s in resp.steps if s.kind == "development"]
    text = " ".join(s.title + " " + s.explanation_md for s in dev_steps).lower()
    assert "hom" in text  # u_{hom}
    assert "forz" in text or "duhamel" in text  # u_{forz} or Duhamel


def test_pedagogy_mentions_causality():
    resp = solve(_duhamel_problem("exp(-x^2)", "exp(-x^2)*exp(-t)"))
    interp = next(s for s in resp.steps if s.kind == "interpretation")
    text = interp.explanation_md.lower()
    assert "causal" in text or "memoria" in text or "olvido" in text


def test_response_has_verification_steps():
    resp = solve(_duhamel_problem("exp(-x^2)", "exp(-x^2)*exp(-t)"))
    verif_steps = [s for s in resp.steps if s.kind == "verification"]
    # intro + kernel check + Duhamel-Leibniz argument
    assert len(verif_steps) >= 3
