"""Tests for the telegraph equation."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _telegraph_problem(f: str, g: str = "0") -> PDEProblem:
    return PDEProblem(
        equation_latex="u_{tt} + 2*alpha*u_t + beta*u = c^2 * u_{xx}",
        equation_kind="telegraph",
        domain=Domain(x=["0", "L"], t=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=L", value="0"),
        ],
        initial_conditions=[
            InitialCondition(order=0, value=f),
            InitialCondition(order=1, value=g),
        ],
        parameters={
            "alpha": "positive",
            "beta": "nonnegative",
            "c": "positive",
            "L": "positive",
        },
    )


def test_routes_to_telegraph():
    resp = solve(_telegraph_problem("sin(pi*x/L)"))
    assert resp.method == "telegraph_sov"


def test_three_regimes_step_present():
    resp = solve(_telegraph_problem("sin(pi*x/L)"))
    titles = " ".join(s.title.lower() for s in resp.steps)
    assert "regímenes" in titles or "regimenes" in titles or "amortiguado" in titles


def test_solution_is_a_series():
    resp = solve(_telegraph_problem("sin(pi*x/L)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    assert isinstance(sol, sp.Sum)


def test_classification_step():
    resp = solve(_telegraph_problem("sin(pi*x/L)"))
    cls_steps = [s for s in resp.steps if s.kind == "classification"]
    assert any("hiperbólica" in s.explanation_md.lower() or "hiperbolica" in s.explanation_md.lower() for s in cls_steps)


def test_three_ic_steps_present():
    resp = solve(_telegraph_problem("sin(pi*x/L)", "0"))
    initial_steps = [s for s in resp.steps if s.kind == "initial"]
    text = " ".join(s.title for s in initial_steps)
    assert "A_n" in text and "B_n" in text
