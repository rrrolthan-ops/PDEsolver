"""Tests for the rectangular drum: wave equation on [0,a]×[0,b]."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _drum_problem(f: str, g: str = "0") -> PDEProblem:
    return PDEProblem(
        equation_latex="u_{tt} = c^2*(u_{xx}+u_{yy})",
        equation_kind="wave",
        domain=Domain(x=["0", "a"], y=["0", "b"], t=["0", "infty"]),
        boundary_conditions=[
            {"type": "dirichlet", "where": "x=0", "value": "0"},
            {"type": "dirichlet", "where": "x=a", "value": "0"},
            {"type": "dirichlet", "where": "y=0", "value": "0"},
            {"type": "dirichlet", "where": "y=b", "value": "0"},
        ],
        initial_conditions=[
            InitialCondition(order=0, value=f),
            InitialCondition(order=1, value=g),
        ],
        parameters={"a": "positive", "b": "positive", "c": "positive"},
    )


def test_routes_to_wave_rect():
    resp = solve(_drum_problem("sin(pi*x/a)*sin(pi*y/b)"))
    assert resp.method == "sov_wave_rect"


def test_1d_wave_still_routes_to_sov_wave_1d():
    """A 1D wave (no y in domain) must keep going to sov_wave_1d."""
    p = PDEProblem(
        equation_latex="u_{tt} = c^2*u_{xx}",
        equation_kind="wave",
        domain=Domain(x=["0", "L"], t=["0", "infty"]),
        boundary_conditions=[
            {"type": "dirichlet", "where": "x=0", "value": "0"},
            {"type": "dirichlet", "where": "x=L", "value": "0"},
        ],
        initial_conditions=[
            InitialCondition(order=0, value="sin(pi*x/L)"),
            InitialCondition(order=1, value="0"),
        ],
        parameters={"L": "positive", "c": "positive"},
    )
    resp = solve(p)
    assert resp.method == "sov_wave_1d"


def test_wave_disk_still_routes_to_wave_disk():
    p = PDEProblem(
        equation_latex="u_{tt} = c^2*nabla^2 u",
        equation_kind="wave",
        geometry="disk",
        domain=Domain(t=["0", "infty"]),
        boundary_conditions=[{"type": "dirichlet", "where": "r=R", "value": "0"}],
        initial_conditions=[
            InitialCondition(order=0, value="1"),
            InitialCondition(order=1, value="0"),
        ],
        parameters={"R": "positive", "c": "positive"},
    )
    resp = solve(p)
    assert resp.method == "sov_wave_disk"


def test_fundamental_mode_recovered():
    """For f = sin(πx/a)sin(πy/b), only the (1,1) mode survives. The
    solution should reduce to sin(πx/a) sin(πy/b) cos(ω_{11} t) under
    the snapshot."""
    resp = solve(_drum_problem("sin(pi*x/a)*sin(pi*y/b)", "0"))
    final = next(s for s in resp.steps if s.kind == "final")
    # The plot's t = 0 slice should peak at exactly the input profile.
    plot = resp.plot_data
    assert plot is not None
    max_u = max(max(row) for row in plot["u"])
    # Peak of sin(πx) sin(πy) on the unit square is 1 (at x = y = 0.5).
    assert abs(max_u - 1.0) < 0.01


def test_solution_is_double_sum():
    """The solution is a double Sum — SymPy may collapse two nested
    Sums into a single Sum with two limit tuples, or keep them nested.
    Either shape is acceptable."""
    resp = solve(_drum_problem("sin(pi*x/a)*sin(pi*y/b)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    assert isinstance(sol, sp.Sum)
    # Total number of dummy variables across nested Sums = 2.
    dummies: list = []
    expr_walker = sol
    while isinstance(expr_walker, sp.Sum):
        dummies.extend(expr_walker.limits)
        expr_walker = expr_walker.function
    assert len(dummies) == 2, f"expected 2 sum dummies, got {len(dummies)}: {dummies}"


def test_pedagogy_mentions_frequencies():
    resp = solve(_drum_problem("sin(pi*x/a)*sin(pi*y/b)"))
    text = " ".join(s.title + " " + s.explanation_md for s in resp.steps).lower()
    assert "frecuenc" in text or "ω" in text or "omega" in text or "\\omega" in text
    # Mentions both the harmonic 1D contrast and the rectangular/circular drum.
    assert "tambor" in text or "drum" in text or "rectang" in text


def test_pedagogy_mentions_degeneracy_or_chladni():
    resp = solve(_drum_problem("sin(pi*x/a)*sin(pi*y/b)"))
    text = " ".join(s.title + " " + s.explanation_md for s in resp.steps).lower()
    assert "degenera" in text or "chladni" in text


def test_pedagogy_mentions_kac():
    """The "can one hear the shape of a drum" hook."""
    resp = solve(_drum_problem("sin(pi*x/a)*sin(pi*y/b)"))
    text = " ".join(s.title + " " + s.explanation_md for s in resp.steps).lower()
    assert "kac" in text


def test_classification_step_says_hyperbolic_2d():
    resp = solve(_drum_problem("sin(pi*x/a)*sin(pi*y/b)"))
    classif = next(s for s in resp.steps if s.kind == "classification")
    text = (classif.title + " " + classif.explanation_md).lower()
    assert "hiperb" in text


def test_verification_present():
    resp = solve(_drum_problem("sin(pi*x/a)*sin(pi*y/b)"))
    verif_steps = [s for s in resp.steps if s.kind == "verification"]
    # intro + PDE check + BC check
    assert len(verif_steps) >= 3


def test_plot_satisfies_bcs():
    """u(x, y, 0) on the boundary should be zero (it's the initial
    profile sin(πx/a)sin(πy/b) with sin(0) = sin(π) = 0)."""
    resp = solve(_drum_problem("sin(pi*x/a)*sin(pi*y/b)"))
    plot = resp.plot_data
    # The 4 corners (i=0, i=-1, j=0, j=-1) should all be ≈ 0.
    u = plot["u"]
    for v in u[0]:  # top edge
        assert abs(v) < 1e-3
    for v in u[-1]:  # bottom edge
        assert abs(v) < 1e-3
    for row in u:
        assert abs(row[0]) < 1e-3 and abs(row[-1]) < 1e-3
