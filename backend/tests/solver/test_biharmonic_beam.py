"""Tests for the simply-supported Euler-Bernoulli beam."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _beam_problem(q: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="EI*u'''' = q(x)",
        equation_kind="biharmonic",
        source_term=q,
        domain=Domain(x=["0", "L"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=L", value="0"),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"L": "positive", "EI": "positive"},
    )


X = sp.Symbol("x", real=True)
L_S = sp.Symbol("L", positive=True)
EI = sp.Symbol("EI", positive=True)
N = sp.Symbol("n", integer=True, positive=True)


def test_routes_to_beam():
    resp = solve(_beam_problem("sin(pi*x/L)"))
    assert resp.method == "biharmonic_beam"


def test_fundamental_mode_load():
    """q = sin(πx/L) ⇒ A_1 = L^4 / (EI π^4), others zero."""
    resp = solve(_beam_problem("sin(pi*x/L)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function
    a1_sin = sp.simplify(term.subs(N, 1))
    expected = (L_S**4 / (EI * sp.pi**4)) * sp.sin(sp.pi * X / L_S)
    assert sp.simplify(a1_sin - expected) == 0
    # n=2 should be zero (orthogonality).
    assert sp.simplify(term.subs(N, 2)) == 0


def test_solution_satisfies_pde():
    """For q = sin(πx/L), the partial sum at n=1 satisfies EI u'''' = q."""
    resp = solve(_beam_problem("sin(pi*x/L)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function
    u1 = sp.simplify(term.subs(N, 1))
    residual = sp.simplify(EI * sp.diff(u1, X, 4) - sp.sin(sp.pi * X / L_S))
    assert residual == 0


def test_simply_supported_bcs():
    """u(0) = u(L) = 0 and u''(0) = u''(L) = 0 hold term-by-term."""
    resp = solve(_beam_problem("sin(pi*x/L)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function
    assert sp.simplify(term.subs(X, 0)) == 0
    assert sp.simplify(term.subs(X, L_S)) == 0
    assert sp.simplify(sp.diff(term, X, 2).subs(X, 0)) == 0
    assert sp.simplify(sp.diff(term, X, 2).subs(X, L_S)) == 0


def test_response_has_four_bcs_observation():
    resp = solve(_beam_problem("sin(pi*x/L)"))
    obs_kinds = [o.kind for s in resp.steps for o in s.observations]
    # At least one pitfall and one intuition box.
    assert "pitfall" in obs_kinds
    assert "intuition" in obs_kinds
