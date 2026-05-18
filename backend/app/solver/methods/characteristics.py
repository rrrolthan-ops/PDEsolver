"""Method of characteristics for the 1D linear transport equation.

Problem covered
---------------
    u_t + c u_x = 0     in x ∈ ℝ,  t > 0,    c constant
    u(x, 0) = u_0(x)

Result: u(x, t) = u_0(x - c t).

This is the cleanest, most elementary first-order PDE — a perfect
classroom for the characteristic method. The same recipe extends to
quasilinear first-order equations, where characteristics stop being
parallel straight lines (we note this as a follow-on).
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class CharacteristicsTransport1D(Method):
    """Linear transport u_t + c u_x = 0 by the method of characteristics."""

    slug = "characteristics_transport_1d"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        c = sp.Symbol("c", positive=True)

        u0_latex = (
            problem.initial_conditions[0].value
            if problem.initial_conditions
            else "0"
        )
        u0_expr = parse_scalar_latex(u0_latex, problem.parameters).subs(
            sp.Symbol("x"), x
        )

        steps: list[Step] = []
        steps.append(self._step_statement(u0_latex))
        steps.append(self._step_classification())
        steps.append(self._step_method_motivation())
        steps += self._steps_construction(c)
        solution_expr = self._build_solution(u0_expr, c, x, t)
        steps += self._steps_apply_ic(u0_latex, solution_expr)
        steps.append(self._step_final(solution_expr))
        steps += self._steps_verification(solution_expr, c, x, t, u0_expr)
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # ---------------------------------------------------------------------

    def _step_statement(self, u0_latex: str) -> Step:
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (transporte 1D)",
            md=T.T_statement_characteristics(),
            latex=equation_chain(
                [
                    r"&u_t + c\, u_x = 0,\quad x \in \mathbb{R},\ t > 0,",
                    rf"&u(x, 0) = {u0_latex}.",
                ]
            ),
            level="basic",
            observations=[obs.get("characteristics_first_order")],
        )

    def _step_classification(self) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — EDP hiperbólica de primer orden",
            md=(
                "Es de primer orden, así que la clasificación clásica "
                "$B^2 - 4AC$ no aplica directamente. Sin embargo, "
                "pertenece a la clase de **EDPs hiperbólicas**: tiene "
                "una única familia de curvas características reales a "
                "lo largo de las cuales la solución se propaga."
            ),
            level="basic",
        )

    def _step_method_motivation(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Idea del método de las características",
            md=T.T_characteristics_method_motivation(),
            level="basic",
        )

    def _steps_construction(self, c: sp.Symbol) -> list[Step]:
        s_curves = step(
            kind="development",
            title="Paso 3.1 — Ecuaciones de las características",
            md=(
                "Las características son las curvas $x = x(t)$ con "
                "$dx/dt = c$. Como $c$ es constante, son **rectas "
                "paralelas** de pendiente $c$ en el plano $(x, t)$:"
            ),
            latex=equation_chain(
                [
                    r"\frac{dx}{dt} &= c,",
                    r"x(t) &= ct + \xi,",
                    r"\xi &= x - ct \quad \text{(parámetro de la característica)}.",
                ]
            ),
            level="basic",
        )
        s_invariance = step(
            kind="development",
            title="Paso 3.2 — $u$ es constante a lo largo de cada característica",
            md=T.T_characteristics_solve(),
            latex=equation_chain(
                [
                    r"\frac{du}{dt}\bigg|_{\text{a lo largo de la car.}} &= u_t + c\, u_x = 0,",
                    r"u(x, t) &= u(\xi, 0) = u_0(\xi).",
                ]
            ),
            level="basic",
        )
        return [s_curves, s_invariance]

    def _build_solution(
        self,
        u0_expr: sp.Basic,
        c: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
    ) -> sp.Basic:
        return u0_expr.subs(x, x - c * t)

    def _steps_apply_ic(self, u0_latex: str, solution_expr: sp.Basic) -> list[Step]:
        s = step(
            kind="initial",
            title=f"Paso 5 — Aplicación de $u_0(x) = {u0_latex}$",
            md=(
                "Sustituyendo $\\xi = x - ct$ en $u_0(\\xi)$ obtenemos "
                "directamente la solución cerrada."
            ),
            latex=rf"u(x, t) = u_0(x - ct) = {sp.latex(solution_expr)}.",
            level="basic",
        )
        return [s]

    def _step_final(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Solución",
            md="La solución cerrada es:",
            latex=rf"\boxed{{\; u(x, t) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        c: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
        u0_expr: sp.Basic,
    ) -> list[Step]:
        residual = sp.simplify(
            sp.diff(solution_expr, t) + c * sp.diff(solution_expr, x)
        )
        pde_ok = bool(residual == 0)
        ic_residual = sp.simplify(solution_expr.subs(t, 0) - u0_expr)

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "Comprobamos que $u_t + c u_x = 0$ y que $u(x, 0) = u_0(x)$."
            ),
            level="basic",
        )
        s_pde = step(
            kind="verification",
            title="Verificación de la EDP",
            md=(
                "Por la regla de la cadena, $u_t = -c u_0'(x-ct)$ y "
                "$u_x = u_0'(x-ct)$, así que $u_t + c u_x = 0$ idénticamente."
                if pde_ok
                else "**Atención:** residuo no nulo."
            ),
            latex=rf"u_t + c\, u_x = {sp.latex(residual)}.",
            level="intermediate",
        )
        s_ic = step(
            kind="verification",
            title="Verificación de la condición inicial",
            md=(
                "En $t = 0$, $u(x, 0) = u_0(x - 0) = u_0(x)$."
                if ic_residual == 0
                else "**Atención:** la IC no coincide."
            ),
            latex=rf"u(x, 0) - u_0(x) = {sp.latex(ic_residual)}.",
            level="intermediate",
        )
        return [s_intro, s_pde, s_ic]

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_characteristics_physical_interpretation(),
            level="basic",
            observations=[obs.get("characteristics_shock_warning")],
        )
