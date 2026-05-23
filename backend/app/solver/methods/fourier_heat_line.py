"""Heat equation on the real line via the Fourier transform.

Problem covered
---------------
    u_t = α² u_xx        x ∈ ℝ,   t > 0
    u(x, 0) = f(x)

Solution
--------
    u(x, t) = (G(·, t) * f)(x)
            = (1/√(4π α² t)) ∫_{-∞}^{∞} exp(-(x-y)²/(4 α² t)) f(y) dy

Where G is the **Gaussian heat kernel**, the fundamental solution of
the heat equation. This is the closed-form analogue of D'Alembert for
the wave equation: same domain (the real line), no boundary conditions,
solution expressed as a convolution with a kernel that encodes the
operator's response to a point source.

Pedagogical contrast
--------------------
- D'Alembert (wave): finite speed of propagation, sharp light cone,
  no smoothing. u(x₀, t₀) depends only on initial data in
  [x₀ - ct₀, x₀ + ct₀].
- Fourier-Gauss (heat): infinite speed of propagation (G(x, t) > 0
  everywhere for t > 0), instant C^∞ smoothing, self-similarity
  under (x, t) ↦ (λx, λ²t).
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class FourierHeatLine(Method):
    """Fourier-transform solution of the heat equation on the real line."""

    slug = "fourier_heat_line"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        y = sp.Symbol("y", real=True)
        k = sp.Symbol("k", real=True)
        alpha = sp.Symbol("alpha", positive=True)

        # ---------- Parse f(x) ------------------------------------------------
        f_latex = "0"
        for ic in problem.initial_conditions:
            if ic.order == 0:
                f_latex = ic.value
                break
        f_expr = parse_scalar_latex(f_latex, problem.parameters).subs(
            sp.Symbol("x"), x
        )

        steps: list[Step] = []

        # ===== PASO 0 — Statement =============================================
        steps.append(self._step_statement(f_latex))

        # ===== PASO 1 — Classification ========================================
        steps.append(self._step_classification(alpha))

        # ===== PASO 2 — Method choice =========================================
        steps.append(self._step_method_choice())

        # ===== PASO 3 — Development ==========================================
        steps.append(self._step_pde_to_ode(k))
        steps.append(self._step_solve_ode(k, alpha, t))
        steps.append(self._step_inverse(alpha, x, t))

        # ===== PASO 5 — Apply the initial condition (already used in step 3) =
        steps.append(self._step_apply_initial_condition(f_latex))

        # ===== PASO 6 — Final formula =========================================
        solution_expr = self._build_solution_expression(f_expr, alpha, x, t, y)
        steps.append(self._step_final_formula(solution_expr, f_latex))

        # ===== PASO 7 — Verification =========================================
        steps += self._steps_verification(solution_expr, alpha, x, t)

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

    def _step_statement(self, f_latex: str) -> Step:
        latex = equation_chain(
            [
                r"&\text{EDP:} \quad u_t = \alpha^2\, u_{xx}, "
                r"\quad x \in \mathbb{R},\quad t > 0,",
                rf"&\text{{condición inicial:}} \quad u(x, 0) = {f_latex}.",
            ]
        )
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (varilla infinita)",
            md=T.T_statement_heat_line(),
            latex=latex,
            level="basic",
        )

    # ===========================================================================
    # PASO 1
    # ===========================================================================

    def _step_classification(self, alpha: sp.Symbol) -> Step:
        A, B, C = alpha**2, sp.Integer(0), sp.Integer(0)
        disc = sp.simplify(B**2 - 4 * A * C)
        return step(
            kind="classification",
            title="Paso 1 — Clasificación (parabólica)",
            md=(
                "La ecuación es de **segundo orden en $x$** y de **primer "
                "orden en $t$**: comparándola con la forma canónica "
                "$A u_{xx} + B u_{xt} + C u_{tt} + \\ldots = 0$:"
            ),
            latex=equation_chain(
                [
                    r"A &= \alpha^2,\quad B = 0,\quad C = 0,",
                    rf"\Delta &= B^2 - 4AC = {sp.latex(disc)},",
                    r"&\Rightarrow \text{EDP parabólica}.",
                ]
            ),
            level="basic",
        )

    # ===========================================================================
    # PASO 2
    # ===========================================================================

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método: transformada de Fourier en $x$",
            md=T.T_heat_line_method_choice(),
            latex=(
                r"\mathcal{F}[\partial_x u](k, t) = ik\, \hat u(k, t),\qquad "
                r"\mathcal{F}[\partial_x^2 u](k, t) = -k^2\, \hat u(k, t)."
            ),
            level="basic",
            observations=[obs.get("fourier_transform_diagonalizes_pde")],
        )

    # ===========================================================================
    # PASO 3 — Development
    # ===========================================================================

    def _step_pde_to_ode(self, k: sp.Symbol) -> Step:
        return step(
            kind="development",
            title="Paso 3.1 — La EDP se transforma en una EDO en $t$",
            md=T.T_heat_line_pde_to_ode(),
            latex=equation_chain(
                [
                    r"u_t = \alpha^2 u_{xx} "
                    r"&\xrightarrow{\mathcal{F}_x} "
                    r"\partial_t \hat u(k, t) = -\alpha^2 k^2\, \hat u(k, t),",
                    r"&\quad \hat u(k, 0) = \hat f(k).",
                ]
            ),
            level="basic",
        )

    def _step_solve_ode(
        self, k: sp.Symbol, alpha: sp.Symbol, t: sp.Symbol
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3.2 — Solución de la EDO modal",
            md=T.T_heat_line_solve_ode(),
            latex=equation_chain(
                [
                    r"\partial_t \hat u &= -\alpha^2 k^2\, \hat u "
                    r"\quad \Rightarrow \quad "
                    r"\hat u(k, t) = \hat f(k)\, e^{-\alpha^2 k^2 t}.",
                ]
            ),
            level="basic",
            observations=[obs.get("gaussian_smoothing")],
        )

    def _step_inverse(
        self, alpha: sp.Symbol, x: sp.Symbol, t: sp.Symbol
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3.3 — Inversa: convolución con la gaussiana",
            md=T.T_heat_line_inverse(),
            latex=equation_chain(
                [
                    r"u(x, t) &= \mathcal{F}^{-1}\!\bigl[\hat f(k)\, "
                    r"e^{-\alpha^2 k^2 t}\bigr](x) = (f * G)(x, t),",
                    r"G(x, t) &= \frac{1}{\sqrt{4\pi \alpha^2 t}}\, "
                    r"\exp\!\left(-\frac{x^2}{4\alpha^2 t}\right).",
                ]
            ),
            level="intermediate",
            observations=[obs.get("heat_kernel_self_similar")],
        )

    # ===========================================================================
    # PASO 5 — Apply initial condition
    # ===========================================================================

    def _step_apply_initial_condition(self, f_latex: str) -> Step:
        return step(
            kind="initial",
            title="Paso 5 — Incorporación de la condición inicial",
            md=(
                "La transformada $\\hat f(k)$ que aparece en el modo "
                "$\\hat u(k, t)$ es **exactamente** la transformada del "
                "dato inicial. Cuando invertimos, esa $\\hat f$ se traduce "
                "en una convolución con $f$ — la condición inicial entra "
                "explícitamente en la fórmula final como el integrando.\n\n"
                "Para nuestro problema concreto: $f(x) = "
                + f_latex
                + "$."
            ),
            latex=rf"f(x) = {f_latex}.",
            level="basic",
        )

    # ===========================================================================
    # PASO 6 — Final formula
    # ===========================================================================

    def _build_solution_expression(
        self,
        f_expr: sp.Basic,
        alpha: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
        y: sp.Symbol,
    ) -> sp.Basic:
        """Build u(x, t) = (1/√(4π α² t)) ∫ exp(-(x-y)²/(4 α² t)) f(y) dy.

        We try to evaluate the integral symbolically (it succeeds for
        Gaussians, polynomials × Gaussian, etc.). If SymPy can't or the
        result is unwieldy, we keep the integral unevaluated — that's
        the textbook form, and the numerical sampler handles it.
        """
        f_of_y = f_expr.subs(x, y)
        kernel = sp.exp(-((x - y) ** 2) / (4 * alpha**2 * t))
        prefactor = 1 / sp.sqrt(4 * sp.pi * alpha**2 * t)

        integrand = kernel * f_of_y
        integral = sp.Integral(integrand, (y, -sp.oo, sp.oo))

        # Attempt evaluation. If SymPy returns the same integral or a
        # Piecewise/conditional we don't trust here, fall back to the
        # unevaluated form.
        try:
            evaluated = sp.simplify(integral.doit())
            if (
                not evaluated.has(sp.Integral)
                and not evaluated.has(sp.Piecewise)
                and evaluated.is_finite is not False
            ):
                return sp.simplify(prefactor * evaluated)
        except Exception:
            pass
        return prefactor * integral

    def _step_final_formula(self, expr: sp.Basic, f_latex: str) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Fórmula final (núcleo de Gauss)",
            md=T.T_heat_line_final_formula(),
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
        alpha: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
    ) -> list[Step]:
        # Symbolic verification of the **kernel** G(x, t) directly — this
        # is what proves the formula works for *every* admissible f, since
        # the convolution preserves the PDE.
        G = sp.exp(-(x**2) / (4 * alpha**2 * t)) / sp.sqrt(
            4 * sp.pi * alpha**2 * t
        )
        G_t = sp.simplify(sp.diff(G, t))
        G_xx = sp.simplify(sp.diff(G, x, 2))
        residual = sp.simplify(G_t - alpha**2 * G_xx)

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "La forma cerrada $u = f * G$ traslada la verificación "
                "del PDE a una propiedad del **núcleo** $G$: si $G$ "
                "satisface el calor, también lo hace la convolución (por "
                "linealidad de las derivadas y por la regla "
                "$\\partial_x (f * g) = f * \\partial_x g$). Comprobamos "
                "que $G_t = \\alpha^2 G_{xx}$ directamente."
            ),
            level="basic",
        )
        s_kernel = step(
            kind="verification",
            title="Verificación del núcleo: $G_t - \\alpha^2 G_{xx} = 0$",
            md=(
                "Diferenciando explícitamente el núcleo gaussiano:"
                if residual == 0
                else "**Atención:** el residuo no se simplificó a cero."
            ),
            latex=equation_chain(
                [
                    rf"G_t &= {sp.latex(G_t)},",
                    rf"G_{{xx}} &= {sp.latex(G_xx)},",
                    rf"G_t - \alpha^2 G_{{xx}} &= {sp.latex(residual)}.",
                ]
            ),
            level="intermediate",
        )
        s_ic = step(
            kind="verification",
            title="Verificación de la condición inicial",
            md=(
                "Cuando $t \\to 0^+$, el núcleo $G(\\cdot, t)$ converge "
                "(en sentido distribucional) a la **delta de Dirac** "
                "$\\delta(x)$: su masa total se mantiene en $1$ "
                "($\\int G\\, dx = 1$ para todo $t$) y la anchura "
                "$\\sigma = \\sqrt{2\\alpha^2 t} \\to 0$. La convolución "
                "$f * \\delta = f$ recupera exactamente el dato inicial:"
            ),
            latex=equation_chain(
                [
                    r"\int_{-\infty}^{\infty} G(x, t)\, dx &= 1 \quad "
                    r"(\text{para todo } t > 0),",
                    r"G(\cdot, t) &\xrightarrow{t \to 0^+} \delta,",
                    r"u(x, 0^+) &= (f * \delta)(x) = f(x).",
                ]
            ),
            level="exhaustive",
        )
        return [s_intro, s_kernel, s_ic]

    # ===========================================================================
    # PASOS 8 y 9
    # ===========================================================================

    def _step_visualization(self) -> Step:
        return step(
            kind="visualization",
            title="Paso 8 — Visualización",
            md=(
                "La superficie adjunta muestra $u(x, t)$ sobre un dominio "
                "acotado del plano $(x, t)$ — recuerda que la solución "
                "real vive en toda la recta. Observa:\n\n"
                "- En $t = 0^+$ el perfil reproduce $f(x)$.\n"
                "- A medida que $t$ crece, el perfil **se ensancha** "
                "como $\\sqrt{t}$ y se **aplana**, conservando el área.\n"
                "- Para $t$ grande, $u$ tiende al valor medio espacial "
                "(cero si $f$ es integrable).\n\n"
                "**Comparación didáctica.** Para la onda, el mismo dato "
                "inicial produciría dos copias viajando rígidamente a "
                "velocidad $c$. Aquí, en cambio, no hay frente: la "
                "información se filtra **simultáneamente en todas las "
                "direcciones** con peso gaussiano."
            ),
            level="basic",
            observations=[obs.get("heat_infinite_speed")],
        )

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_heat_line_physical_interpretation(),
            level="basic",
            observations=[
                obs.get("heat_infinite_speed"),
                obs.get("heat_kernel_self_similar"),
            ],
        )
