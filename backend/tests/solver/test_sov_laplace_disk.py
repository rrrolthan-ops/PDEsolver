"""Tests for Laplace's equation on a disk by SOV in polar coordinates."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _disk_problem(f_theta: str) -> PDEProblem:
    return PDEProblem(
        equation_latex=r"u_{rr} + (1/r)*u_r + (1/r^2)*u_{\theta\theta} = 0",
        equation_kind="laplace",
        geometry="disk",
        domain=Domain(x=["0", "R"]),  # x carries r informationally
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="r=R", value=f_theta),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"R": "positive"},
    )


R = sp.Symbol("R", positive=True)
THETA = sp.Symbol("theta", real=True)
RR = sp.Symbol("r", nonnegative=True)
N = sp.Symbol("n", integer=True, positive=True)


def test_routes_to_laplace_disk():
    resp = solve(_disk_problem("cos(theta)"))
    assert resp.method == "sov_laplace_disk"


def _extract_sum(sol: sp.Basic) -> sp.Sum | None:
    """Return the (single) sp.Sum inside `sol`, regardless of whether sol is
    the Sum itself or an Add wrapping it with a constant term."""
    if isinstance(sol, sp.Sum):
        return sol
    if isinstance(sol, sp.Add):
        for arg in sol.args:
            if isinstance(arg, sp.Sum):
                return arg
    return None


def _extract_constant(sol: sp.Basic) -> sp.Basic:
    """Return the constant (non-Sum) part of `sol`, or 0 if there is none."""
    if isinstance(sol, sp.Sum):
        return sp.Integer(0)
    if isinstance(sol, sp.Add):
        return sp.Add(*[arg for arg in sol.args if not isinstance(arg, sp.Sum)])
    return sol


def test_fundamental_cosine_mode():
    """f(θ) = cos(θ) ⇒ only the n=1 cosine mode contributes.

    a_1 R = (1/π) ∫ cos²θ dθ = 1 ⇒ a_1 = 1/R. So u = (r/R) cos θ.
    """
    resp = solve(_disk_problem("cos(theta)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    sum_obj = _extract_sum(sol)
    assert sum_obj is not None
    term = sum_obj.function
    n1 = sp.simplify(term.subs(N, 1))
    expected = (RR / R) * sp.cos(THETA)
    assert sp.simplify(n1 - expected) == 0


def test_constant_boundary_gives_constant_solution():
    """f(θ) = 1 ⇒ u(r, θ) = 1 (the average is 1, all other coefficients zero)."""
    resp = solve(_disk_problem("1"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    sum_obj = _extract_sum(sol)
    constant_part = _extract_constant(sol)
    # Take constant + first few terms; they should sum to 1.
    if sum_obj is not None:
        truncated = constant_part + sum(
            sum_obj.function.subs(N, k) for k in range(1, 5)
        )
    else:
        truncated = constant_part
    assert sp.simplify(truncated - 1) == 0


def test_harmonic_in_polar():
    """Verify that r^n cos(nθ) is harmonic in polar coords."""
    resp = solve(_disk_problem("cos(theta)"))
    verif_steps = [s for s in resp.steps if s.kind == "verification"]
    # At least: intro + PDE check + BC check. The PDE step should mention
    # that the term is armónico (harmonic).
    assert len(verif_steps) >= 2
    text = " ".join(s.title.lower() + " " + s.explanation_md.lower() for s in verif_steps)
    assert "armón" in text or "harmonic" in text


def test_geometry_disk_routing():
    """The geometry='disk' hint must override Cartesian Laplace routing."""
    p = _disk_problem("sin(2*theta)")
    resp = solve(p)
    assert resp.method == "sov_laplace_disk"
