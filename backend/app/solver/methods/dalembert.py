"""D'Alembert's formula for the 1D wave equation on the line.

Problem covered
---------------
    u_tt = c^2 u_xx        x ∈ ℝ,   t > 0
    u(x, 0) = f(x)
    u_t(x, 0) = g(x)

Solution
--------
    u(x, t) = (f(x - ct) + f(x + ct)) / 2
            + (1/(2c)) ∫_{x-ct}^{x+ct} g(s) ds

Why this method belongs alongside SOV
-------------------------------------
Pedagogically, D'Alembert teaches a completely different way of
thinking about waves: not as superposition of modes (Fourier picture)
but as superposition of two travelling pulses (characteristics picture).
This contrast — same PDE, two complementary mental models — is one of
the most valuable things to internalise about the wave equation.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class DAlembertWave1D(Method):
    """D'Alembert's formula for the wave equation on the infinite line."""

    slug = "dalembert_wave_1d"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        s_var = sp.Symbol("s", real=True)
        c = sp.Symbol("c", positive=True)

        # ---------- Parse f and g ---------------------------------------------
        f_latex = "0"
        g_latex = "0"
        for ic in problem.initial_conditions:
            if ic.order == 0:
                f_latex = ic.value
            elif ic.order == 1:
                g_latex = ic.value
        f_expr = parse_scalar_latex(f_latex, problem.parameters).subs(sp.Symbol("x"), x)
        g_expr = parse_scalar_latex(g_latex, problem.parameters).subs(sp.Symbol("x"), x)

        steps: list[Step] = []

        # ===== PASO 0 — Statement =============================================
        steps.append(self._step_statement(f_latex, g_latex))

        # ===== PASO 1 — Classification ========================================
        steps += self._steps_classification(c)

        # ===== PASO 2 — Method choice =========================================
        steps.append(self._step_method_choice())

        # ===== PASO 3 — Development ==========================================
        steps += self._steps_change_of_variables()
        steps.append(self._step_general_solution())

        # ===== PASO 5 — Apply initial conditions ==============================
        steps += self._steps_apply_ics()

        # ===== PASO 6 — Final formula =========================================
        solution_expr, integral_expr = self._build_solution_expression(
            f_expr, g_expr, c, x, t, s_var
        )
        steps.append(self._step_final_formula(solution_expr))

        # ===== PASO 7 — Verification =========================================
        steps += self._steps_verification(
            solution_expr, integral_expr, f_expr, g_expr, c, x, t
        )

        # ===== PASO 8 — Visualisation =========================================
        steps.append(self._step_visualization())

        # ===== PASO 9 — Physical interpretation ==============================
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # ===========================================================================
    # PASO 0
    # ===========================================================================

    def _step_statement(self, f_latex: str, g_latex: str) -> Step:
        latex = equation_chain(
            [
                r"&\text{EDP:} \quad u_{tt} = c^2\, u_{xx}, "
                r"\quad x \in \mathbb{R},\quad t > 0,",
                rf"&\text{{posición inicial:}} \quad u(x, 0) = {f_latex},",
                rf"&\text{{velocidad inicial:}} \quad u_t(x, 0) = {g_latex}.",
            ]
        )
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (línea infinita)",
            md=T.T_dalembert_statement(),
            latex=latex,
            level="basic",
        )

    # ===========================================================================
    # PASO 1
    # ===========================================================================

    def _steps_classification(self, c: sp.Symbol) -> list[Step]:
        A, B, C = c**2, sp.Integer(0), sp.Integer(-1)
        disc = sp.simplify(B**2 - 4 * A * C)
        s = step(
            kind="classification",
            title="Paso 1 — Clasificación (hiperbólica)",
            md=(
                "Coeficientes y discriminante:"
            ),
            latex=equation_chain(
                [
                    rf"A &= {sp.latex(A)},\quad B = {sp.latex(B)},\quad C = {sp.latex(C)},",
                    rf"\Delta &= B^2 - 4AC = {sp.latex(disc)} > 0,",
                    r"&\Rightarrow \text{EDP hiperbólica}.",
                ]
            ),
            level="basic",
        )
        return [s]

    # ===========================================================================
    # PASO 2
    # ===========================================================================

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método: factorización + características",
            md=T.T_dalembert_method_motivation(),
            latex=(
                r"\partial_t^2 - c^2 \partial_x^2 = "
                r"(\partial_t - c\partial_x)(\partial_t + c\partial_x)."
            ),
            level="basic",
            observations=[obs.get("dalembert_factorization")],
        )

    # ===========================================================================
    # PASO 3 — Change of variables
    # ===========================================================================

    def _steps_change_of_variables(self) -> list[Step]:
        s_def = step(
            kind="development",
            title="Paso 3.1 — Cambio a variables características",
            md=T.T_dalembert_change_of_variables(),
            latex=equation_chain(
                [
                    r"\xi &= x - ct,\quad \eta = x + ct,",
                    r"u_x &= u_\xi + u_\eta,\quad u_t = -c\, u_\xi + c\, u_\eta,",
                    r"u_{xx} &= u_{\xi\xi} + 2u_{\xi\eta} + u_{\eta\eta},",
                    r"u_{tt} &= c^2 u_{\xi\xi} - 2 c^2 u_{\xi\eta} + c^2 u_{\eta\eta}.",
                ]
            ),
            level="basic",
        )
        s_reduce = step(
            kind="development",
            title="Paso 3.2 — La EDP se reduce a $u_{\\xi\\eta} = 0$",
            md=(
                "Sustituyendo $u_{tt}$ y $c^2 u_{xx}$ en $u_{tt} - c^2 u_{xx} = 0$:"
            ),
            latex=equation_chain(
                [
                    r"u_{tt} - c^2 u_{xx} &= "
                    r"\bigl(c^2 u_{\xi\xi} - 2c^2 u_{\xi\eta} + c^2 u_{\eta\eta}\bigr)",
                    r"&\quad - c^2 \bigl(u_{\xi\xi} + 2 u_{\xi\eta} + u_{\eta\eta}\bigr)",
                    r"&= -4 c^2\, u_{\xi\eta},",
                    r"&\Rightarrow u_{\xi\eta} = 0.",
                ]
            ),
            level="basic",
        )
        return [s_def, s_reduce]

    def _step_general_solution(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.3 — Solución general en $(\\xi, \\eta)$",
            md=T.T_dalembert_general_solution(),
            latex=equation_chain(
                [
                    r"u_\eta &\text{ no depende de } \eta \Rightarrow u_\eta = h(\xi),",
                    r"u(\xi, \eta) &= \int h(\xi)\, d\eta + \Phi(\xi) "
                    r"= \Psi(\eta) + \Phi(\xi),",
                    r"u(x, t) &= \Phi(x - ct) + \Psi(x + ct).",
                ]
            ),
            level="basic",
        )

    # ===========================================================================
    # PASO 5 — Apply ICs
    # ===========================================================================

    def _steps_apply_ics(self) -> list[Step]:
        s_apply = step(
            kind="initial",
            title="Paso 5 — Aplicación de las condiciones iniciales",
            md=T.T_dalembert_apply_ics(),
            latex=equation_chain(
                [
                    r"u(x, 0) = f(x) &\Rightarrow \Phi(x) + \Psi(x) = f(x),",
                    r"u_t(x, 0) = g(x) &\Rightarrow -c\Phi'(x) + c\Psi'(x) = g(x),",
                    r"&\Rightarrow \Psi'(x) - \Phi'(x) = g(x)/c,",
                    r"&\Rightarrow \Psi(x) - \Phi(x) = \tfrac{1}{c}\!\int_0^x g(s)\, ds + K.",
                ]
            ),
            level="basic",
        )
        s_solve = step(
            kind="initial",
            title="Paso 5.1 — Despeje de $\\Phi$ y $\\Psi$",
            md=T.T_dalembert_formula(),
            latex=equation_chain(
                [
                    r"\Phi(x) &= \tfrac{1}{2} f(x) - \tfrac{1}{2c}\int_0^x g(s)\, ds - \tfrac{K}{2},",
                    r"\Psi(x) &= \tfrac{1}{2} f(x) + \tfrac{1}{2c}\int_0^x g(s)\, ds + \tfrac{K}{2}.",
                ]
            ),
            level="intermediate",
        )
        return [s_apply, s_solve]

    # ===========================================================================
    # PASO 6 — Final formula
    # ===========================================================================

    def _build_solution_expression(
        self,
        f_expr: sp.Basic,
        g_expr: sp.Basic,
        c: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
        s_var: sp.Symbol,
    ) -> tuple[sp.Basic, sp.Basic]:
        """Build u(x, t) = (f(x-ct) + f(x+ct))/2 + 1/(2c) ∫g.

        We return the expression with the integral **kept symbolic** even
        when SymPy could close it: keeping the integral makes the
        verification step crisper and matches what students see in books.
        Separately we also return the evaluated integral expression for
        the closed-form display.
        """
        f_minus = f_expr.subs(x, x - c * t)
        f_plus = f_expr.subs(x, x + c * t)

        g_of_s = g_expr.subs(x, s_var)
        integral_expr = sp.integrate(g_of_s, (s_var, x - c * t, x + c * t))
        integral_expr = sp.simplify(integral_expr)

        u = (f_minus + f_plus) / 2 + integral_expr / (2 * c)
        u = sp.simplify(u)
        return u, integral_expr

    def _step_final_formula(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Fórmula de D'Alembert",
            md=T.T_dalembert_final_box(),
            latex=rf"\boxed{{\; u(x, t) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    # ===========================================================================
    # PASO 7 — Verification
    # ===========================================================================

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        integral_expr: sp.Basic,
        f_expr: sp.Basic,
        g_expr: sp.Basic,
        c: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
    ) -> list[Step]:
        u_tt = sp.diff(solution_expr, t, 2)
        u_xx = sp.diff(solution_expr, x, 2)
        residual = sp.simplify(u_tt - c**2 * u_xx)
        pde_ok = bool(residual == 0)

        # IC checks: u(x, 0) should give f; u_t(x, 0) should give g.
        u_at_0 = sp.simplify(solution_expr.subs(t, 0))
        u_t = sp.diff(solution_expr, t)
        u_t_at_0 = sp.simplify(u_t.subs(t, 0))

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "Comprobamos que la fórmula obtenida satisface la EDP y "
                "las dos condiciones iniciales. Para D'Alembert la "
                "verificación es especialmente didáctica: cada pieza "
                "(la media de $f$ y la integral de $g$) cumple su parte."
            ),
            level="basic",
        )
        s_pde = step(
            kind="verification",
            title="Verificación de la EDP",
            md=(
                "Calculamos $u_{tt}$ y $c^2 u_{xx}$ y restamos. La regla "
                "de la cadena hace caer todos los términos."
                if pde_ok
                else "**Atención:** el residuo no se simplificó a cero."
            ),
            latex=rf"u_{{tt}} - c^2 u_{{xx}} = {sp.latex(residual)}.",
            level="intermediate",
        )
        s_ic_pos = step(
            kind="verification",
            title="Verificación de $u(x, 0) = f(x)$",
            md=(
                "En $t = 0$: $f(x - 0) = f(x + 0) = f(x)$ y la integral "
                "$\\int_{x}^{x} g\\, ds = 0$. Por tanto $u(x, 0) = f(x)$."
            ),
            latex=rf"u(x, 0) = {sp.latex(u_at_0)} \overset{{!}}{{=}} {sp.latex(f_expr)}.",
            level="intermediate",
        )
        s_ic_vel = step(
            kind="verification",
            title="Verificación de $u_t(x, 0) = g(x)$",
            md=(
                "Derivando respecto a $t$ y evaluando en $t = 0$, los "
                "términos en $f$ se cancelan (suman $-c f'(x) + c f'(x) = 0$) "
                "y queda exactamente $g(x)$ (por el teorema fundamental "
                "del cálculo aplicado a la integral de $g$)."
            ),
            latex=rf"u_t(x, 0) = {sp.latex(u_t_at_0)} \overset{{!}}{{=}} {sp.latex(g_expr)}.",
            level="intermediate",
        )
        return [s_intro, s_pde, s_ic_pos, s_ic_vel]

    # ===========================================================================
    # PASOS 8 y 9
    # ===========================================================================

    def _step_visualization(self) -> Step:
        return step(
            kind="visualization",
            title="Paso 8 — Visualización",
            md=(
                "El panel adjunto muestra $u(x, t)$ en un dominio acotado "
                "(en realidad la solución vive en $\\mathbb{R}$, "
                "pero se grafica un trozo). Si $g = 0$, observa cómo el "
                "perfil inicial se reparte en dos copias **idénticas** que "
                "viajan en direcciones opuestas a velocidad $c$.\n\n"
                "Para visualizar las **rectas características** "
                "$x \\pm ct = \\text{cte}$, fíjate en cualquier perfil "
                "constante en la superficie: avanza diagonalmente."
            ),
            level="basic",
        )

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_dalembert_physical_interpretation(),
            level="basic",
            observations=[obs.get("dalembert_domain_of_dependence")],
        )
