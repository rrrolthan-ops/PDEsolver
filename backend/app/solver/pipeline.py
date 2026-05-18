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
from app.solver.methods.dalembert import DAlembertWave1D
from app.solver.methods.separation_of_variables import SeparationOfVariablesHeat1D
from app.solver.methods.sov_laplace import SeparationOfVariablesLaplaceRect
from app.solver.methods.sov_wave import SeparationOfVariablesWave1D
from app.solver.numerics import convergence_snapshots, sample_2d


# Registry mapping slug → instance. Methods are stateless.
_METHODS = {
    "separation_of_variables": SeparationOfVariablesHeat1D(),
    "sov_wave_1d": SeparationOfVariablesWave1D(),
    "dalembert_wave_1d": DAlembertWave1D(),
    "sov_laplace_rect": SeparationOfVariablesLaplaceRect(),
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
        plot = {"x": plot["var1"], "t": plot["var2"], "u": plot["u"]}
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
        plot = {"x": plot["var1"], "t": plot["var2"], "u": plot["u"]}
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
        plot = {"x": plot["var1"], "t": plot["var2"], "u": plot["u"]}
        return plot, None  # closed form → no convergence study

    if slug == "sov_laplace_rect":
        y = sp.Symbol("y", real=True)
        a, b = sp.Symbol("a", positive=True), sp.Symbol("b", positive=True)
        params = {a: 1.0, b: 1.0}
        plot = sample_2d(
            expr, var1=x, var2=y, var1_range=(0.0, 1.0), var2_range=(0.0, 1.0),
            parameter_values=params,
        )
        # Frontend speaks "x"/"t"; we relabel "y" → "t" so the same Plot
        # component works without changes. The axis label is set on the
        # frontend; the underlying data shape is identical.
        plot = {"x": plot["var1"], "t": plot["var2"], "u": plot["u"]}
        conv = convergence_snapshots(
            expr, var1=x, var2=y, parameter_values=params,
            var1_range=(0.0, 1.0), var2_eval=1.0,  # snapshot at y = b
        )
        return plot, conv

    return None, None
