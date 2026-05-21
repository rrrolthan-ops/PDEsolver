"""Heat equation on the semi-infinite line via the Laplace transform.

Problem covered
---------------
    u_t = α² u_xx              x > 0,   t > 0
    u(x, 0) = 0
    u(0, t) = h                (constant Dirichlet at the wall)
    u(x, t) bounded as x → ∞

Solution
--------
    u(x, t) = h · erfc(x / (2 α √t))

Why Laplace and not Fourier
---------------------------
The natural transform is determined by *where* the inhomogeneous data
lives:

- u_t = α² u_xx, **on the full line ℝ**, data on t = 0: use Fourier in
  x (`fourier_heat_line`).
- u_t = α² u_xx, **on x > 0**, data on x = 0 (time-dependent boundary):
  use **Laplace in t** (this method). The boundary condition becomes the
  forcing in the transformed problem, the initial condition is folded
  automatically into ∂_t → s.

The two methods together cover the classical "transform-and-invert"
toolkit for the heat equation on unbounded domains.
"""

from __future__ import annotations

import sympy as sp

from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class LaplaceHeatHalfLine(Method):
    """Laplace-transform solution of the heat equation on x ∈ [0, ∞)."""

    slug = "laplace_heat_halfline"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True, nonnegative=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        s = sp.Symbol("s", positive=True)
        alpha = sp.Symbol("alpha", positive=True)

        # ---------- Parse boundary value h --------------------------------
        # We accept either a numeric or symbolic h. Defaults to a generic
        # parameter `h` when the BC value is anything other than a single
        # constant; the pedagogy doesn't change for the constant-BC case.
        h_value = self._extract_h(problem)
        h_sym = sp.sympify(h_value)

        steps: list[Step] = []

        # ===== PASO 0 — Statement =========================================
        steps.append(self._step_statement(h_value))

        # ===== PASO 1 — Classification ====================================
        steps.append(self._step_classification(alpha))

        # ===== PASO 2 — Method choice =====================================
        steps.append(self._step_method_choice())

        # ===== PASO 3 — Development ======================================
        steps.append(self._step_pde_to_ode(alpha, x, s))
        steps.append(self._step_solve_ode(alpha, x, s, h_sym))
        steps.append(self._step_inverse(alpha, x, t))

        # ===== PASO 4 — Boundary conditions (formally already applied in 3.2)
        steps.append(self._step_bcs())

        # ===== PASO 5 — Initial condition (folded into ∂_t → s)
        steps.append(self._step_ic())

        # ===== PASO 6 — Final formula ====================================
        solution_expr = h_sym * sp.erfc(x / (2 * alpha * sp.sqrt(t)))
        steps.append(self._step_final_formula(solution_expr))

        # ===== PASO 7 — Verification =====================================
        steps += self._steps_verification(solution_expr, alpha, x, t, h_sym)

        # ===== PASO 8 — Visualisation ====================================
        steps.append(self._step_visualization())

        # ===== PASO 9 — Physical interpretation ==========================
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # ===========================================================================
    # Helpers
    # ===========================================================================

    @staticmethod
    def _extract_h(problem: PDEProblem) -> str:
        """Pull the constant Dirichlet value at x = 0 out of the BCs.

        We default to ``h`` (treated as a symbolic positive parameter) so
        that the formula and the verification step can run even when the
        user hasn't given a concrete number.
        """
        for bc in problem.boundary_conditions:
            where = bc.where.replace(" ", "").lower()
            if where in {"x=0", "0"}:
                return bc.value.strip() or "h"
        return "h"

    # ===========================================================================
    # PASO 0
    # ===========================================================================

    def _step_statement(self, h_value: str) -> Step:
        latex = equation_chain(
            [
                r"&\text{EDP:} \quad u_t = \alpha^2\, u_{xx}, "
                r"\quad x > 0,\quad t > 0,",
                rf"&\text{{condición inicial:}} \quad u(x, 0) = 0,",
                rf"&\text{{frontera (pared):}} \quad u(0, t) = {h_value},",
                r"&\text{decaimiento al infinito:} \quad "
                r"u(x, t) \to 0 \text{ acotada cuando } x \to \infty.",
            ]
        )
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (barra semi-infinita)",
            md=T.T_statement_heat_halfline(),
            latex=latex,
            level="basic",
        )

    # ===========================================================================
    # PASO 1
    # ===========================================================================

    def _step_classification(self, alpha: sp.Symbol) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Clasificación (parabólica)",
            md=(
                "Misma EDP del calor que en los dominios acotado y "
                "no acotado: parabólica. Lo que cambia es la **geometría "
                "del dominio** y la **localización del dato no homogéneo** "
                "(la pared en $x = 0$), no la naturaleza matemática de "
                "la EDP."
            ),
            latex=(
                r"A = \alpha^2,\quad B = 0,\quad C = 0,\quad "
                r"\Delta = 0 \Rightarrow \text{parabólica}."
            ),
            level="basic",
        )

    # ===========================================================================
    # PASO 2
    # ===========================================================================

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método: transformada de Laplace en $t$",
            md=T.T_heat_halfline_method_choice(),
            latex=(
                r"\mathcal{L}[u](x, s) = U(x, s) = "
                r"\int_0^\infty e^{-st}\, u(x, t)\, dt,\qquad "
                r"\mathcal{L}[u_t] = s\, U - u(x, 0)."
            ),
            level="basic",
            observations=[obs.get("laplace_diagonalizes_dt")],
        )

    # ===========================================================================
    # PASO 3
    # ===========================================================================

    def _step_pde_to_ode(
        self, alpha: sp.Symbol, x: sp.Symbol, s: sp.Symbol
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3.1 — La EDP se transforma en EDO en $x$",
            md=T.T_heat_halfline_pde_to_ode(),
            latex=equation_chain(
                [
                    r"\mathcal{L}[u_t] &= s\, U(x, s) - u(x, 0) "
                    r"= s\, U(x, s) \quad (\text{usando } u(x, 0) = 0),",
                    r"\mathcal{L}[u_{xx}] &= U_{xx}(x, s),",
                    r"s\, U &= \alpha^2\, U_{xx} "
                    r"\quad \Longleftrightarrow \quad "
                    r"U_{xx} - \frac{s}{\alpha^2}\, U = 0.",
                ]
            ),
            level="basic",
        )

    def _step_solve_ode(
        self,
        alpha: sp.Symbol,
        x: sp.Symbol,
        s: sp.Symbol,
        h_sym: sp.Basic,
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3.2 — Solución de la EDO + condiciones de frontera",
            md=T.T_heat_halfline_solve_ode(),
            latex=equation_chain(
                [
                    r"U_{xx} - \tfrac{s}{\alpha^2}\, U &= 0 "
                    r"\Rightarrow U(x, s) = A(s) e^{-\sqrt{s}\, x/\alpha} "
                    r"+ B(s) e^{+\sqrt{s}\, x/\alpha},",
                    r"\text{acotada al } \infty &\Rightarrow B(s) = 0,",
                    rf"u(0, t) = {sp.latex(h_sym)} &\Rightarrow "
                    rf"U(0, s) = \frac{{{sp.latex(h_sym)}}}{{s}} "
                    rf"\Rightarrow A(s) = \frac{{{sp.latex(h_sym)}}}{{s}},",
                    rf"U(x, s) &= \frac{{{sp.latex(h_sym)}}}{{s}}\, "
                    r"e^{-\sqrt{s}\, x/\alpha}.",
                ]
            ),
            level="intermediate",
        )

    def _step_inverse(
        self, alpha: sp.Symbol, x: sp.Symbol, t: sp.Symbol
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3.3 — Transformada inversa: aparece $\\operatorname{erfc}$",
            md=T.T_heat_halfline_inverse(),
            latex=equation_chain(
                [
                    r"\mathcal{L}^{-1}\!\left[\tfrac{1}{s}\, "
                    r"e^{-a\sqrt{s}}\right](t) "
                    r"&= \operatorname{erfc}\!\left(\frac{a}{2\sqrt{t}}\right),"
                    r"\quad a > 0,",
                    r"a &= x/\alpha,",
                    r"u(x, t) &= h\, \operatorname{erfc}\!\left("
                    r"\frac{x}{2\alpha\sqrt{t}}\right).",
                ]
            ),
            level="intermediate",
            observations=[obs.get("erfc_inverse_laplace_pair")],
        )

    # ===========================================================================
    # PASO 4 — Boundary conditions (recap)
    # ===========================================================================

    def _step_bcs(self) -> Step:
        return step(
            kind="boundary",
            title="Paso 4 — Aplicación de las condiciones de frontera",
            md=(
                "Las dos condiciones de frontera entraron ya en el "
                "Paso 3.2:\n\n"
                "1. $u(x, t)$ acotada cuando $x \\to \\infty$ forzó "
                "$B(s) = 0$ — eliminando la solución exponencial creciente.\n"
                "2. $u(0, t) = h$, transformada al dominio de Laplace, "
                "dio $U(0, s) = h/s$, fijando $A(s) = h/s$.\n\n"
                "**Lección importante.** Una de las virtudes de la "
                "transformada es que **las condiciones de frontera se "
                "aplican en el dominio transformado**, donde la EDO "
                "tiene solución general explícita. Compara con SOV: allí "
                "las BCs se aplican sobre las autofunciones espaciales."
            ),
            latex=(
                r"B(s) = 0\ (\text{regularidad en } \infty),\qquad "
                r"A(s) = h/s\ (\text{BC en } x = 0)."
            ),
            level="basic",
        )

    # ===========================================================================
    # PASO 5 — Initial condition
    # ===========================================================================

    def _step_ic(self) -> Step:
        return step(
            kind="initial",
            title="Paso 5 — Condición inicial (absorbida por $\\mathcal{L}$)",
            md=(
                "A diferencia de SOV (donde la condición inicial fija "
                "los coeficientes $B_n$ por ortogonalidad) y de Fourier "
                "(donde aparece como $\\hat\\psi_0$ en el integrando), "
                "en Laplace la condición inicial **se incorpora "
                "automáticamente** vía la fórmula "
                "$\\mathcal{L}[u_t] = s\\, U(x, s) - u(x, 0)$.\n\n"
                "En nuestro caso $u(x, 0) = 0$, así que el término "
                "extra desaparece y la EDO transformada queda limpia. "
                "Si hubiéramos tenido $u(x, 0) = u_0(x)$, ese perfil "
                "habría aparecido como un término forzante en la EDO "
                "(un problema no homogéneo en $x$)."
            ),
            latex=(
                r"u(x, 0) = 0 \Rightarrow \mathcal{L}[u_t] = "
                r"s\, U(x, s)."
            ),
            level="basic",
        )

    # ===========================================================================
    # PASO 6 — Final formula
    # ===========================================================================

    def _step_final_formula(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Fórmula final (solución de Stokes)",
            md=T.T_heat_halfline_final_formula(),
            latex=rf"\boxed{{\; u(x, t) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
            observations=[obs.get("self_similar_diffusion_eta")],
        )

    # ===========================================================================
    # PASO 7 — Verification
    # ===========================================================================

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        alpha: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
        h_sym: sp.Basic,
    ) -> list[Step]:
        u_t = sp.diff(solution_expr, t)
        u_xx = sp.diff(solution_expr, x, 2)
        residual = sp.simplify(u_t - alpha**2 * u_xx)
        pde_ok = bool(residual == 0)

        # BC at x = 0: erfc(0) = 1.
        u_at_0 = sp.simplify(solution_expr.subs(x, 0))
        # IC at t = 0+: erfc(x/(2α√t)) → 0 as t → 0+ for any x > 0.
        u_as_t_to_0 = sp.simplify(sp.limit(solution_expr, t, 0, dir="+"))

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "Para una solución de forma cerrada en términos de "
                "$\\operatorname{erfc}$ podemos verificar la EDP "
                "**directamente** derivando dos veces respecto a $x$ y "
                "una vez respecto a $t$. Las identidades de la función "
                "error hacen que los términos se cancelen exactamente."
            ),
            level="basic",
        )
        s_pde = step(
            kind="verification",
            title="Verificación de la EDP $u_t = \\alpha^2 u_{xx}$",
            md=(
                "Diferenciando y simplificando:"
                if pde_ok
                else "**Atención:** el residuo no se simplificó a cero."
            ),
            latex=equation_chain(
                [
                    rf"u_t &= {sp.latex(sp.simplify(u_t))},",
                    rf"u_{{xx}} &= {sp.latex(sp.simplify(u_xx))},",
                    rf"u_t - \alpha^2 u_{{xx}} &= {sp.latex(residual)}.",
                ]
            ),
            level="intermediate",
        )
        s_bc = step(
            kind="verification",
            title=r"Verificación de $u(0, t) = h$",
            md=(
                "Usamos $\\operatorname{erfc}(0) = 1$:"
            ),
            latex=(
                rf"u(0, t) = {sp.latex(h_sym)}\, \operatorname{{erfc}}(0) "
                rf"= {sp.latex(u_at_0)}\, \overset{{!}}{{=}}\, "
                rf"{sp.latex(h_sym)}."
            ),
            level="intermediate",
        )
        s_ic = step(
            kind="verification",
            title=r"Verificación de $u(x, 0^+) = 0$",
            md=(
                "Cuando $t \\to 0^+$, el argumento "
                "$x/(2\\alpha\\sqrt{t}) \\to +\\infty$, y "
                "$\\operatorname{erfc}(z) \\to 0$ cuando $z \\to +\\infty$:"
            ),
            latex=(
                rf"\lim_{{t \to 0^+}} u(x, t) = "
                rf"{sp.latex(h_sym)}\, \lim_{{t \to 0^+}} "
                r"\operatorname{erfc}\!\left(\tfrac{x}{2\alpha\sqrt{t}}\right) "
                rf"= {sp.latex(u_as_t_to_0)}."
            ),
            level="intermediate",
        )
        return [s_intro, s_pde, s_bc, s_ic]

    # ===========================================================================
    # PASOS 8 y 9
    # ===========================================================================

    def _step_visualization(self) -> Step:
        return step(
            kind="visualization",
            title="Paso 8 — Visualización",
            md=(
                "La superficie muestra $u(x, t)$ con $\\alpha = h = 1$. "
                "Observaciones:\n\n"
                "- En $x = 0$ la temperatura está pegada al valor de "
                "frontera $h$ para **todo** $t > 0$.\n"
                "- A profundidad fija $x$, $u$ crece monótonamente de "
                "$0$ a $h$ cuando $t$ crece.\n"
                "- A tiempo fijo $t$, $u$ decae de $h$ en la pared hasta "
                "$0$ en la profundidad — la transición se hace en una "
                "escala $\\delta(t) = 2\\alpha\\sqrt{t}$.\n"
                "- Los perfiles a distintos tiempos son **versiones "
                "reescaladas del mismo** (autosimilaridad en $\\eta$)."
            ),
            level="basic",
            observations=[obs.get("diffusion_length_sqrt_t")],
        )

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_heat_halfline_physical_interpretation(),
            level="basic",
            observations=[
                obs.get("diffusion_length_sqrt_t"),
                obs.get("self_similar_diffusion_eta"),
            ],
        )
