"""Tests for the heat equation on x ∈ [0, ∞) via Laplace transform."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _halfline_problem(h_value: str = "h", alpha_param: str = "positive") -> PDEProblem:
    return PDEProblem(
        equation_latex="u_t = alpha^2 * u_{xx}",
        equation_kind="heat",
        domain=Domain(x=["0", "infty"], t=["0", "infty"]),
        boundary_conditions=[
            {"type": "dirichlet", "where": "x=0", "value": h_value},
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"alpha": alpha_param, "h": "positive"},
    )


X = sp.Symbol("x", real=True, nonnegative=True)
T = sp.Symbol("t", real=True, nonnegative=True)
ALPHA = sp.Symbol("alpha", positive=True)
H = sp.Symbol("h")  # bare — comes from sympify("h")


def test_routes_to_laplace_halfline():
    resp = solve(_halfline_problem("h"))
    assert resp.method == "laplace_heat_halfline"


def test_does_not_collide_with_bounded_heat():
    bounded = PDEProblem(
        equation_latex="u_t = alpha^2 * u_{xx}",
        equation_kind="heat",
        domain=Domain(x=["0", "L"], t=["0", "infty"]),
        boundary_conditions=[
            {"type": "dirichlet", "where": "x=0", "value": "0"},
            {"type": "dirichlet", "where": "x=L", "value": "0"},
        ],
        initial_conditions=[InitialCondition(order=0, value="sin(pi*x/L)")],
        parameters={"L": "positive", "alpha": "positive"},
    )
    resp = solve(bounded)
    assert resp.method == "separation_of_variables"


def test_does_not_collide_with_full_line_heat():
    """Full line (x ∈ ℝ, no BC) still goes to fourier_heat_line."""
    full_line = PDEProblem(
        equation_latex="u_t = alpha^2 * u_{xx}",
        equation_kind="heat",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],
        initial_conditions=[InitialCondition(order=0, value="exp(-x^2)")],
        parameters={"alpha": "positive"},
    )
    resp = solve(full_line)
    assert resp.method == "fourier_heat_line"


def test_final_formula_is_erfc():
    """Solution is exactly h · erfc(x / (2 α √t))."""
    resp = solve(_halfline_problem("h"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    expected = H * sp.erfc(X / (2 * ALPHA * sp.sqrt(T)))
    assert sp.simplify(sol - expected) == 0


def test_concrete_h_value():
    """With h = 1 the solution is just erfc(x/(2α√t))."""
    resp = solve(_halfline_problem("1"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    expected = sp.erfc(X / (2 * ALPHA * sp.sqrt(T)))
    assert sp.simplify(sol - expected) == 0


def test_solution_satisfies_pde():
    """u_t = α² u_xx — verified symbolically by the verification step.
    Re-check it here as a unit test on the artifact directly.
    """
    resp = solve(_halfline_problem("h"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    residual = sp.simplify(sp.diff(sol, T) - ALPHA**2 * sp.diff(sol, X, 2))
    assert residual == 0


def test_boundary_condition_satisfied():
    """u(0, t) = h."""
    resp = solve(_halfline_problem("h"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    at_wall = sp.simplify(sol.subs(X, 0))
    assert sp.simplify(at_wall - H) == 0


def test_initial_condition_limit():
    """u(x, 0+) = 0 for any x > 0 (erfc(∞) = 0)."""
    resp = solve(_halfline_problem("h"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    # Concrete x > 0 to avoid SymPy's hesitation about the sign.
    sol_at_x1 = sol.subs(X, 1)
    limit_t0 = sp.limit(sol_at_x1, T, 0, dir="+")
    assert sp.simplify(limit_t0) == 0


def test_pedagogy_mentions_laplace_and_erfc():
    resp = solve(_halfline_problem("h"))
    all_text = " ".join(
        s.title + " " + s.explanation_md for s in resp.steps
    ).lower()
    assert "laplace" in all_text
    assert "erfc" in all_text


def test_pedagogy_mentions_diffusion_length():
    resp = solve(_halfline_problem("h"))
    interp = next(s for s in resp.steps if s.kind == "interpretation")
    txt = interp.explanation_md.lower()
    assert (
        "longitud de difusión" in txt
        or "longitud de difusion" in txt
        or "$\\delta" in interp.explanation_md  # the symbol δ
    )


def test_pedagogy_mentions_self_similarity():
    resp = solve(_halfline_problem("h"))
    all_text = " ".join(
        s.title + " " + s.explanation_md for s in resp.steps
    ).lower()
    assert "autosimil" in all_text or "similarid" in all_text


def test_response_has_verification_steps():
    resp = solve(_halfline_problem("h"))
    verif_steps = [s for s in resp.steps if s.kind == "verification"]
    # Intro + PDE check + BC check + IC check.
    assert len(verif_steps) >= 4


def test_plot_is_surface_xt():
    resp = solve(_halfline_problem("h"))
    plot = resp.plot_data
    assert plot is not None
    assert plot.get("kind") == "surface_xt"
    # All values between 0 and h (= 1 in the plot defaults).
    for row in plot["u"]:
        for v in row:
            assert -1e-6 <= v <= 1.0 + 1e-6, f"out-of-range density: {v}"
            assert v == v  # not NaN


def test_plot_monotone_at_fixed_depth():
    """At a fixed x > 0, u(x, t) should be monotone increasing in t
    (the front advances into the medium)."""
    resp = solve(_halfline_problem("h"))
    plot = resp.plot_data
    # plot["u"] is indexed [t][x]. Pick a representative x somewhere
    # past the wall (third column) and check the column is monotone.
    col_idx = len(plot["x"]) // 3
    column = [plot["u"][i][col_idx] for i in range(len(plot["t"]))]
    for prev, curr in zip(column, column[1:]):
        # Numerical noise is tiny; require strict-ish monotonicity.
        assert curr >= prev - 1e-9
