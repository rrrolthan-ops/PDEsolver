"""Tests for the wave-1D separation-of-variables method.

References
----------
- Haberman, "Applied Partial Differential Equations", §4.4 (vibrating string).
- Strauss, "Partial Differential Equations: An Introduction", ch. 4.
"""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _wave_problem(f: str, g: str = "0") -> PDEProblem:
    return PDEProblem(
        equation_latex="u_{tt} = c^2 * u_{xx}",
        equation_kind="wave",
        domain=Domain(x=["0", "L"], t=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=L", value="0"),
        ],
        initial_conditions=[
            InitialCondition(order=0, value=f),
            InitialCondition(order=1, value=g),
        ],
        parameters={"c": "positive", "L": "positive"},
    )


X = sp.Symbol("x", real=True)
T = sp.Symbol("t", real=True, nonnegative=True)
L_S = sp.Symbol("L", positive=True)
C_S = sp.Symbol("c", positive=True)
N = sp.Symbol("n", integer=True, positive=True)


def _term_for(k: int, A_k, B_k):
    omega_k = C_S * k * sp.pi / L_S
    return (A_k * sp.cos(omega_k * T) + B_k * sp.sin(omega_k * T)) * sp.sin(
        k * sp.pi * X / L_S
    )


def test_pure_position_fundamental_mode():
    """f = sin(πx/L), g = 0 ⇒ A_1 = 1, B_n = 0, others A_n = 0.

    The string starts displaced as the fundamental mode and is released
    from rest: it should oscillate purely as that mode.
    """
    resp = solve(_wave_problem("sin(pi*x/L)", "0"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    assert isinstance(sol, sp.Sum)
    term = sol.function
    # n = 1: should equal cos(cπt/L) sin(πx/L).
    n1 = sp.simplify(term.subs(N, 1))
    expected = sp.cos(C_S * sp.pi * T / L_S) * sp.sin(sp.pi * X / L_S)
    assert sp.simplify(n1 - expected) == 0
    # n = 2: should be zero (B_n = 0 because g=0; A_n = 0 because f ⊥ sin(2πx/L)).
    n2 = sp.simplify(term.subs(N, 2))
    assert n2 == 0


def test_velocity_kick_only():
    """f = 0, g = sin(πx/L) ⇒ A_n = 0 for all n; B_1 = L/(cπ).

    The string starts at rest and receives an initial-velocity kick
    along the fundamental mode.
    """
    resp = solve(_wave_problem("0", "sin(pi*x/L)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    term = sol.function
    # n = 1: B_1 sin(omega_1 t) sin(πx/L), where B_1 = L/(cπ).
    n1 = sp.simplify(term.subs(N, 1))
    expected = (L_S / (C_S * sp.pi)) * sp.sin(C_S * sp.pi * T / L_S) * sp.sin(
        sp.pi * X / L_S
    )
    assert sp.simplify(n1 - expected) == 0


def test_response_has_two_initial_steps():
    """The wave method must emit TWO initial-condition steps (A_n and B_n)."""
    resp = solve(_wave_problem("sin(pi*x/L)", "sin(2*pi*x/L)"))
    initial_steps = [s for s in resp.steps if s.kind == "initial"]
    titles = " ".join(s.title for s in initial_steps)
    assert "A_n" in titles or "$A_n$" in titles
    assert "B_n" in titles or "$B_n$" in titles


def test_classification_is_hyperbolic():
    resp = solve(_wave_problem("sin(pi*x/L)"))
    class_steps = [s for s in resp.steps if s.kind == "classification"]
    text = " ".join(s.title + s.explanation_md for s in class_steps).lower()
    assert "hiperbólica" in text or "hyperbolic" in text


def test_wave_method_routed_correctly():
    resp = solve(_wave_problem("sin(pi*x/L)"))
    assert resp.method == "sov_wave_1d"
