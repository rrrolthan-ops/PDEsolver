"""Tests for D'Alembert's formula on the infinite line."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _dalembert_problem(f: str, g: str = "0") -> PDEProblem:
    return PDEProblem(
        equation_latex="u_{tt} = c^2 * u_{xx}",
        equation_kind="wave",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],  # unbounded line, no BCs
        initial_conditions=[
            InitialCondition(order=0, value=f),
            InitialCondition(order=1, value=g),
        ],
        parameters={"c": "positive"},
    )


X = sp.Symbol("x", real=True)
T = sp.Symbol("t", real=True, nonnegative=True)
C = sp.Symbol("c", positive=True)


def test_routes_to_dalembert():
    resp = solve(_dalembert_problem("exp(-x^2)"))
    assert resp.method == "dalembert_wave_1d"


def test_gaussian_pulse_no_velocity():
    """f = exp(-x²), g = 0 ⇒ u = (f(x-ct) + f(x+ct))/2 — two travelling Gaussians."""
    resp = solve(_dalembert_problem("exp(-x^2)", "0"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    expected = (sp.exp(-(X - C * T) ** 2) + sp.exp(-(X + C * T) ** 2)) / 2
    assert sp.simplify(sol - expected) == 0


def test_zero_position_constant_velocity():
    """f = 0, g = 1 ⇒ u = t (the constant kick lifts the whole line uniformly).

    By d'Alembert: u = (1/(2c)) ∫_{x-ct}^{x+ct} 1 ds = (1/(2c)) · 2ct = t.
    """
    resp = solve(_dalembert_problem("0", "1"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    assert sp.simplify(sol - T) == 0


def test_linear_initial_profile():
    """f = x, g = 0 ⇒ u = (x-ct + x+ct)/2 = x. The straight line doesn't evolve."""
    resp = solve(_dalembert_problem("x", "0"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    assert sp.simplify(sol - X) == 0


def test_satisfies_pde_symbolically():
    """For a smooth f, verify u_tt = c^2 u_xx holds."""
    resp = solve(_dalembert_problem("sin(x)", "0"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    residual = sp.simplify(sp.diff(sol, T, 2) - C**2 * sp.diff(sol, X, 2))
    assert residual == 0


def test_ics_satisfied():
    """u(x, 0) = f and u_t(x, 0) = g."""
    resp = solve(_dalembert_problem("sin(x)", "cos(x)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    assert sp.simplify(sol.subs(T, 0) - sp.sin(X)) == 0
    assert sp.simplify(sp.diff(sol, T).subs(T, 0) - sp.cos(X)) == 0


def test_method_choice_step_mentions_characteristics():
    resp = solve(_dalembert_problem("exp(-x^2)"))
    choice_steps = [s for s in resp.steps if s.kind == "method_choice"]
    text = " ".join(s.explanation_md for s in choice_steps).lower()
    assert "característ" in text or "factor" in text
