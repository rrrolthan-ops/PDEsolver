"""Tests for the generic 2nd-order PDE classifier (fallback method)."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _general_problem(equation_latex: str) -> PDEProblem:
    """A bare 2nd-order PDE on a generic domain, no BCs/ICs.

    The point is that the generic classifier should pick it up even
    when none of the specific predicates apply.
    """
    return PDEProblem(
        equation_latex=equation_latex,
        equation_kind="general",
        domain=Domain(x=["0", "1"], y=["0", "1"]),
        boundary_conditions=[],
        initial_conditions=[],
        parameters={},
    )


# ---------------------------------------------------------------------------
# Routing — fallback must fire only when no specific method applies
# ---------------------------------------------------------------------------


def test_pure_hyperbolic_routes_to_general():
    """u_xx - 4 u_xy + 3 u_yy = 0 on a generic (x, y) rectangle — no
    specific method applies (it's neither wave/heat/Laplace), so the
    fallback fires."""
    resp = solve(_general_problem("u_{xx} - 4*u_{xy} + 3*u_{yy} = 0"))
    assert resp.method == "general_second_order"


def test_pure_parabolic_routes_to_general():
    """u_xx + 4 u_xy + 4 u_yy = 0 — degenerate parabolic (Δ = 0)."""
    resp = solve(_general_problem("u_{xx} + 4*u_{xy} + 4*u_{yy} = 0"))
    assert resp.method == "general_second_order"


def test_pure_elliptic_with_parameter_routes_to_general():
    """u_xx + 2 u_xy + 2 u_yy = 0 — discriminant 4 − 8 = −4 < 0."""
    resp = solve(_general_problem("u_{xx} + 2*u_{xy} + 2*u_{yy} = 0"))
    assert resp.method == "general_second_order"


def test_specific_methods_still_win():
    """A bare wave equation on the line still routes to D'Alembert,
    not to the generic fallback."""
    p = PDEProblem(
        equation_latex="u_{tt} = c^2*u_{xx}",
        equation_kind="wave",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],
        initial_conditions=[
            InitialCondition(order=0, value="exp(-x^2)"),
            InitialCondition(order=1, value="0"),
        ],
        parameters={"c": "positive"},
    )
    resp = solve(p)
    assert resp.method == "dalembert_wave_1d"


def test_laplace_rect_still_wins():
    p = PDEProblem(
        equation_latex="u_{xx} + u_{yy} = 0",
        equation_kind="laplace",
        domain=Domain(x=["0", "a"], y=["0", "b"]),
        boundary_conditions=[
            {"type": "dirichlet", "where": "x=0", "value": "0"},
            {"type": "dirichlet", "where": "x=a", "value": "0"},
            {"type": "dirichlet", "where": "y=0", "value": "0"},
            {"type": "dirichlet", "where": "y=b", "value": "sin(pi*x/a)"},
        ],
        initial_conditions=[],
        parameters={"a": "positive", "b": "positive"},
    )
    resp = solve(p)
    assert resp.method == "sov_laplace_rect"


# ---------------------------------------------------------------------------
# Classification correctness
# ---------------------------------------------------------------------------


def test_hyperbolic_classification_text():
    resp = solve(_general_problem("u_{xx} - 4*u_{xy} + 3*u_{yy} = 0"))
    classification_steps = [s for s in resp.steps if s.kind == "classification"]
    text = " ".join(s.latex for s in classification_steps).lower()
    assert "hiperb" in text or "delta > 0" in text or "\\delta > 0" in text


def test_parabolic_classification_text():
    resp = solve(_general_problem("u_{xx} + 4*u_{xy} + 4*u_{yy} = 0"))
    text = " ".join(s.latex for s in resp.steps if s.kind == "classification").lower()
    assert "parab" in text or "delta = 0" in text or "\\delta = 0" in text


def test_elliptic_classification_text():
    resp = solve(_general_problem("u_{xx} + 2*u_{xy} + 2*u_{yy} = 0"))
    text = " ".join(s.latex for s in resp.steps if s.kind == "classification").lower()
    assert "elípt" in text or "elipt" in text or "delta < 0" in text or "\\delta < 0" in text


# ---------------------------------------------------------------------------
# Closed form for the hyperbolic pure case
# ---------------------------------------------------------------------------


def test_hyperbolic_closed_form_structure():
    """For u_xx - 4 u_xy + 3 u_yy = 0 the solution is u = F(ξ) + G(η)
    with ξ, η linear in x, y along the two characteristic families."""
    resp = solve(_general_problem("u_{xx} - 4*u_{xy} + 3*u_{yy} = 0"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    # It should be a sum of two applied functions F(...) + G(...).
    assert isinstance(sol, sp.Add)
    # And it should satisfy the PDE symbolically.
    x, y = sp.Symbol("x", real=True), sp.Symbol("y", real=True)
    residual = sp.simplify(
        sp.diff(sol, x, 2)
        - 4 * sp.diff(sol, x, y)
        + 3 * sp.diff(sol, y, 2)
    )
    assert residual == 0


def test_hyperbolic_characteristics_are_correct():
    """For u_xx - 4 u_xy + 3 u_yy = 0 the characteristic equation is
    m² + 4m + 3 = 0 → m = -3 or -1, so ξ = y + 3x and η = y + x.
    """
    resp = solve(_general_problem("u_{xx} - 4*u_{xy} + 3*u_{yy} = 0"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    args = list(sol.args)
    assert len(args) == 2

    x, y = sp.Symbol("x", real=True), sp.Symbol("y", real=True)
    expected_args = {sp.expand(y + 3 * x), sp.expand(y + x)}
    got_args = {sp.expand(fn_call.args[0]) for fn_call in args}
    assert got_args == expected_args, f"got {got_args}, expected {expected_args}"


def test_elliptic_no_closed_form():
    """Elliptic case must NOT produce a closed-form general solution
    (no BCs given). The 'final' step explains the dropout."""
    resp = solve(_general_problem("u_{xx} + 2*u_{xy} + 2*u_{yy} = 0"))
    final = next(s for s in resp.steps if s.kind == "final")
    txt = final.explanation_md.lower()
    assert "bcs" in txt or "condicion" in txt or "no" in txt
    # No 'verification' step in dropout case
    assert not any(s.kind == "verification" for s in resp.steps)


# ---------------------------------------------------------------------------
# Pedagogy
# ---------------------------------------------------------------------------


def test_pedagogy_explains_three_families():
    resp = solve(_general_problem("u_{xx} - 4*u_{xy} + 3*u_{yy} = 0"))
    all_text = " ".join(
        s.title + " " + s.explanation_md for s in resp.steps
    ).lower()
    assert "hiperb" in all_text
    assert "parab" in all_text
    assert "elípt" in all_text or "elipt" in all_text


def test_pedagogy_mentions_characteristic_equation():
    resp = solve(_general_problem("u_{xx} - 4*u_{xy} + 3*u_{yy} = 0"))
    all_text = " ".join(s.latex for s in resp.steps).lower()
    assert "característ" in " ".join(
        s.explanation_md for s in resp.steps
    ).lower() or "caracter" in " ".join(
        s.title for s in resp.steps
    ).lower()


def test_response_has_canonical_change_step():
    resp = solve(_general_problem("u_{xx} - 4*u_{xy} + 3*u_{yy} = 0"))
    dev_steps = [s for s in resp.steps if s.kind == "development"]
    text = " ".join(s.title for s in dev_steps).lower()
    assert "canónic" in text or "canonic" in text
