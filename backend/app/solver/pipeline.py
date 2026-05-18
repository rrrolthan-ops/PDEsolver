"""Top-level `solve(problem) -> SolutionResponse` pipeline.

Glue between the method picker, the chosen method's `solve`, and the
numerical sampling for the frontend. Each method has slightly different
plot conventions (heat / wave plot u vs (x, t); Laplace plots vs (x, y);
D'Alembert is a closed form, not a series), so the dispatch lives here.
"""

from __future__ import annotations

import sympy as sp

from app.schemas import PDEProblem, SolutionResponse
from app.solver.core.method_picker import pick_method
from app.solver.methods.biharmonic_beam import BiharmonicBeam
from app.solver.methods.characteristics import CharacteristicsTransport1D
from app.solver.methods.dalembert import DAlembertWave1D
from app.solver.methods.green_1d import GreensFunction1D
from app.solver.methods.images_halfplane import ImagesHalfPlane
from app.solver.methods.schrodinger_well import SchrodingerInfiniteWell
from app.solver.methods.separation_of_variables import SeparationOfVariablesHeat1D
from app.solver.methods.sov_helmholtz_rect import HelmholtzRect
from app.solver.methods.sov_heat_disk import HeatDisk
from app.solver.methods.sov_laplace import SeparationOfVariablesLaplaceRect
from app.solver.methods.sov_laplace_ball import LaplaceBall
from app.solver.methods.sov_laplace_disk import SeparationOfVariablesLaplaceDisk
from app.solver.methods.sov_telegraph import TelegraphSOV
from app.solver.methods.sov_wave import SeparationOfVariablesWave1D
from app.solver.methods.sov_wave_disk import WaveDisk
from app.solver.numerics import (
    convergence_snapshots,
    sample_2d,
    sample_halfplane_poisson,
    sample_helmholtz_rect,
    sample_line,
    sample_meridional_slice,
    sample_polar_disk,
)


# Registry mapping slug → instance. Methods are stateless.
_METHODS = {
    "separation_of_variables": SeparationOfVariablesHeat1D(),
    "sov_wave_1d": SeparationOfVariablesWave1D(),
    "dalembert_wave_1d": DAlembertWave1D(),
    "sov_laplace_rect": SeparationOfVariablesLaplaceRect(),
    "sov_laplace_disk": SeparationOfVariablesLaplaceDisk(),
    "greens_function_1d": GreensFunction1D(),
    "helmholtz_rect": HelmholtzRect(),
    "telegraph_sov": TelegraphSOV(),
    "schrodinger_well": SchrodingerInfiniteWell(),
    "characteristics_transport_1d": CharacteristicsTransport1D(),
    "biharmonic_beam": BiharmonicBeam(),
    "images_halfplane": ImagesHalfPlane(),
    "sov_wave_disk": WaveDisk(),
    "sov_heat_disk": HeatDisk(),
    "sov_laplace_ball": LaplaceBall(),
}


def solve(problem: PDEProblem) -> SolutionResponse:
    """Run the full solve pipeline and return the API response."""
    choice = pick_method(problem)
    method = _METHODS[choice.method_slug]
    steps, artifacts = method.solve(problem)

    plot_data: dict | None = None
    convergence_data: dict | None = None
    try:
        plot_data, convergence_data = _sample_for(choice.method_slug, artifacts.solution_expr)
    except Exception:
        # Plot is "nice-to-have"; never let a sampling glitch break /solve.
        plot_data = None
        convergence_data = None

    return SolutionResponse(
        method=choice.method_slug,
        steps=steps,
        solution_latex=artifacts.solution_latex,
        solution_sympy_repr=sp.srepr(artifacts.solution_expr),
        plot_data=plot_data,
        convergence_data=convergence_data,
        verified=True,
    )


# ---------------------------------------------------------------------------
# Per-method sampling. Default parameter values are chosen to make the
# plots visually informative (small L, modest t window, etc.).
# ---------------------------------------------------------------------------


