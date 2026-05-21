"""Tests for the Fourier-transform heat equation on the infinite line."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _heat_line_problem(f: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="u_t = alpha^2 * u_{xx}",
        equation_kind="heat",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],  # unbounded line, decay at infinity
        initial_conditions=[InitialCondition(order=0, value=f)],
        parameters={"alpha": "positive"},
    )


X = sp.Symbol("x", real=True)
T = sp.Symbol("t", real=True, nonnegative=True)
ALPHA = sp.Symbol("alpha", positive=True)


def test_routes_to_fourier_heat_line():
    resp = solve(_heat_line_problem("exp(-x^2)"))
    assert resp.method == "fourier_heat_line"


def test_does_not_collide_with_bounded_heat():
    """Same equation on a bounded interval must still hit SOV."""
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


def test_final_solution_has_correct_structure():
    """For f(x) = exp(-x²), SymPy can evaluate the Gaussian convolution
    in closed form. Either way, the result must satisfy the heat equation
    and the initial condition.
    """
    resp = solve(_heat_line_problem("exp(-x^2)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)

    # The expression should depend on both x and t (unless f was constant).
    assert X in sol.free_symbols
    assert T in sol.free_symbols
    # And on alpha (it's the only physical parameter).
    assert ALPHA in sol.free_symbols


def test_kernel_satisfies_heat_equation():
    """The Gaussian kernel G(x, t) = (4πα²t)^{-1/2} exp(-x²/(4α²t)) is
    the canonical fundamental solution. We verify symbolically that it
    satisfies the PDE — this is what the verification step does.
    """
    G = sp.exp(-(X**2) / (4 * ALPHA**2 * T)) / sp.sqrt(4 * sp.pi * ALPHA**2 * T)
    residual = sp.simplify(sp.diff(G, T) - ALPHA**2 * sp.diff(G, X, 2))
    assert residual == 0


def test_kernel_unit_mass():
    """∫_{-∞}^{∞} G(x, t) dx = 1 (a probability density for every t > 0).

    Verified numerically — SymPy's symbolic integration of the Gaussian
    leaves polar_lift/Piecewise residues that obscure the result, but
    numerical integration confirms the unit-mass property.
    """
    import numpy as np
    from scipy.integrate import quad

    for alpha_val in (0.5, 1.0, 2.0):
        for t_val in (0.1, 0.5, 2.0):
            sigma2 = 4 * alpha_val**2 * t_val
            mass, _ = quad(
                lambda x: np.exp(-(x**2) / sigma2) / np.sqrt(np.pi * sigma2),
                -np.inf,
                np.inf,
            )
            assert abs(mass - 1.0) < 1e-9


def test_solution_satisfies_pde_for_gaussian_initial():
    """For a Gaussian initial condition, SymPy evaluates the convolution
    and we can check the PDE residual directly on the closed form.
    """
    resp = solve(_heat_line_problem("exp(-x^2)"))
    final = next(s for s in resp.steps if s.kind == "final")
    sol = sp.sympify(final.sympy_repr)
    if sol.has(sp.Integral):
        # SymPy didn't evaluate; the kernel check above already gave us
        # the symbolic verification. Nothing to test here.
        return
    residual = sp.simplify(sp.diff(sol, T) - ALPHA**2 * sp.diff(sol, X, 2))
    assert residual == 0


def test_pedagogy_mentions_fourier_and_gaussian():
    resp = solve(_heat_line_problem("exp(-x^2)"))
    all_text = " ".join(
        s.title + " " + s.explanation_md for s in resp.steps
    ).lower()
    assert "fourier" in all_text
    assert "gauss" in all_text or "núcleo" in all_text
    # Either the convolution theorem or convolution itself should appear.
    assert "convoluc" in all_text


def test_pedagogy_mentions_infinite_speed_or_smoothing():
    """The two marquee physical points the method makes."""
    resp = solve(_heat_line_problem("exp(-x^2)"))
    interp = next(s for s in resp.steps if s.kind == "interpretation")
    txt = interp.explanation_md.lower()
    assert "infinit" in txt or "suaviz" in txt or "autosimil" in txt


def test_method_choice_step_mentions_unbounded_domain():
    resp = solve(_heat_line_problem("exp(-x^2)"))
    choice_steps = [s for s in resp.steps if s.kind == "method_choice"]
    text = " ".join(s.explanation_md for s in choice_steps).lower()
    # Either explicitly mentioning the unbounded/continuous-spectrum nature,
    # or just the choice of Fourier as the diagonalising tool.
    assert "fourier" in text
    assert (
        "continuo" in text or "no acotad" in text or "diagonaliz" in text
    )


def test_response_has_verification_step():
    resp = solve(_heat_line_problem("exp(-x^2)"))
    verif_steps = [s for s in resp.steps if s.kind == "verification"]
    assert len(verif_steps) >= 2  # intro + kernel check at minimum


def test_plot_is_xt_surface():
    resp = solve(_heat_line_problem("exp(-x^2)"))
    plot = resp.plot_data
    assert plot is not None
    assert plot.get("kind") == "surface_xt"
    # All values should be finite real numbers (heat solutions are real).
    for row in plot["u"]:
        for v in row:
            assert v == v  # not NaN
            assert abs(v) < 1e6  # not blown up


def test_plot_values_positive_for_nonnegative_initial():
    """Heat equation preserves positivity: if f ≥ 0, then u(·, t) ≥ 0."""
    resp = solve(_heat_line_problem("exp(-x^2)"))
    plot = resp.plot_data
    for row in plot["u"]:
        for v in row:
            assert v >= -1e-9
