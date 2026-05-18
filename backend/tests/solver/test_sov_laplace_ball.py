"""Tests for axisymmetric Laplace in a 3D ball (Legendre expansion)."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _ball_problem(f_theta: str) -> PDEProblem:
    return PDEProblem(
        equation_latex=r"\nabla^2 u = 0",
        equation_kind="laplace",
        geometry="sphere",
        domain=Domain(x=["0", "R"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="r=R", value=f_theta),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"R": "positive"},
    )


X = sp.Symbol("r", nonnegative=True)
THETA = sp.Symbol("theta", real=True)
R = sp.Symbol("R", positive=True)
ELL = sp.Symbol("ell", integer=True, nonnegative=True)


def test_routes_to_laplace_ball():
    resp = solve(_ball_problem("cos(theta)"))
    assert resp.method == "sov_laplace_ball"


def test_response_mentions_legendre():
    resp = solve(_ball_problem("cos(theta)"))
    titles = " ".join(s.title.lower() for s in resp.steps)
    assert "legendre" in titles


def _evaluate_term_at(term: sp.Basic, ell_value: int) -> sp.Basic:
    """Substitute ell -> integer and `.doit()` any pending Integrals."""
    # Match the ell symbol by name (sympify may not preserve assumptions).
    ell_sym = next(s for s in term.free_symbols if s.name == "ell")
    return sp.simplify(term.subs(ell_sym, ell_value).doit())


def test_constant_boundary_gives_constant_interior():
    """f = 1 ⇒ u = 1 (the n=0 monopole is the average).

    A_0 = (1/2) ∫_{-1}^{1} 1 · P_0(xi) dxi = (1/2)(2) = 1.
    A_ℓ for ℓ ≥ 1: zero by orthogonality.
    So u = r^0 · P_0(cos theta) · 1 = 1.
    """
    resp = solve(_ball_problem("1"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function if isinstance(sol, sp.Sum) else sol
    partial = sum(_evaluate_term_at(term, k) for k in range(0, 4))
    assert sp.simplify(partial - 1) == 0


def test_cos_theta_boundary():
    """f = cos(theta) = xi ⇒ only ℓ = 1 contributes.

    P_1(xi) = xi, so ∫_{-1}^{1} xi · P_1 dxi = ∫ xi² dxi = 2/3.
    A_1 = (3/(2R)) · (2/3) = 1/R.
    u = A_1 r P_1(cos theta) = (r/R) cos theta.
    """
    resp = solve(_ball_problem("cos(theta)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function if isinstance(sol, sp.Sum) else sol
    ell1 = _evaluate_term_at(term, 1)
    expected = (X / R) * sp.cos(THETA)
    assert sp.simplify(ell1 - expected) == 0
    ell0 = _evaluate_term_at(term, 0)
    assert ell0 == 0


def test_multipole_observation():
    resp = solve(_ball_problem("cos(theta)"))
    obs_md = " ".join(o.text_md for s in resp.steps for o in s.observations).lower()
    assert "multipolo" in obs_md or "multipole" in obs_md


def test_mean_value_theorem_observation():
    resp = solve(_ball_problem("1"))
    obs_md = " ".join(o.text_md for s in resp.steps for o in s.observations).lower()
    assert "valor medio" in obs_md or "mean value" in obs_md