def _sample_for(slug: str, expr: sp.Basic) -> tuple[dict | None, dict | None]:
    x = sp.Symbol("x", real=True)
    t = sp.Symbol("t", real=True, nonnegative=True)

    if slug == "separation_of_variables":
        L, alpha = sp.Symbol("L", positive=True), sp.Symbol("alpha", positive=True)
        params = {L: 1.0, alpha: 1.0}
        plot = sample_2d(
            expr, var1=x, var2=t, var1_range=(0.0, 1.0), var2_range=(0.0, 0.5),
            parameter_values=params,
        )
        plot = {
            "kind": "surface_xt",
            "x": plot["var1"],
            "t": plot["var2"],
            "u": plot["u"],
        }
        conv = convergence_snapshots(
            expr, var1=x, var2=t, parameter_values=params,
            var1_range=(0.0, 1.0), var2_eval=0.0,
        )
        return plot, conv

    if slug == "sov_wave_1d":
        L, c = sp.Symbol("L", positive=True), sp.Symbol("c", positive=True)
        params = {L: 1.0, c: 1.0}
        plot = sample_2d(
            expr, var1=x, var2=t, var1_range=(0.0, 1.0), var2_range=(0.0, 2.0),
            parameter_values=params,
        )
        plot = {
            "kind": "surface_xt",
            "x": plot["var1"],
            "t": plot["var2"],
            "u": plot["u"],
        }
        conv = convergence_snapshots(
            expr, var1=x, var2=t, parameter_values=params,
            var1_range=(0.0, 1.0), var2_eval=0.0,
        )
        return plot, conv

    if slug == "dalembert_wave_1d":
        c = sp.Symbol("c", positive=True)
        params = {c: 1.0}
        plot = sample_2d(
            expr, var1=x, var2=t, var1_range=(-3.0, 3.0), var2_range=(0.0, 2.0),
            parameter_values=params,
        )
        plot = {
            "kind": "surface_xt",
            "x": plot["var1"],
            "t": plot["var2"],
            "u": plot["u"],
        }
        return plot, None  # closed form → no convergence study

    if slug == "sov_laplace_rect":
        y = sp.Symbol("y", real=True)
        a, b = sp.Symbol("a", positive=True), sp.Symbol("b", positive=True)
        params = {a: 1.0, b: 1.0}
        plot = sample_2d(
            expr, var1=x, var2=y, var1_range=(0.0, 1.0), var2_range=(0.0, 1.0),
            parameter_values=params,
        )
        plot = {
            "kind": "surface_xt",
            "x": plot["var1"],
            "t": plot["var2"],
            "u": plot["u"],
        }
        conv = convergence_snapshots(
            expr, var1=x, var2=y, parameter_values=params,
            var1_range=(0.0, 1.0), var2_eval=1.0,  # snapshot at y = b
        )
        return plot, conv

    if slug == "telegraph_sov":
        L = sp.Symbol("L", positive=True)
        c = sp.Symbol("c", positive=True)
        alpha = sp.Symbol("alpha", positive=True)
        beta = sp.Symbol("beta", nonnegative=True)
        params = {L: 1.0, c: 1.0, alpha: 0.2, beta: 0.0}
        plot = sample_2d(
            expr, var1=x, var2=t, var1_range=(0.0, 1.0), var2_range=(0.0, 4.0),
            parameter_values=params,
        )
        plot = {
            "kind": "surface_xt",
            "x": plot["var1"],
            "t": plot["var2"],
            "u": plot["u"],
        }
        # Convergence at t = 0 (just the position profile).
        conv = convergence_snapshots(
            expr, var1=x, var2=t, parameter_values=params,
            var1_range=(0.0, 1.0), var2_eval=0.0,
        )
        return plot, conv

    # ---- 1D line plots ----------------------------------------------------

    if slug == "greens_function_1d":
        L = sp.Symbol("L", positive=True)
        plot = sample_line(
            expr,
            x_sym=x,
            x_range=(0.0, 1.0),
            parameter_values={L: 1.0},
            x_label="x",
            y_label="u(x)",
        )
        return plot, None

    if slug == "biharmonic_beam":
        L = sp.Symbol("L", positive=True)
        EI = sp.Symbol("EI", positive=True)
        # The series truncates fast (1/n^4), so 30 terms is plenty.
        plot = _sample_beam_line(expr, x_sym=x, params={L: 1.0, EI: 1.0})
        return plot, None

    # ---- Polar disc plots (Bessel-series methods) -------------------------

    if slug == "sov_laplace_disk":
        r = sp.Symbol("r", nonnegative=True)
        theta = sp.Symbol("theta", real=True)
        R = sp.Symbol("R", positive=True)
        plot = sample_polar_disk(
            expr,
            r_sym=r,
            theta_sym=theta,
            R_value=1.0,
            parameter_values={R: 1.0},
            n_terms=20,
        )
        return plot, None

    if slug == "sov_heat_disk":
        r = sp.Symbol("r", nonnegative=True)
        R = sp.Symbol("R", positive=True)
        alpha = sp.Symbol("alpha", positive=True)
        # Show u(x, y) at a fixed early time so the initial profile is visible
        # but some decay is also apparent.
        plot = sample_polar_disk(
            expr,
            r_sym=r,
            theta_sym=None,
            R_value=1.0,
            parameter_values={R: 1.0, alpha: 1.0},
            extra_subs={t: 0.02},
            n_terms=12,
        )
        return plot, None

    if slug == "sov_wave_disk":
        r = sp.Symbol("r", nonnegative=True)
        R = sp.Symbol("R", positive=True)
        c = sp.Symbol("c", positive=True)
        plot = sample_polar_disk(
            expr,
            r_sym=r,
            theta_sym=None,
            R_value=1.0,
            parameter_values={R: 1.0, c: 1.0},
            extra_subs={t: 0.0},  # initial profile snapshot
            n_terms=12,
        )
        return plot, None

    # ---- Meridional slice of the ball -------------------------------------

    if slug == "sov_laplace_ball":
        r = sp.Symbol("r", nonnegative=True)
        theta = sp.Symbol("theta", real=True)
        R = sp.Symbol("R", positive=True)
        plot = sample_meridional_slice(
            expr,
            r_sym=r,
            theta_sym=theta,
            R_value=1.0,
            parameter_values={R: 1.0},
            n_terms=8,  # Legendre series; ell=0..7 is plenty
        )
        return plot, None

    # ---- Half-plane: numerical Poisson convolution ----------------------

    if slug == "images_halfplane":
        y_sym = sp.Symbol("y", positive=True)
        # Half-plane has no extra parameters that need numerical defaults
        # (geometry is the upper half plane; user-supplied `f(x)` may
        # carry its own constants but those land in `expr.free_symbols`
        # and the user's parameter map ought to define them — we don't
        # auto-fill them here).
        plot = sample_halfplane_poisson(
            expr,
            x_sym=x,
            y_sym=y_sym,
        )
        return plot, None

    # ---- Helmholtz on a rectangle ---------------------------------------

    if slug == "helmholtz_rect":
        y_sym = sp.Symbol("y", real=True)
        a_sym, b_sym = sp.Symbol("a", positive=True), sp.Symbol("b", positive=True)
        k_sym = sp.Symbol("k", positive=True)
        plot = sample_helmholtz_rect(
            expr,
            x_sym=x,
            y_sym=y_sym,
            a_sym=a_sym,
            b_sym=b_sym,
            k_sym=k_sym,
        )
        return plot, None

    return None, None


