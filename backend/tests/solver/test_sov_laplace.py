"""Tests for the Laplace-rectangle separation-of-variables method."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _laplace_problem(f_top: str) -> PDEProblem:
    """Laplace in [0, a] × [0, b] with u=0 on three sides, u(x, b) = f_top."""
    return PDEProblem(
        equation_latex="u_{xx} + u_{yy} = 0",
        equation_kind="laplace",
        domain=Domain(x=["0", "a"], y=["0", "b"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=a", value="0"),
            BoundaryCondition(type="dirichlet", where="y=0", value="0"),
            BoundaryCondition(type="dirichlet", where="y=b", value=f_top),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"a": "positive", "b": "positive"},
    )


X = sp.Symbol("x", real=True)
Y = sp.Symbol("y", real=True)
A = sp.Symbol("a", positive=True)
B = sp.Symbol("b", positive=True)
N = sp.Symbol("n", integer=True, positive=True)


def test_routes_to_laplace_rect():
    resp = solve(_laplace_problem("sin(pi*x/a)"))
    assert resp.method == "sov_laplace_rect"


def test_fundamental_mode_top_boundary():
    """f(x) = sin(πx/a) ⇒ only n=1 contributes.

    A_1 sinh(πb/a) sin(πx/a) = sin(πx/a) at y=b ⇒ A_1 = 1/sinh(πb/a).
    """
    resp = solve(_laplace_problem("sin(pi*x/a)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function
    n1 = sp.simplify(term.subs(N, 1))
    expected = (
        (1 / sp.sinh(sp.pi * B / A))
        * sp.sin(sp.pi * X / A)
        * sp.sinh(sp.pi * Y / A)
    )
    assert sp.simplify(n1 - expected) == 0
    # n = 2 should be zero (orthogonality).
    n2 = sp.simplify(term.subs(N, 2))
    assert n2 == 0


def test_top_boundary_recovered():
    """At y = b the series should reproduce f(x). Check n=1 term at y=b equals sin(πx/a)."""
    resp = solve(_laplace_problem("sin(pi*x/a)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function
    n1_at_top = sp.simplify(term.subs(N, 1).subs(Y, B))
    expected = sp.sin(sp.pi * X / A)
    assert sp.simplify(n1_at_top - expected) == 0


def test_three_sides_homogeneous():
    """u(0, y), u(a, y), u(x, 0) all zero — by construction term-by-term."""
    resp = solve(_laplace_problem("sin(pi*x/a)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function
    assert sp.simplify(term.subs(X, 0)) == 0
    assert sp.simplify(term.subs(X, A)) == 0
    assert sp.simplify(term.subs(Y, 0)) == 0


def test_laplacian_zero():
    resp = solve(_laplace_problem("sin(pi*x/a)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function
    laplacian = sp.simplify(sp.diff(term, X, 2) + sp.diff(term, Y, 2))
    assert laplacian == 0


def test_classification_elliptic():
    resp = solve(_laplace_problem("sin(pi*x/a)"))
    class_steps = [s for s in resp.steps if s.kind == "classification"]
    text = " ".join(s.title + s.explanation_md for s in class_steps).lower()
    assert "elíptica" in text or "elliptic" in text
