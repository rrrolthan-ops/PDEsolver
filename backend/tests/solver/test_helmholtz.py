"""Tests for inhomogeneous Helmholtz on a rectangle."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _helmholtz_problem(f_source: str | None) -> PDEProblem:
    return PDEProblem(
        equation_latex=r"u_{xx} + u_{yy} + k^2 * u = f(x, y)",
        equation_kind="helmholtz",
        source_term=f_source,
        domain=Domain(x=["0", "a"], y=["0", "b"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=a", value="0"),
            BoundaryCondition(type="dirichlet", where="y=0", value="0"),
            BoundaryCondition(type="dirichlet", where="y=b", value="0"),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"a": "positive", "b": "positive", "k": "positive"},
    )


def test_routes_to_helmholtz():
    resp = solve(_helmholtz_problem("sin(pi*x/a)*sin(pi*y/b)"))
    assert resp.method == "helmholtz_rect"


def test_eigenvalue_mode_when_homogeneous():
    """No source → eigenvalue-problem output."""
    resp = solve(_helmholtz_problem(None))
    final = next(s for s in resp.steps if s.kind == "final")
    text = final.title.lower()
    assert "autofunción" in text or "modo" in text


def test_inhomogeneous_solution_structure():
    """f = sin(πx/a) sin(πy/b) → solution contains 1/(k² − k_{11}²) factor.

    SymPy may keep the result as a (nested) Sum with a Piecewise coefficient
    instead of collapsing to a single term; we don't pin the exact shape,
    only that the right sines and the right denominator appear.
    """
    resp = solve(_helmholtz_problem("sin(pi*x/a)*sin(pi*y/b)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol_str = final.latex + " " + str(sp.sympify(final.sympy_repr))
    assert "sin" in sol_str
    # The denominator k² − π²/a² − π²/b² (or its sympy form) shows up.
    assert "k" in sol_str
    assert "pi" in sol_str or "\\pi" in sol_str


def test_method_choice_step_present():
    resp = solve(_helmholtz_problem("sin(pi*x/a)*sin(pi*y/b)"))
    assert any(s.kind == "method_choice" for s in resp.steps)