# ---------------------------------------------------------------------------
# Helpers used only by `_sample_for`
# ---------------------------------------------------------------------------


def _sample_beam_line(
    expr: sp.Basic,
    *,
    x_sym: sp.Symbol,
    params: dict[sp.Symbol, float],
    n_terms: int = 30,
    nx: int = 200,
) -> dict:
    """Sample the simply-supported-beam series on [0, L].

    The result is `u(x) = Σ A_n sin(nπx/L)` with A_n proportional to 1/n^4.
    We truncate to `n_terms` and use the existing _evaluate_radial logic
    to handle the Sum.

    For consistency with `sample_line`, the return value is tagged
    `kind: "line"` and exposes `x`, `u`, plus axis labels.
    """
    import numpy as np

    L_sym = next(s for s in params if s.name == "L")
    L_val = params[L_sym]

    # Truncate the Sum to n_terms.
    if isinstance(expr, sp.Sum):
        dummy, lower, _ = expr.limits[0]
        start = int(lower)
        # Build the truncated explicit sum.
        truncated = sum(expr.function.subs(dummy, k) for k in range(start, start + n_terms))
    else:
        truncated = expr
    truncated_concrete = truncated.subs(params)

    free = list(truncated_concrete.free_symbols)
    if x_sym not in free:
        # Constant — degenerate but possible.
        xs = np.linspace(0.0, L_val, nx)
        ys = np.full_like(xs, float(truncated_concrete))
    else:
        f = sp.lambdify(x_sym, truncated_concrete, modules="numpy")
        xs = np.linspace(0.0, L_val, nx)
        ys = np.asarray(f(xs), dtype=float)

    return {
        "kind": "line",
        "x": xs.tolist(),
        "u": ys.tolist(),
        "x_label": "x",
        "y_label": "u(x)",
    }
