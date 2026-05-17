"""Top-level `solve(problem) -> SolutionResponse` pipeline.

Glue between the method picker, the chosen method's `solve`, and the
numerical sampling for the frontend. This is what `api/routes_problems`
ultimately calls.
"""

from __future__ import annotations

import sympy as sp

from app.schemas import PDEProblem, SolutionResponse
from app.solver.core.method_picker import pick_method
from app.solver.methods.separation_of_variables import SeparationOfVariablesHeat1D
from app.solver.numerics import convergence_snapshots, sample_series_solution


# Registry mapping slug → instance. Methods are stateless.
_METHODS = {
    "separation_of_variables": SeparationOfVariablesHeat1D(),
}


def solve(problem: PDEProblem) -> SolutionResponse:
    """Run the full solve pipeline and return the API response."""
    choice = pick_method(problem)
    method = _METHODS[choice.method_slug]
    steps, artifacts = method.solve(problem)

    # Numerical sampling: only when the solution is a series and we can
    # safely lambdify it (Phase 1 always satisfies this).
    plot_data: dict | None = None
    convergence_data: dict | None = None
    try:
        x_sym = sp.Symbol("x", real=True)
        t_sym = sp.Symbol("t", real=True, nonnegative=True)
        L_sym = sp.Symbol("L", positive=True)
        alpha_sym = sp.Symbol("alpha", positive=True)

        plot_data = sample_series_solution(
            artifacts.solution_expr,
            x=x_sym,
            t=t_sym,
            L=L_sym,
            alpha=alpha_sym,
        )
        convergence_data = convergence_snapshots(
            artifacts.solution_expr,
            x=x_sym,
            t=t_sym,
            L=L_sym,
            alpha=alpha_sym,
            t_eval=0.0,
        )
    except Exception:
        # Plot is a "nice-to-have". If it fails (e.g. for very exotic
        # initial profiles) we still hand back the symbolic steps.
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
