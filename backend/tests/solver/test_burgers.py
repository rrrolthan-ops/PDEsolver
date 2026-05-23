"""Tests for the inviscid Burgers equation by characteristics."""

from __future__ import annotations

from app.schemas import (
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _burgers_problem(u0: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="u_t + u*u_x = 0",
        equation_kind="general",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],
        initial_conditions=[InitialCondition(order=0, value=u0)],
        parameters={},
    )


def test_routes_to_burgers():
    resp = solve(_burgers_problem("-tanh(x)"))
    assert resp.method == "burgers_inviscid"


def test_linear_transport_still_routes_to_characteristics():
    """u_t + c·u_x = 0 must NOT be picked up by Burgers (which looks
    for the literal `u*u_x` shape)."""
    p = PDEProblem(
        equation_latex="u_t + c*u_x = 0",
        equation_kind="general",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],
        initial_conditions=[InitialCondition(order=0, value="exp(-x^2)")],
        parameters={"c": "positive"},
    )
    resp = solve(p)
    assert resp.method == "characteristics_transport_1d"


def test_breaking_time_for_minus_tanh():
    """For u_0(x) = -tanh(x), u_0'(0) = -1 is the global minimum, so
    t_b = -1/(-1) = 1.
    """
    resp = solve(_burgers_problem("-tanh(x)"))
    breaking_step = next(
        s for s in resp.steps if "tiempo de ruptura" in s.title.lower()
    )
    # The boxed result should end in `= 1.` (the breaking time is 1).
    stripped = breaking_step.latex.replace(" ", "")
    assert "=1.\\;}" in stripped, f"breaking-time LaTeX did not end at 1: {stripped}"


def test_non_decreasing_data_no_shock():
    """For u_0(x) = tanh(x), u_0'(x) ≥ 0 everywhere, so no shock forms.

    The pedagogy should not introduce the Rankine-Hugoniot step.
    """
    resp = solve(_burgers_problem("tanh(x)"))
    has_rankine = any("Rankine" in s.title for s in resp.steps)
    assert not has_rankine
    breaking_step = next(
        s for s in resp.steps if "tiempo de ruptura" in s.title.lower()
    )
    assert "\\infty" in breaking_step.latex or "infty" in breaking_step.latex


def test_decreasing_data_has_rankine_hugoniot_step():
    resp = solve(_burgers_problem("-tanh(x)"))
    has_rankine = any("Rankine" in s.title for s in resp.steps)
    assert has_rankine


def test_implicit_formula_present():
    """The final step should display u = u_0(x - u t)."""
    resp = solve(_burgers_problem("-tanh(x)"))
    final = next(s for s in resp.steps if s.kind == "final")
    # The formula should mention `u` and `t·u` (or `tu`) — any
    # rendering that combines t and u multiplicatively. SymPy renders
    # u*t as "tu" by default (alphabetical).
    txt = final.latex.replace(" ", "")
    assert "u" in txt
    assert any(s in txt for s in ("tu", "ut", "u*t", "t*u", "u\\,t", "t\\,u"))


def test_pedagogy_mentions_shock_and_characteristics():
    resp = solve(_burgers_problem("-tanh(x)"))
    text = " ".join(s.title + " " + s.explanation_md for s in resp.steps).lower()
    assert "característ" in text
    assert "choque" in text or "shock" in text
    assert "ruptura" in text or "rompe" in text


def test_pedagogy_mentions_rankine_hugoniot():
    resp = solve(_burgers_problem("-tanh(x)"))
    text = " ".join(s.title + " " + s.explanation_md for s in resp.steps).lower()
    assert "rankine" in text


def test_pedagogy_contrasts_with_linear_transport():
    """The marquee teaching point: Burgers is non-linear → shocks.
    Linear transport is the contrast (no shocks, characteristics
    parallel)."""
    resp = solve(_burgers_problem("-tanh(x)"))
    text = " ".join(s.title + " " + s.explanation_md for s in resp.steps).lower()
    assert "transporte lineal" in text or "lineal" in text


def test_verification_step_uses_chain_rule():
    """The verification is a chain-rule argument; it should mention
    du/dt and u_t + u·u_x explicitly."""
    resp = solve(_burgers_problem("-tanh(x)"))
    verif = next(s for s in resp.steps if s.kind == "verification")
    assert "u_t" in verif.latex
    assert "u_x" in verif.latex


def test_plot_is_surface_xt():
    resp = solve(_burgers_problem("-tanh(x)"))
    plot = resp.plot_data
    assert plot is not None
    assert plot.get("kind") == "surface_xt"
    for row in plot["u"]:
        for v in row:
            assert v == v  # not NaN
            assert abs(v) < 10.0, f"out-of-range u: {v}"


def test_plot_initial_profile_matches():
    """At t = 0 the surface should reproduce u_0(x) (modulo grid
    sampling error)."""
    import sympy as _sp

    resp = solve(_burgers_problem("-tanh(x)"))
    plot = resp.plot_data
    xs = plot["x"]
    u_at_t0 = plot["u"][0]  # first time slice
    # u_0(x) = -tanh(x). Check correlation at a few sample points.
    for x_val, u_val in zip(xs[::10], u_at_t0[::10]):
        expected = float(-_sp.tanh(_sp.Float(x_val)))
        assert abs(u_val - expected) < 1e-4, (
            f"at x = {x_val}: got {u_val}, expected {expected}"
        )


def test_classification_says_quasi_linear_hyperbolic():
    resp = solve(_burgers_problem("-tanh(x)"))
    classif = next(s for s in resp.steps if s.kind == "classification")
    assert "cuasi-lineal" in classif.explanation_md.lower() or "cuasi-lineal" in classif.title.lower()
    assert "hiperb" in classif.title.lower() or "hiperb" in classif.explanation_md.lower()
