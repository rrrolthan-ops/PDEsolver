"""Heat equation with source f(x, t) on the real line — Duhamel's principle.

Problem covered
---------------
    u_t = α² u_xx + f(x, t)       x ∈ ℝ,   t > 0
    u(x, 0) = u_0(x)

Solution by Duhamel's principle
-------------------------------
Linearity decomposes the problem as

    u = u_hom + u_forc,

where

    u_hom(x, t)  = ∫_ℝ G(x - y, t) u_0(y) dy                    (Fourier)
    u_forc(x, t) = ∫_0^t ∫_ℝ G(x - y, t - s) f(y, s) dy ds      (Duhamel)

and G is the Gaussian heat kernel,

    G(x, t) = (4π α² t)^{-1/2} exp(-x² / (4 α² t)).

Why this method belongs in the curriculum
-----------------------------------------
Duhamel is the "abstract" version of Green's-function reasoning for
evolution PDEs: write the inhomogeneous solution as the action of the
homogeneous semigroup on the source, integrated against past time.
The same construction works for the wave equation, Schrödinger, the
transport equation, etc. Here we exhibit it in the cleanest possible
setting — heat on the real line — using the fundamental solution we
already built for `fourier_heat_line`.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class DuhamelHeat(Method):
    """Duhamel's principle for the heat equation with a source on the line."""

    slug = "duhamel_heat"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        y = sp.Symbol("y", real=True)
        s_var = sp.Symbol("s", real=True, nonnegative=True)
        alpha = sp.Symbol("alpha", positive=True)

        # ---------- Parse u_0(x) and f(x, t) --------------------------------
        u0_latex = "0"
        for ic in problem.initial_conditions:
            if ic.order == 0:
                u0_latex = ic.value
                break
        u0_expr = parse_scalar_latex(u0_latex, problem.parameters).subs(
            sp.Symbol("x"), x
        )

        f_latex = problem.source_term or "0"
        f_expr = parse_scalar_latex(f_latex, problem.parameters)
        # The source may depend on x and/or t; subs them to be safe.
        f_expr = f_expr.subs(sp.Symbol("x"), x).subs(sp.Symbol("t"), t)

        steps: list[Step] = []

        # ===== PASO 0 — Statement =============================================
        steps.append(self._step_statement(u0_latex, f_latex))

        # ===== PASO 1 — Classification ========================================
        steps.append(self._step_classification(alpha))

        # ===== PASO 2 — Method choice =========================================
        steps.append(self._step_method_choice())

        # ===== PASO 3 — Decomposition ========================================
        steps.append(self._step_decomposition())

        # ===== PASO 4 — Homogeneous part (Fourier on the line) ==============
        steps.append(self._step_homogeneous(alpha, x, t, y))

        # ===== PASO 5 — Duhamel integral for the forcing =====================
        steps.append(self._step_duhamel_integral(alpha, x, t, y, s_var))

        # ===== PASO 6 — Final combined formula ===============================
        solution_expr = self._build_solution_expression(
            u0_expr, f_expr, alpha, x, t, y, s_var
        )
        steps.append(self._step_final_formula(solution_expr))

        # ===== PASO 7 — Verification (operator-level) =======================
        steps += self._steps_verification(alpha, x, t)

        # ===== PASO 8 — Visualization =========================================
        steps.append(self._step_visualization(f_latex, u0_latex))

        # ===== PASO 9 — Physical interpretation ==============================
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # ===========================================================================
    # PASO 0
    # ===========================================================================

    def _step_statement(self, u0_latex: str, f_latex: str) -> Step:
        latex = equation_chain(
            [
                r"&\text{EDP:} \quad u_t = \alpha^2\, u_{xx} + f(x, t), "
                r"\quad x \in \mathbb{R},\quad t > 0,",
                rf"&\text{{fuente:}} \quad f(x, t) = {f_latex},",
                rf"&\text{{condición inicial:}} \quad u(x, 0) = {u0_latex}.",
            ]
        )
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (calor inhomogéneo en la recta)",
            md=T.T_statement_duhamel(),
            latex=latex,
            level="basic",
        )

    # ===========================================================================
    # PASO 1
    # ===========================================================================

    def _step_classification(self, alpha: sp.Symbol) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Clasificación (parabólica, lineal, inhomogénea)",
            md=(
                "Mismo operador que el calor homogéneo — parabólico — "
                "pero ahora con un **término fuente**. La EDP sigue "
                "siendo lineal: si $u_1$ resuelve con CI $u_{0,1}$ y "
                "fuente $f_1$, y $u_2$ con CI $u_{0,2}$ y fuente "
                "$f_2$, entonces $u_1 + u_2$ resuelve con CI "
                "$u_{0,1} + u_{0,2}$ y fuente $f_1 + f_2$. Esta "
                "**linealidad** es el motor del principio de Duhamel."
            ),
            latex=(
                r"u_t - \alpha^2 u_{xx} = f(x, t) "
                r"\quad \Rightarrow \quad \text{parabólica lineal "
                r"inhomogénea.}"
            ),
            level="basic",
        )

    # ===========================================================================
    # PASO 2
    # ===========================================================================

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método: principio de Duhamel",
            md=T.T_duhamel_method_choice(),
            latex=(
                r"u = u_{\text{hom}} + u_{\text{forz}}, \qquad "
                r"u_{\text{hom}} \text{ resuelve la EDP homogénea con "
                r"el dato inicial};\ "
                r"u_{\text{forz}} \text{ resuelve la EDP inhomogénea "
                r"con dato inicial cero.}"
            ),
            level="basic",
            observations=[obs.get("duhamel_superposition")],
        )

    # ===========================================================================
    # PASO 3
    # ===========================================================================

    def _step_decomposition(self) -> Step:
        return step(
            kind="development",
            title="Paso 3 — Descomposición $u = u_{\\text{hom}} + u_{\\text{forz}}$",
            md=(
                "Por linealidad, basta resolver dos subproblemas y "
                "sumar sus soluciones:"
            ),
            latex=equation_chain(
                [
                    r"u_{\text{hom}}:&\ "
                    r"\partial_t u_{\text{hom}} = \alpha^2 \partial_x^2 u_{\text{hom}},"
                    r"\quad u_{\text{hom}}(x, 0) = u_0(x),",
                    r"u_{\text{forz}}:&\ "
                    r"\partial_t u_{\text{forz}} = \alpha^2 \partial_x^2 u_{\text{forz}} + f(x, t),"
                    r"\quad u_{\text{forz}}(x, 0) = 0.",
                ]
            ),
            level="basic",
        )

    # ===========================================================================
    # PASO 4 — Homogeneous part
    # ===========================================================================

    def _step_homogeneous(
        self, alpha: sp.Symbol, x: sp.Symbol, t: sp.Symbol, y: sp.Symbol
    ) -> Step:
        return step(
            kind="development",
            title="Paso 4 — Parte homogénea (Fourier en $x$)",
            md=(
                "Ya conocemos esta solución del método **Fourier en la "
                "recta**: convolución del dato inicial con el núcleo de "
                "Gauss."
            ),
            latex=equation_chain(
                [
                    r"G(x, t) &= \frac{1}{\sqrt{4\pi \alpha^2 t}}\, "
                    r"\exp\!\left(-\frac{x^2}{4\alpha^2 t}\right),",
                    r"u_{\text{hom}}(x, t) &= \int_{-\infty}^{\infty} "
                    r"G(x - y, t)\, u_0(y)\, dy.",
                ]
            ),
            level="intermediate",
        )

    # ===========================================================================
    # PASO 5 — Duhamel integral
    # ===========================================================================

    def _step_duhamel_integral(
        self,
        alpha: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
        y: sp.Symbol,
        s_var: sp.Symbol,
    ) -> Step:
        return step(
            kind="development",
            title="Paso 5 — Integral de Duhamel para la fuente",
            md=(
                "Para el subproblema con fuente y dato inicial cero, "
                "imaginamos $f$ como una **superposición de pulsos "
                "instantáneos**: en el tiempo $s$, una distribución "
                "espacial $f(y, s)$ \"actúa\" y luego evoluciona como "
                "el calor con dato inicial $f(\\cdot, s)$ durante un "
                "tiempo $t - s$. Sumando (integrando) sobre todos los "
                "instantes $s \\in [0, t]$:"
            ),
            latex=equation_chain(
                [
                    r"u_{\text{forz}}(x, t) &= "
                    r"\int_0^t \!\!\int_{-\infty}^{\infty} "
                    r"G(x - y, t - s)\, f(y, s)\, dy\, ds.",
                ]
            ),
            level="intermediate",
            observations=[obs.get("duhamel_causality")],
        )

    # ===========================================================================
    # PASO 6 — Final formula
    # ===========================================================================

    def _build_solution_expression(
        self,
        u0_expr: sp.Basic,
        f_expr: sp.Basic,
        alpha: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
        y: sp.Symbol,
        s_var: sp.Symbol,
    ) -> sp.Basic:
        # Build the two convolutions symbolically. We keep them as
        # unevaluated Integrals — they're the textbook form, and
        # SymPy struggles to close them in closed form except in
        # nice special cases.
        G_homog = sp.exp(-((x - y) ** 2) / (4 * alpha**2 * t)) / sp.sqrt(
            4 * sp.pi * alpha**2 * t
        )
        u_hom = sp.Integral(
            G_homog * u0_expr.subs(x, y), (y, -sp.oo, sp.oo)
        )

        f_of_ys = f_expr.subs({x: y, t: s_var})
        G_kernel = sp.exp(-((x - y) ** 2) / (4 * alpha**2 * (t - s_var))) / sp.sqrt(
            4 * sp.pi * alpha**2 * (t - s_var)
        )
        u_forc = sp.Integral(
            G_kernel * f_of_ys,
            (y, -sp.oo, sp.oo),
            (s_var, 0, t),
        )

        # Drop the homogeneous part if u_0 = 0 (cleaner display).
        if u0_expr == 0:
            return u_forc
        # Drop the forcing if f = 0 (degenerate but possible).
        if f_expr == 0:
            return u_hom
        return u_hom + u_forc

    def _step_final_formula(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Fórmula final (Duhamel)",
            md=T.T_duhamel_formula(),
            latex=rf"\boxed{{\; u(x, t) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    # ===========================================================================
    # PASO 7 — Verification (operator-level)
    # ===========================================================================

    def _steps_verification(
        self,
        alpha: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
    ) -> list[Step]:
        # We verify at the operator level: the heat kernel satisfies
        # G_t = α² G_xx, so the homogeneous part of u solves the
        # homogeneous PDE; the Duhamel part has u_forc(x, 0) = 0 (the
        # integral is empty) and, applying ∂_t - α²∂_xx, recovers
        # exactly f(x, t) via the Leibniz integral rule and the delta
        # limit of G as t → 0+.
        G = sp.exp(-(x**2) / (4 * alpha**2 * t)) / sp.sqrt(
            4 * sp.pi * alpha**2 * t
        )
        residual = sp.simplify(sp.diff(G, t) - alpha**2 * sp.diff(G, x, 2))
        kernel_ok = residual == 0

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "**Estructura del argumento.** Por linealidad y por la "
                "regla de Leibniz aplicada a las integrales de "
                "convolución:\n\n"
                "1. $u_{\\text{hom}}$ satisface la EDP homogénea — lo "
                "hereda directamente de $G$.\n"
                "2. $u_{\\text{forz}}$ tiene $u_{\\text{forz}}(x, 0) = 0$ "
                "(la integral es vacía).\n"
                "3. Aplicando $\\partial_t - \\alpha^2 \\partial_x^2$ a "
                "$u_{\\text{forz}}$, la frontera $s = t$ del integral "
                "contribuye $f(x, t)$ (límite delta de $G$ cuando "
                "$t - s \\to 0^+$), y el bulk se anula por "
                "$G_t = \\alpha^2 G_{xx}$.\n\n"
                "Comprobamos en primer lugar la identidad sobre el "
                "núcleo:"
            ),
            level="basic",
        )
        s_kernel = step(
            kind="verification",
            title=r"Verificación del núcleo: $G_t = \alpha^2 G_{xx}$",
            md=(
                "Diferenciando $G$ explícitamente (igual que en el "
                "método homogéneo, ahora reutilizado para la integral "
                "de Duhamel):"
            )
            if kernel_ok
            else "**Atención:** el residuo no se simplificó a cero.",
            latex=rf"G_t - \alpha^2 G_{{xx}} = {sp.latex(residual)}.",
            level="intermediate",
        )
        s_duhamel_check = step(
            kind="verification",
            title="Verificación de la fórmula de Duhamel (vía Leibniz)",
            md=(
                "Aplicamos el operador del calor a $u_{\\text{forz}}$ "
                "usando la regla de Leibniz para derivar dentro del "
                "integral en $s$ y sacar la frontera $s = t$:"
            ),
            latex=equation_chain(
                [
                    r"\partial_t u_{\text{forz}}(x, t) "
                    r"&= \lim_{s \to t^-} \int_{\mathbb{R}} G(x - y, t - s) f(y, s) dy "
                    r"+ \int_0^t \!\!\int_{\mathbb{R}} G_t(x - y, t - s) f(y, s) dy ds,",
                    r"&= f(x, t) + \alpha^2 \int_0^t \!\!\int_{\mathbb{R}} "
                    r"G_{xx}(x - y, t - s) f(y, s) dy ds",
                    r"&\quad (\text{usando } G_t = \alpha^2 G_{xx} "
                    r"\text{ y } G(\cdot, 0^+) = \delta),",
                    r"\Rightarrow\quad \partial_t u_{\text{forz}} "
                    r"- \alpha^2 \partial_x^2 u_{\text{forz}} &= f(x, t).\qquad\blacksquare",
                ]
            ),
            level="exhaustive",
        )
        return [s_intro, s_kernel, s_duhamel_check]

    # ===========================================================================
    # PASO 8 — Visualization
    # ===========================================================================

    def _step_visualization(self, f_latex: str, u0_latex: str) -> Step:
        return step(
            kind="visualization",
            title="Paso 8 — Visualización",
            md=(
                f"La superficie muestra $u(x, t)$ resultado de la "
                f"superposición del transporte del dato inicial "
                f"$u_0(x) = {u0_latex}$ con la integral de la fuente "
                f"$f(x, t) = {f_latex}$ contra el núcleo de Gauss.\n\n"
                "**Lo que esperarías ver:**\n\n"
                "- Si $u_0 = 0$ y $f$ es localizada en el origen, $u$ "
                "**crece** desde cero a medida que la fuente \"deposita\" "
                "calor, y luego ese calor se difunde.\n"
                "- Si $f$ tiene signo definido positivo, $u \\to +\\infty$ "
                "para tiempos largos (a menos que la fuente esté "
                "espacialmente integrable y decrezca con $t$).\n"
                "- El **núcleo gaussiano** acota la velocidad efectiva "
                "de respuesta: aunque formalmente infinita, los efectos "
                "son apreciables sólo dentro de la \"longitud de "
                "difusión\" $\\delta(t-s) = 2\\alpha\\sqrt{t-s}$ "
                "alrededor de cada fuente."
            ),
            level="basic",
        )

    # ===========================================================================
    # PASO 9 — Physical interpretation
    # ===========================================================================

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_duhamel_intuition(),
            level="basic",
            observations=[obs.get("duhamel_causality")],
        )
