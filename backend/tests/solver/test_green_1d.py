"""Tests for 1D Poisson via Green's function."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _poisson_problem(f_x: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="-u_{xx} = f(x)",
        equation_kind="poisson",
        source_term=f_x,
        domain=Domain(x=["0", "L"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=L", value="0"),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"L": "positive"},
    )


X = sp.Symbol("x", real=True)
L_S = sp.Symbol("L", positive=True)


def test_routes_to_green_1d():
    resp = solve(_poisson_problem("x*(L-x)"))
    assert resp.method == "greens_function_1d"


def test_constant_source():
    """f = 1 ⇒ u = x(L − x)/2."""
    resp = solve(_poisson_problem("1"))
    final = next(s for s in resp.steps if s.kind == "final")
    u = sp.sympify(final.sympy_repr)
    expected = X * (L_S - X) / 2
    assert sp.simplify(u - expected) == 0


def test_linear_source():
    """f = x ⇒ u = x(L²−x²)/6.

    Solve: -u'' = x, u(0)=u(L)=0.
    u'' = -x, u' = -x²/2 + C, u = -x³/6 + Cx + D.
    u(0) = 0 ⇒ D = 0. u(L) = 0 ⇒ -L³/6 + CL = 0 ⇒ C = L²/6.
    u = -x³/6 + xL²/6 = x(L² − x²)/6. ✓
    """
    resp = solve(_poisson_problem("x"))
    final = next(s for s in resp.steps if s.kind == "final")
    u = sp.sympify(final.sympy_repr)
    expected = X * (L_S**2 - X**2) / 6
    assert sp.simplify(u - expected) == 0


def test_quadratic_source():
    """f = x(L − x) ⇒ classic textbook example.

    By direct integration: u''(x) = -x(L-x) = x² - xL.
    u'(x) = x³/3 - x²L/2 + A
    u(x) = x⁴/12 - x³L/6 + Ax + B
    u(0) = 0 ⇒ B = 0.
    u(L) = L⁴/12 - L⁴/6 + AL = -L⁴/12 + AL = 0 ⇒ A = L³/12.
    u(x) = x⁴/12 - x³L/6 + xL³/12 = x(x³ - 2x²L + L³)/12.
    """
    resp = solve(_poisson_problem("x*(L - x)"))
    final = next(s for s in resp.steps if s.kind == "final")
    u = sp.sympify(final.sympy_repr)
    expected = X * (X**3 - 2 * X**2 * L_S + L_S**3) / 12
    assert sp.simplify(u - expected) == 0


def test_solution_satisfies_ode():
    """Verify -u'' = f symbolically for a non-trivial f."""
    resp = solve(_poisson_problem("sin(pi*x/L)"))
    final = next(s for s in resp.steps if s.kind == "final")
    u = sp.sympify(final.sympy_repr)
    residual = sp.simplify(-sp.diff(u, X, 2) - sp.sin(sp.pi * X / L_S))
    assert residual == 0


def test_boundary_conditions():
    resp = solve(_poisson_problem("x*(L-x)"))
    final = next(s for s in resp.steps if s.kind == "final")
    u = sp.sympify(final.sympy_repr)
    assert sp.simplify(u.subs(X, 0)) == 0
    assert sp.simplify(u.subs(X, L_S)) == 0


def test_response_has_green_construction():
    resp = solve(_poisson_problem("x*(L-x)"))
    dev_steps = [s for s in resp.steps if s.kind == "development"]
    text = " ".join(s.title.lower() for s in dev_steps)
    assert "construcción" in text or "construccion" in text or "función" in text
