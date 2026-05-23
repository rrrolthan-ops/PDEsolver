"""Separation of variables for the 1D wave equation on a bounded interval.

Problem covered
---------------
    u_tt = c^2 u_xx               in 0 < x < L,  t > 0
    u(0, t) = u(L, t) = 0          (Dirichlet, homogeneous)
    u(x, 0) = f(x)                 (initial position)
    u_t(x, 0) = g(x)               (initial velocity)

Differences from the heat case (and what the pedagogy emphasises)
-----------------------------------------------------------------
1. Time enters squared. The temporal ODE is second-order, so each mode
   has TWO temporal degrees of freedom (cos and sin), not one.
2. We need TWO initial conditions to fix them: the position f and the
   velocity g.
3. No dissipation. Modes oscillate forever; energy is conserved.
4. The frequencies form an arithmetic progression (harmonic series),
   which is why strings sound "musical".
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class SeparationOfVariablesWave1D(Method):
    """Separation of variables for the wave equation on [0, L] with Dirichlet 0."""

    slug = "sov_wave_1d"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        # ---------- Symbols ----------------------------------------------------
        x = sp.Symbol("x", real=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        L = sp.Symbol("L", positive=True)
        c = sp.Symbol("c", positive=True)

        # ---------- Parse f and g ---------------------------------------------
        # Wave problems carry two ICs: order=0 (position) and order=1 (velocity).
        # We accept the problem with either or both present; missing g defaults
        # to zero (the "plucked string at rest" classic).
        f_latex = "0"
        g_latex = "0"
        for ic in problem.initial_conditions:
            if ic.order == 0:
                f_latex = ic.value
            elif ic.order == 1:
                g_latex = ic.value
        f_expr = parse_scalar_latex(f_latex, problem.parameters).subs(
            {sp.Symbol("x"): x, sp.Symbol("L"): L}
        )
        g_expr = parse_scalar_latex(g_latex, problem.parameters).subs(
            {sp.Symbol("x"): x, sp.Symbol("L"): L}
        )

        steps: list[Step] = []

        # ===== PASO 0 — Statement =============================================
        steps.append(self._step_statement(f_latex, g_latex))

        # ===== PASO 1 — Classification ========================================
        steps += self._steps_classification(c)

        # ===== PASO 2 — Method choice =========================================
        steps += self._steps_method_choice()

        # ===== PASO 3 — Development ==========================================
        steps += self._steps_separation(c, x, t)
        steps += self._steps_three_cases(L)
        steps += self._steps_temporal_ode(c, L)
        steps += self._steps_superposition(c, L)

        # ===== PASO 5 — Apply ICs to get An and Bn ===========================
        An_expr, Bn_expr = self._steps_two_fourier_coefficients(
            steps, f_expr, g_expr, f_latex, g_latex, c, L, x
        )

        # ===== PASO 6 — Final solution =======================================
        solution_expr = self._build_solution_expression(
            An_expr, Bn_expr, x, t, L, c
        )
        steps.append(self._step_final_solution(solution_expr))

        # ===== PASO 7 — Verification =========================================
        steps += self._steps_verification(
            solution_expr, f_expr, g_expr, c, x, t, L
        )

        # ===== PASO 8 — Visualization ========================================
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
                r"\qquad 0 < x < L,\quad t > 0,",
                r"&\text{contorno:} \quad u(0, t) = 0,\quad u(L, t) = 0,",
                rf"&\text{{posición inicial:}} \quad u(x, 0) = {f_latex},",
                rf"&\text{{velocidad inicial:}} \quad u_t(x, 0) = {g_latex}.",
            ]
        )
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento del problema",
            md=T.T_statement_wave(),
            latex=latex,
            level="basic",
            observations=[obs.get("wave_needs_two_ics")],
        )

    # ===========================================================================
    # PASO 1
    # ===========================================================================

    def _steps_classification(self, c: sp.Symbol) -> list[Step]:
        # Writing the PDE as c^2 u_xx − u_tt = 0:
        #   A = c^2  (coef of u_xx)
        #   C = -1   (coef of u_tt)
        #   B = 0
        # Δ = B^2 - 4AC = 0 - 4 · c^2 · (-1) = 4 c^2 > 0 → hyperbolic.
        A, B, C = c**2, sp.Integer(0), sp.Integer(-1)
        disc = sp.simplify(B**2 - 4 * A * C)

        s1 = step(
            kind="classification",
            title="Paso 1 — Clasificación de la EDP",
            md=T.T_classification_intro(),
            latex=equation_chain(
                [
                    r"&c^2\, u_{xx} - u_{tt} = 0,",
                    rf"&A = {sp.latex(A)}, \quad B = {sp.latex(B)}, "
                    rf"\quad C = {sp.latex(C)},",
                    rf"&\Delta = B^2 - 4AC = {sp.latex(disc)} > 0.",
                ]
            ),
            level="basic",
        )
        s2 = step(
            kind="classification",
            title="Conclusión: hiperbólica",
            md=(
                "Como $\\Delta > 0$, la EDP es **hiperbólica**. Las "
                "hiperbólicas son ecuaciones de **propagación**: la "
                "información se mueve a lo largo de curvas características "
                "(que veremos en detalle si elegimos el método de "
                "D'Alembert). Hay dos direcciones temporales equivalentes "
                "—esto es lo que distingue cualitativamente la onda del "
                "calor."
            ),
            level="basic",
        )
        return [s1, s2]

    # ===========================================================================
    # PASO 2
    # ===========================================================================

    def _steps_method_choice(self) -> list[Step]:
        s_main = step(
            kind="method_choice",
            title="Paso 2 — Método: separación de variables",
            md=(
                "Mismas razones que en el caso del calor: la EDP es "
                "**lineal y homogénea**, el dominio espacial es un "
                "intervalo finito $[0, L]$, y las condiciones de contorno "
                "son **homogéneas**. Estas tres propiedades juntas hacen "
                "que el método produzca un problema de Sturm-Liouville "
                "discreto con autofunciones que forman base ortogonal."
            ),
            level="basic",
        )
        s_alt = step(
            kind="method_choice",
            title="Alternativa: D'Alembert",
            md=(
                "Para la **ecuación de onda 1D** existe un método alternativo "
                "extremadamente elegante: la **fórmula de D'Alembert**. "
                "Funciona directamente en el dominio infinito y, usando "
                "extensiones periódicas, también en intervalos finitos. "
                "Las dos soluciones son matemáticamente equivalentes; "
                "la serie de Fourier resalta los **modos normales** "
                "(buen lenguaje para acústica), mientras que D'Alembert "
                "resalta las **ondas viajeras** (buen lenguaje para "
                "causalidad relativista)."
            ),
            level="intermediate",
        )
        return [s_main, s_alt]

    # ===========================================================================
    # PASO 3
    # ===========================================================================

    def _steps_separation(
        self, c: sp.Symbol, x: sp.Symbol, t: sp.Symbol
    ) -> list[Step]:
        X = sp.Function("X")
        Tt = sp.Function("T")
        ansatz = X(x) * Tt(t)
        u_tt = sp.diff(ansatz, t, 2)
        u_xx = sp.diff(ansatz, x, 2)

        s_ansatz = step(
            kind="development",
            title="Paso 3.1 — Ansatz separable",
            md=T.T_sov_ansatz(),
            latex=r"u(x, t) = X(x)\, T(t).",
            level="basic",
            observations=[obs.get("sov_why_separable")],
        )
        s_subs = step(
            kind="development",
            title="Paso 3.2 — Sustituimos en la EDP",
            md="Calculamos las dos derivadas segundas y llevamos a la EDP.",
            latex=equation_chain(
                [
                    rf"u_{{tt}} &= {sp.latex(u_tt)},",
                    rf"u_{{xx}} &= {sp.latex(u_xx)},",
                    r"X(x)\, T''(t) &= c^2\, X''(x)\, T(t).",
                ]
            ),
            level="basic",
        )
        s_divide = step(
            kind="development",
            title="Paso 3.3 — Dividimos por $c^2\\, X(x)\\, T(t)$",
            md=(
                "Como antes, separamos las dependencias en variables "
                "distintas a cada lado de la igualdad:"
            ),
            latex=r"\frac{T''(t)}{c^2\, T(t)} = \frac{X''(x)}{X(x)}.",
            level="basic",
        )
        s_constant = step(
            kind="development",
            title="Paso 3.4 — Constante de separación",
            md=T.T_sov_constant_separation(),
            latex=equation_chain(
                [
                    r"\frac{T''(t)}{c^2\, T(t)} = \frac{X''(x)}{X(x)} &= -\lambda,",
                    r"T''(t) + c^2 \lambda\, T(t) &= 0,",
                    r"X''(x) + \lambda\, X(x) &= 0.",
                ]
            ),
            level="basic",
            observations=[obs.get("sov_sign_convention")],
        )
        return [s_ansatz, s_subs, s_divide, s_constant]

    def _steps_three_cases(self, L: sp.Symbol) -> list[Step]:
        """Spatial three-cases analysis — identical to the heat case."""
        # We reuse the same prose templates because the SPATIAL ODE is
        # the same; only the temporal ODE differs in the wave case.
        s_intro = step(
            kind="development",
            title="Paso 3.5 — Examen de los tres casos en $\\lambda$",
            md=T.T_sov_three_cases_intro(),
            level="basic",
            observations=[obs.get("sov_why_three_cases")],
        )
        s_neg = step(
            kind="development",
            title="Caso 1: $\\lambda < 0$",
            md=T.T_sov_case_lambda_negative(),
            latex=equation_chain(
                [
                    r"\lambda = -\mu^2, \quad \mu > 0,",
                    r"X(x) = A\, e^{\mu x} + B\, e^{-\mu x}.",
                ]
            ),
            level="basic",
        )
        s_neg_bc = step(
            kind="development",
            title="…descartado por las condiciones de contorno",
            md=T.T_sov_case_lambda_negative_discard(),
            latex=r"X(0) = X(L) = 0 \Rightarrow A = B = 0 \Rightarrow X \equiv 0.",
            level="intermediate",
        )
        s_zero = step(
            kind="development",
            title="Caso 2: $\\lambda = 0$",
            md=T.T_sov_case_lambda_zero(),
            latex=r"X(x) = A x + B \Rightarrow A = B = 0 \Rightarrow X \equiv 0.",
            level="intermediate",
        )
        s_pos = step(
            kind="development",
            title="Caso 3: $\\lambda > 0$ (el productivo)",
            md=T.T_sov_case_lambda_positive(),
            latex=equation_chain(
                [
                    r"\lambda = \mu^2,\quad \mu > 0,",
                    r"X(x) = A \cos(\mu x) + B \sin(\mu x).",
                ]
            ),
            level="basic",
        )
        s_eigen = step(
            kind="boundary",
            title="Paso 4 — Autovalores y autofunciones",
            md=T.T_sov_eigenvalues(),
            latex=equation_chain(
                [
                    r"X(0) = 0 &\Rightarrow A = 0,",
                    r"X(L) = 0 &\Rightarrow \sin(\mu L) = 0 \Rightarrow \mu L = n\pi,",
                    r"\boxed{\;\lambda_n = (n\pi/L)^2,\quad X_n(x) = \sin(n\pi x/L).\;}",
                ]
            ),
            level="basic",
            observations=[obs.get("sturm_liouville_theorem")],
        )
        return [s_intro, s_neg, s_neg_bc, s_zero, s_pos, s_eigen]

    def _steps_temporal_ode(self, c: sp.Symbol, L: sp.Symbol) -> list[Step]:
        s = step(
            kind="development",
            title="Paso 3.6 — Resolución de la EDO temporal (segundo orden)",
            md=T.T_wave_temporal_ode(),
            latex=equation_chain(
                [
                    r"T_n'' + c^2 \lambda_n\, T_n &= 0,",
                    r"&\text{característica: } r^2 + c^2 \lambda_n = 0,",
                    r"&r = \pm i\, c\, \mu_n = \pm i\, c\, n\pi/L,",
                    r"T_n(t) &= A_n \cos\!\bigl(\tfrac{c n\pi}{L}\, t\bigr) "
                    r"+ B_n \sin\!\bigl(\tfrac{c n\pi}{L}\, t\bigr).",
                ]
            ),
            level="basic",
            observations=[obs.get("wave_harmonic_frequencies"), obs.get("wave_no_dissipation")],
        )
        return [s]

    def _steps_superposition(self, c: sp.Symbol, L: sp.Symbol) -> list[Step]:
        s = step(
            kind="development",
            title="Paso 3.7 — Superposición",
            md=(
                "Cada producto $X_n(x) T_n(t)$ es solución. La superposición "
                "de **todos** los modos da la solución general:"
            ),
            latex=(
                r"u(x, t) = \sum_{n=1}^{\infty} "
                r"\bigl[A_n \cos\!\bigl(\tfrac{c n\pi t}{L}\bigr) "
                r"+ B_n \sin\!\bigl(\tfrac{c n\pi t}{L}\bigr)\bigr]\, "
                r"\sin\!\bigl(\tfrac{n\pi x}{L}\bigr)."
            ),
            level="basic",
        )
        return [s]

    # ===========================================================================
    # PASO 5 — Two families of Fourier coefficients
    # ===========================================================================

    def _steps_two_fourier_coefficients(
        self,
        steps: list[Step],
        f_expr: sp.Basic,
        g_expr: sp.Basic,
        f_latex: str,
        g_latex: str,
        c: sp.Symbol,
        L: sp.Symbol,
        x: sp.Symbol,
    ) -> tuple[sp.Basic, sp.Basic]:
        n = sp.Symbol("n", integer=True, positive=True)

        steps.append(
            step(
                kind="initial",
                title="Paso 5 — Aplicación de las dos condiciones iniciales",
                md=T.T_wave_two_ics(),
                level="basic",
                observations=[obs.get("fourier_orthogonality")],
            )
        )

        # ----- An from u(x, 0) = f(x) ---------------------------------------
        steps.append(
            step(
                kind="initial",
                title="Paso 5.1 — Coeficientes $A_n$ (de la posición inicial)",
                md=(
                    "En $t = 0$, $\\cos(0) = 1$ y $\\sin(0) = 0$, así que la "
                    "serie se reduce a $\\sum A_n \\sin(n\\pi x/L) = f(x)$. "
                    "Aplicando ortogonalidad obtenemos:"
                ),
                latex=(
                    rf"A_n = \frac{{2}}{{L}} \int_0^L {sp.latex(f_expr)}"
                    r"\, \sin\!\bigl(\tfrac{n\pi x}{L}\bigr)\, dx."
                ),
                level="basic",
            )
        )

        An = sp.Rational(2) / L * sp.integrate(
            f_expr * sp.sin(n * sp.pi * x / L), (x, 0, L)
        )
        An = sp.simplify(An.subs(sp.cos(sp.pi * n), (-1) ** n))

        steps.append(
            step(
                kind="initial",
                title="Resultado de la integral para $A_n$",
                md="Integramos simbólicamente:",
                latex=rf"A_n = {sp.latex(An)}.",
                sympy_expr=An,
                level="basic",
            )
        )

        # ----- Bn from u_t(x, 0) = g(x) --------------------------------------
        steps.append(
            step(
                kind="initial",
                title="Paso 5.2 — Coeficientes $B_n$ (de la velocidad inicial)",
                md=(
                    "Derivando la serie respecto a $t$ y evaluando en $t = 0$: "
                    "los términos con $\\cos$ se anulan al diferenciar (se "
                    "vuelven $-\\sin$), y los $\\sin$ se vuelven $\\cos$ con "
                    "factor $c n\\pi/L$. Queda:\n\n"
                    "$$g(x) = \\sum_{n=1}^{\\infty} B_n\\, \\tfrac{c n \\pi}{L}\\, "
                    "\\sin\\!\\bigl(\\tfrac{n\\pi x}{L}\\bigr).$$\n\n"
                    "Aplicando ortogonalidad, **con un factor adicional** "
                    "$1/(c n\\pi/L) = L/(c n\\pi)$:"
                ),
                latex=(
                    rf"B_n = \frac{{2}}{{c n \pi}} \int_0^L {sp.latex(g_expr)}"
                    r"\, \sin\!\bigl(\tfrac{n\pi x}{L}\bigr)\, dx."
                ),
                level="basic",
            )
        )

        Bn_integral = sp.integrate(g_expr * sp.sin(n * sp.pi * x / L), (x, 0, L))
        Bn = sp.simplify(
            sp.Rational(2) / (c * n * sp.pi) * Bn_integral
        )
        Bn = sp.simplify(Bn.subs(sp.cos(sp.pi * n), (-1) ** n))

        steps.append(
            step(
                kind="initial",
                title="Resultado de la integral para $B_n$",
                md="Integrando:",
                latex=rf"B_n = {sp.latex(Bn)}.",
                sympy_expr=Bn,
                level="basic",
            )
        )

        return An, Bn

    # ===========================================================================
    # Build solution expression
    # ===========================================================================

    def _build_solution_expression(
        self,
        An: sp.Basic,
        Bn: sp.Basic,
        x: sp.Symbol,
        t: sp.Symbol,
        L: sp.Symbol,
        c: sp.Symbol,
    ) -> sp.Basic:
        n = sp.Symbol("n", integer=True, positive=True)
        omega = c * n * sp.pi / L
        spatial = sp.sin(n * sp.pi * x / L)
        temporal = An * sp.cos(omega * t) + Bn * sp.sin(omega * t)
        return sp.Sum(temporal * spatial, (n, 1, sp.oo))

    def _step_final_solution(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Solución",
            md=(
                "Sustituyendo $A_n$ y $B_n$ en la superposición, "
                "obtenemos la solución del problema:"
            ),
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
        f_expr: sp.Basic,
        g_expr: sp.Basic,
        c: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
        L: sp.Symbol,
    ) -> list[Step]:
        # Verify by computing u_tt - c^2 u_xx for the generic term.
        term = solution_expr.function if isinstance(solution_expr, sp.Sum) else solution_expr
        u_tt = sp.diff(term, t, 2)
        u_xx = sp.diff(term, x, 2)
        residual = sp.simplify(u_tt - c**2 * u_xx)
        pde_ok = bool(residual == 0)

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=T.T_verification_intro(),
            level="basic",
        )
        s_pde = step(
            kind="verification",
            title="Verificación de la EDP",
            md=(
                "Sustituimos el término genérico en $u_{tt} - c^2 u_{xx}$. "
                "Si el residuo es cero, la **superposición** también "
                "satisface la EDP (cada término por separado lo hace)."
                if pde_ok
                else "**Atención:** el residuo simbólico no se anuló."
            ),
            latex=(
                r"\begin{aligned}"
                rf"u_{{n,tt}} - c^2\, u_{{n,xx}} = {sp.latex(residual)}."
                r"\end{aligned}"
            ),
            level="intermediate",
        )

        bc0 = sp.simplify(term.subs(x, 0))
        bcL = sp.simplify(term.subs(x, L))
        s_bc = step(
            kind="verification",
            title="Verificación de las condiciones de contorno",
            md=(
                "Por construcción, $X_n(x) = \\sin(n\\pi x/L)$ se anula "
                "en $x = 0$ y $x = L$. La cuerda permanece fija en sus "
                "extremos para todo $t$."
            ),
            latex=(
                r"\begin{aligned}"
                rf"u_n(0, t) &= {sp.latex(bc0)},\\"
                rf"u_n(L, t) &= {sp.latex(bcL)}."
                r"\end{aligned}"
            ),
            level="intermediate",
        )

        # ICs (position and velocity at t = 0) — by construction.
        s_ic = step(
            kind="verification",
            title="Verificación de las condiciones iniciales",
            md=(
                "Por construcción de $A_n$ y $B_n$ como coeficientes de "
                "Fourier en seno de $f$ y $g$ respectivamente, la "
                "evaluación de la serie en $t = 0$ reproduce $f$ y su "
                "derivada temporal reproduce $g$."
            ),
            latex=(
                r"\begin{aligned}"
                rf"u(x, 0) &\overset{{!}}{{=}} {sp.latex(f_expr)},\\"
                rf"u_t(x, 0) &\overset{{!}}{{=}} {sp.latex(g_expr)}."
                r"\end{aligned}"
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
                "El panel adjunto muestra $u(x, t)$ como superficie y la "
                "convergencia de las sumas parciales. A diferencia del "
                "calor, aquí los modos **no decaen**: cada uno oscila "
                "con su frecuencia $\\omega_n = c n\\pi/L$. La superficie "
                "tiene patrones cuadriculados característicos."
            ),
            level="basic",
        )

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_wave_physical_interpretation(),
            level="basic",
            observations=[obs.get("wave_harmonic_frequencies")],
        )
