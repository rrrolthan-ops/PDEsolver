"""Tests for the Schrödinger equation in an infinite 1D well."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _well_problem(psi0: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="i*hbar*u_t = -hbar^2/(2*m) * u_{xx}",
        equation_kind="schrodinger",
        domain=Domain(x=["0", "L"], t=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=L", value="0"),
        ],
        initial_conditions=[InitialCondition(order=0, value=psi0)],
        parameters={"L": "positive", "hbar": "positive", "m": "positive"},
    )


X = sp.Symbol("x", real=True)
T = sp.Symbol("t", real=True, nonnegative=True)
L_S = sp.Symbol("L", positive=True)
HBAR = sp.Symbol("hbar", positive=True)
M = sp.Symbol("m", positive=True)
N = sp.Symbol("n", integer=True, positive=True)


def test_routes_to_schrodinger():
    resp = solve(_well_problem("sqrt(2/L)*sin(pi*x/L)"))
    assert resp.method == "schrodinger_well"


def test_ground_state_stationary():
    """psi_0 = phi_1 ⇒ psi(x, t) = phi_1 e^{-i E_1 t/hbar}."""
    resp = solve(_well_problem("sqrt(2/L)*sin(pi*x/L)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function if isinstance(sol, sp.Sum) else sol
    # Check that the n=1 term is phi_1(x) * exp(-i E_1 t / hbar).
    n1 = sp.simplify(term.subs(N, 1))
    E_1 = sp.pi**2 * HBAR**2 / (2 * M * L_S**2)
    expected = sp.sqrt(2 / L_S) * sp.sin(sp.pi * X / L_S) * sp.exp(-sp.I * E_1 * T / HBAR)
    assert sp.simplify(n1 - expected) == 0
    # n=2 must be zero (orthogonal to psi_0).
    n2 = sp.simplify(term.subs(N, 2))
    assert n2 == 0


def test_response_mentions_quantization():
    resp = solve(_well_problem("sqrt(2/L)*sin(pi*x/L)"))
    # The eigenvalues step should mention E_n or cuantizad...
    titles_and_md = " ".join(s.title + " " + s.explanation_md for s in resp.steps).lower()
    assert "cuantiz" in titles_and_md or "quantiz" in titles_and_md


def test_classification_step_present():
    resp = solve(_well_problem("sqrt(2/L)*sin(pi*x/L)"))
    assert any(s.kind == "classification" for s in resp.steps)


def test_second_eigenstate_at_t_zero():
    """psi_0 = phi_2 ⇒ c_2 = 1 by orthonormality."""
    resp = solve(_well_problem("sqrt(2/L)*sin(2*pi*x/L)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function
    n2 = sp.simplify(term.subs(N, 2).subs(T, 0))
    expected = sp.sqrt(2 / L_S) * sp.sin(2 * sp.pi * X / L_S)
    assert sp.simplify(n2 - expected) == 0
