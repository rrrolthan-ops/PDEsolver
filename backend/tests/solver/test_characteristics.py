"""Tests for the method of characteristics on the transport equation."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _transport_problem(u0: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="u_t + c*u_x = 0",
        equation_kind="general",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],
        initial_conditions=[InitialCondition(order=0, value=u0)],
        parameters={"c": "positive"},
    )


X = sp.Symbol("x", real=True)
T = sp.Symbol("t", real=True, nonnegative=True)
C = sp.Symbol("c", positive=True)


def test_routes_to_characteristics():
    resp = solve(_transport_problem("exp(-x^2)"))
    assert resp.method == "characteristics_transport_1d"


def test_gaussian_pulse_translates_rigidly():
    """u_0 = exp(-x^2) ⇒ u(x, t) = exp(-(x - ct)^2)."""
    resp = solve(_transport_problem("exp(-x^2)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    expected = sp.exp(-((X - C * T) ** 2))
    assert sp.simplify(sol - expected) == 0


def test_sine_initial_profile():
    resp = solve(_transport_problem("sin(x)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    expected = sp.sin(X - C * T)
    assert sp.simplify(sol - expected) == 0


def test_satisfies_pde():
    resp = solve(_transport_problem("sin(x)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    residual = sp.simplify(sp.diff(sol, T) + C * sp.diff(sol, X))
    assert residual == 0


def test_ic_satisfied():
    resp = solve(_transport_problem("x*exp(-x^2)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    at_t0 = sp.simplify(sol.subs(T, 0))
    expected = X * sp.exp(-(X**2))
    assert sp.simplify(at_t0 - expected) == 0


def test_method_text_mentions_characteristics():
    resp = solve(_transport_problem("sin(x)"))
    text = " ".join(s.title + " " + s.explanation_md for s in resp.steps).lower()
    assert "característ" in text or "caracter" in text or "characteristic" in text
