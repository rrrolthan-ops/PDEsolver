"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)


def heat_problem(initial_value: str) -> PDEProblem:
    """Build the canonical heat-1D problem with a given initial profile.

    All tests in this suite share this shape:
        u_t = α² u_xx,   0 < x < L,   t > 0,
        u(0, t) = u(L, t) = 0,
        u(x, 0) = `initial_value`.
    """
    return PDEProblem(
        equation_latex="u_t = alpha^2 * u_{xx}",
        equation_kind="heat",
        domain=Domain(x=["0", "L"], t=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=L", value="0"),
        ],
        initial_conditions=[InitialCondition(order=0, value=initial_value)],
        parameters={"alpha": "positive", "L": "positive"},
    )


@pytest.fixture
def problem_sin1() -> PDEProblem:
    """f(x) = sin(πx/L) — the fundamental mode."""
    return heat_problem("sin(pi*x/L)")


@pytest.fixture
def problem_sin2() -> PDEProblem:
    """f(x) = sin(2πx/L) — the second mode."""
    return heat_problem("sin(2*pi*x/L)")


@pytest.fixture
def problem_parabolic() -> PDEProblem:
    """f(x) = x(L - x) — the classic textbook example (Haberman §2.4)."""
    return heat_problem("x*(L - x)")


@pytest.fixture
def problem_linear() -> PDEProblem:
    """f(x) = x — discontinuous extension to a Fourier sine series at x = L."""
    return heat_problem("x")


@pytest.fixture
def problem_constant() -> PDEProblem:
    """f(x) = 1 — uniform initial temperature, classic Gibbs setup."""
    return heat_problem("1")


@pytest.fixture
def problem_mixed_modes() -> PDEProblem:
    """f(x) = 3 sin(πx/L) − sin(3πx/L) — superposition of two modes."""
    return heat_problem("3*sin(pi*x/L) - sin(3*pi*x/L)")
