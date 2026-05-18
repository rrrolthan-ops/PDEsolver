"""Tests for the new plot_data shapes from the pipeline.

We don't validate numerical accuracy here — the math has its own tests
in `tests/solver/`. We just lock the contract the frontend depends on:

- `kind` field is set correctly
- `x` / `y` / `u` (or `t` / `u`) arrays are present and have the right
  shapes
- NaN-outside-the-disc is rendered as JSON `None`, not a string
"""

from __future__ import annotations

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _heat_problem(initial: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="u_t = alpha^2 * u_{xx}",
        equation_kind="heat",
        domain=Domain(x=["0", "L"], t=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=L", value="0"),
        ],
        initial_conditions=[InitialCondition(order=0, value=initial)],
        parameters={"alpha": "positive", "L": "positive"},
    )


def _greens_problem(f_source: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="-u_{xx} = f(x)",
        equation_kind="poisson",
        source_term=f_source,
        domain=Domain(x=["0", "L"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=L", value="0"),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"L": "positive"},
    )


def _beam_problem(q: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="EI*u'''' = q(x)",
        equation_kind="biharmonic",
        source_term=q,
        domain=Domain(x=["0", "L"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=L", value="0"),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"L": "positive", "EI": "positive"},
    )


def _disk_laplace_problem(f_theta: str) -> PDEProblem:
    return PDEProblem(
        equation_latex=r"u_{rr} + (1/r)*u_r + (1/r^2)*u_{\theta\theta} = 0",
        equation_kind="laplace",
        geometry="disk",
        domain=Domain(x=["0", "R"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="r=R", value=f_theta),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"R": "positive"},
    )


def _heat_disk_problem(f_r: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="u_t = alpha^2*(u_{rr} + u_r/r)",
        equation_kind="heat",
        geometry="disk",
        domain=Domain(x=["0", "R"], t=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="r=R", value="0"),
        ],
        initial_conditions=[InitialCondition(order=0, value=f_r)],
        parameters={"R": "positive", "alpha": "positive"},
    )


def _ball_problem(f_theta: str) -> PDEProblem:
    return PDEProblem(
        equation_latex=r"\nabla^2 u = 0",
        equation_kind="laplace",
        geometry="sphere",
        domain=Domain(x=["0", "R"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="r=R", value=f_theta),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"R": "positive"},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_heat_1d_plot_is_surface_xt():
    resp = solve(_heat_problem("sin(pi*x/L)"))
    plot = resp.plot_data
    assert plot is not None
    assert plot.get("kind") == "surface_xt"
    assert "x" in plot and "t" in plot and "u" in plot
    assert len(plot["u"]) == len(plot["t"])
    assert len(plot["u"][0]) == len(plot["x"])


def test_greens_1d_plot_is_line():
    resp = solve(_greens_problem("x*(L - x)"))
    plot = resp.plot_data
    assert plot is not None
    assert plot.get("kind") == "line"
    assert "x" in plot and "u" in plot
    assert len(plot["x"]) == len(plot["u"])
    assert all(isinstance(v, float) for v in plot["u"])


def test_beam_plot_is_line():
    resp = solve(_beam_problem("sin(pi*x/L)"))
    plot = resp.plot_data
    assert plot is not None
    assert plot.get("kind") == "line"
    assert len(plot["x"]) == len(plot["u"])
    # Beam under sin(πx/L) bows downward (negative dip in the middle is
    # convention-dependent; we just check the magnitude is non-trivial).
    midpoint_displacement = plot["u"][len(plot["u"]) // 2]
    assert abs(midpoint_displacement) > 1e-6


def test_laplace_disk_plot_is_surface_xy_with_holes():
    resp = solve(_disk_laplace_problem("cos(theta)"))
    plot = resp.plot_data
    assert plot is not None
    assert plot.get("kind") == "surface_xy"
    assert "x" in plot and "y" in plot and "u" in plot
    assert plot.get("x_label") == "x"
    assert plot.get("y_label") == "y"
    # The corners of the bounding square must be outside the disc → None.
    corners = (plot["u"][0][0], plot["u"][0][-1], plot["u"][-1][0], plot["u"][-1][-1])
    assert all(c is None for c in corners)
    # The center should be a real number (u(0) = average of f over circle).
    n = len(plot["u"])
    center = plot["u"][n // 2][n // 2]
    assert center is not None
    assert isinstance(center, float)


def test_heat_disk_plot_renders():
    """Heat on disc samples a Bessel series numerically with scipy zeros."""
    resp = solve(_heat_disk_problem("1"))
    plot = resp.plot_data
    assert plot is not None
    assert plot.get("kind") == "surface_xy"
    # Center value should be positive (constant initial profile, mild decay).
    n = len(plot["u"])
    center = plot["u"][n // 2][n // 2]
    assert center is not None
    assert center > 0


def test_ball_plot_is_surface_xy_meridional():
    resp = solve(_ball_problem("cos(theta)"))
    plot = resp.plot_data
    assert plot is not None
    assert plot.get("kind") == "surface_xy"
    # Meridional slice convention: y-axis is z.
    assert plot.get("y_label") == "z"
    # u(r, θ) = (r/R) cos θ → at z = +R/2, x = 0: u = (R/2)·1 = 0.5.
    # We don't assert the exact value (grid alignment) but check the value
    # at the north pole vs south pole has opposite sign.
    n = len(plot["u"])
    # near top-center vs bottom-center, both inside the disc.
    top = plot["u"][int(n * 0.15)][n // 2]
    bottom = plot["u"][int(n * 0.85)][n // 2]
    assert top is not None and bottom is not None
    # Antisymmetric in z: opposite signs.
    assert top * bottom < 0
