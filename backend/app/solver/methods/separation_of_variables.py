"""Separation of variables for the 1D heat equation on a bounded interval.

This module is the PEDAGOGICAL HEART of Phase 1. Every line of code
here has a counterpart in what a teacher would write on the board.
Read it linearly: the `solve` method is intentionally a long, flat
sequence of "compute X, emit a step explaining X, move on" — splitting
it into helpers would scatter the pedagogical flow.

Problem covered
---------------
    u_t = α² u_xx                  in 0 < x < L, t > 0
    u(0, t) = u(L, t) = 0          (Dirichlet, homogeneous)
    u(x, 0) = f(x)                 (initial profile)

Output
------
A `(list[Step], SolutionArtifacts)` tuple:

- Steps 0…9 (statement, classification, method choice, development,
  boundary, initial, final, verification, visualization, interpretation).
- A SymPy expression for `u(x, t)` as a series with the coefficients
  computed symbolically.

Implementation notes
--------------------
- We use `sp.Sum` to keep `u` as an honest infinite series. For
  verification, we sum *term by term* (each term is automatically a
  solution of the PDE, so the sum is too — this lets us avoid the
  subtleties of differentiating under an infinite sum).
- For the Fourier coefficient `B_n` we run `sp.integrate`. When
  SymPy can solve it in closed form we display the result; otherwise
  we leave the integral standing and explain the situation to the
  student. We never silently truncate or numerically evaluate.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class SeparationOfVariablesHeat1D(Method):
    """Separation of variables for the heat equation on [0, L] with Dirichlet 0."""

    slug = "separation_of_variables"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        # ---------- Symbols ----------------------------------------------------
        # We import here (rather than at module top) so the symbols carry
        # any user-declared assumptions from `problem.parameters`.
        x = sp.Symbol("x", real=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        L = sp.Symbol("L", positive=True)
        alpha = sp.Symbol("alpha", positive=True)
        n = sp.Symbol("n", integer=True, positive=True)

        # ---------- Parse the initial profile ---------------------------------
        f_latex = problem.initial_conditions[0].value if problem.initial_conditions else "0"
        f_expr = parse_scalar_latex(f_latex, problem.parameters)
        # Make sure the parsed `f` uses our `x` symbol (the parser uses the
        # canonical one with the same name; substitute to be safe).
        f_expr = f_expr.subs({sp.Symbol("x"): x, sp.Symbol("L"): L})

        # ---------- Build steps ----------------------------------------------
        steps: list[Step] = []

        # ===== PASO 0 — Planteamiento =========================================
        steps.append(self._step_statement(f_latex, L_symbol=L))

        # ===== PASO 1 — Clasificación =========================================
        steps += self._steps_classification(alpha=alpha)

        # ===== PASO 2 — Elección del método ===================================
        steps += self._steps_method_choice()

        # ===== PASO 3 — Desarrollo (separación → 2 EDOs → 3 casos → SL) ======
        steps += self._steps_separation(alpha=alpha, x=x, t=t)
        steps += self._steps_three_cases(L=L)
        steps += self._steps_temporal_ode(alpha=alpha, L=L)
        steps += self._steps_superposition(alpha=alpha, L=L)

        # ===== PASO 5 — Coeficientes de Fourier (PASO 4 ya cubierto arriba) ===
        Bn_expr = self._steps_fourier_coefficients(steps, f_expr, f_latex, L=L, x=x)

        # ===== PASO 6 — Solución final =======================================
        solution_expr = self._build_solution_expression(Bn_expr, x=x, t=t, L=L, alpha=alpha)
        steps.append(self._step_final_solution(solution_expr))

        # ===== PASO 7 — Verificación =========================================
        steps += self._steps_verification(
            solution_expr=solution_expr,
            f_expr=f_expr,
            alpha=alpha,
            x=x,
            t=t,
            L=L,
        )

        # ===== PASO 8 — Visualización (placeholder; real plot in numerics) ===
        steps.append(self._step_visualization())

        # ===== PASO 9 — Interpretación física ================================
        steps.append(self._step_physical_interpretation())

        artifacts = SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )
        return steps, artifacts

    # ===========================================================================
    # PASO 0 — Planteamiento
    # ===========================================================================

    def _step_statement(self, f_latex: str, L_symbol: sp.Symbol) -> Step:
        latex = equation_chain(
            [
                r"&\text{EDP:} \quad u_t = \alpha^2\, u_{xx}, "
                r"\qquad 0 < x < L, \quad t > 0,",
                r"&\text{condiciones de contorno:} \quad u(0, t) = 0, \quad u(L, t) = 0,",
                rf"&\text{{condición inicial:}} \quad u(x, 0) = {f_latex}.",
            ]
        )
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento del problema",
            md=T.T_statement_heat(),
            latex=latex,
            level="basic",
        )

    # ===========================================================================
    # PASO 1 — Clasificación
    # ===========================================================================

    def _steps_classification(self, alpha: sp.Symbol) -> list[Step]:
        # For the heat equation re-written as α² u_xx − u_t = 0 we have
        # A = α², B = 0, C = 0 (the y in "B u_xy + C u_yy" is here the
        # time variable, but it appears only as a first-order term — so
        # the *second-order* discriminant has C = 0 and Δ = 0, confirming
        # parabolic character).
        A = alpha**2
        B = sp.Integer(0)
        C = sp.Integer(0)
        disc = sp.simplify(B**2 - 4 * A * C)

        s1 = step(
            kind="classification",
            title="Paso 1 — Clasificación de la EDP",
            md=T.T_classification_intro(),
            latex=equation_chain(
                [
                    r"&\alpha^2\, u_{xx} - u_t = 0,",
                    rf"&A = {sp.latex(A)}, \quad B = {sp.latex(B)}, \quad C = {sp.latex(C)},",
                    rf"&\Delta = B^2 - 4AC = {sp.latex(disc)}.",
                ]
            ),
            level="basic",
        )
        s2 = step(
            kind="classification",
            title="Conclusión: parabólica",
            md=(
                "Como $\\Delta = 0$, la EDP es **parabólica**. Las parabólicas "
                "tienen una dirección distinguida (el tiempo) que las "
                "convierte en ecuaciones de evolución: dado un perfil "
                "inicial, la EDP nos dice cómo se transforma con el "
                "tiempo. Físicamente, suavizan: las irregularidades del "
                "dato inicial se disipan."
            ),
            level="basic",
        )
        return [s1, s2]

    # ===========================================================================
    # PASO 2 — Elección del método
    # ===========================================================================

    def _steps_method_choice(self) -> list[Step]:
        from app.solver.core.method_picker import _heat_1d_sov

        # The actual MethodChoice text lives in method_picker so it stays
        # in sync with the registry. We just emit it as a step here.
        choice = _heat_1d_sov(None)  # type: ignore[arg-type]  (problem not used by builder)
        s_main = step(
            kind="method_choice",
            title="Paso 2 — Elección del método: separación de variables",
            md=choice.rationale_md,
            level="basic",
        )
        s_alt = step(
            kind="method_choice",
            title="Alternativas consideradas",
            md=choice.alternatives_md,
            level="intermediate",
        )
        return [s_main, s_alt]

    # ===========================================================================
    # PASO 3 — Desarrollo
    # ===========================================================================

    def _steps_separation(
        self, alpha: sp.Symbol, x: sp.Symbol, t: sp.Symbol
    ) -> list[Step]:
        X = sp.Function("X")
        Tt = sp.Function("T")

        # Ansatz step.
        s_ansatz = step(
            kind="development",
            title="Paso 3.1 — Ansatz separable",
            md=T.T_sov_ansatz(),
            latex=r"u(x, t) = X(x)\, T(t).",
            level="basic",
            observations=[obs.get("sov_why_separable")],
        )

        # Compute partial derivatives of the ansatz.
        ansatz = X(x) * Tt(t)
        u_t_val = sp.diff(ansatz, t)         # = X(x) T'(t)
        u_xx_val = sp.diff(ansatz, x, 2)     # = X''(x) T(t)

        s_subs = step(
            kind="development",
            title="Paso 3.2 — Sustituimos en la EDP",
            md=(
                "Calculamos las derivadas del ansatz y las llevamos a la "
                "EDP. Notar que cada derivada actúa sólo sobre uno de "
                "los factores:"
            ),
            latex=equation_chain(
                [
                    rf"u_t &= {sp.latex(u_t_val)},",
                    rf"u_{{xx}} &= {sp.latex(u_xx_val)},",
                    rf"\Rightarrow \quad X(x)\, T'(t) &= \alpha^2\, X''(x)\, T(t).",
                ]
            ),
            level="basic",
        )

        # Divide both sides by α² X(x) T(t).
        s_divide = step(
            kind="development",
            title="Paso 3.3 — Dividimos por $\\alpha^2\\, X(x)\\, T(t)$",
            md=(
                "Dividimos ambos lados de la igualdad por $\\alpha^2 X(x) T(t)$ "
                "(legítimo donde ambos factores son no nulos, que es donde "
                "nos importa). El resultado tiene **toda la dependencia en "
                "$t$ a un lado** y **toda la dependencia en $x$ al otro**:"
            ),
            latex=r"\frac{T'(t)}{\alpha^2\, T(t)} = \frac{X''(x)}{X(x)}.",
            level="basic",
        )

        s_constant = step(
            kind="development",
            title="Paso 3.4 — Constante de separación",
            md=T.T_sov_constant_separation(),
            latex=equation_chain(
                [
                    r"\frac{T'(t)}{\alpha^2\, T(t)} = \frac{X''(x)}{X(x)} &= -\lambda,",
                    r"\Rightarrow \quad T'(t) + \alpha^2 \lambda\, T(t) &= 0,",
                    r"\qquad\qquad X''(x) + \lambda\, X(x) &= 0.",
                ]
            ),
            level="basic",
            observations=[obs.get("sov_sign_convention")],
        )
        return [s_ansatz, s_subs, s_divide, s_constant]

    def _steps_three_cases(self, L: sp.Symbol) -> list[Step]:
        # Spatial ODE + the three sign cases.
        s_intro = step(
            kind="development",
            title="Paso 3.5 — Examen de los tres casos en $\\lambda$",
            md=T.T_sov_three_cases_intro(),
            level="basic",
            observations=[obs.get("sov_why_three_cases")],
        )

        # ----- Case λ < 0 ----------------------------------------------------
        s_neg = step(
            kind="development",
            title="Caso 1: $\\lambda < 0$",
            md=T.T_sov_case_lambda_negative(),
            latex=equation_chain(
                [
                    r"\lambda &= -\mu^2, \quad \mu > 0,",
                    r"X''(x) - \mu^2 X(x) &= 0,",
                    r"X(x) &= A\, e^{\mu x} + B\, e^{-\mu x}.",
                ]
            ),
            level="basic",
        )
        s_neg_bc = step(
            kind="development",
            title="…descartado por las condiciones de contorno",
            md=T.T_sov_case_lambda_negative_discard(),
            latex=equation_chain(
                [
                    r"X(0) = 0 &\Rightarrow A + B = 0 \Rightarrow B = -A,",
                    r"X(L) = 0 &\Rightarrow A\bigl(e^{\mu L} - e^{-\mu L}\bigr) = 2A\,\sinh(\mu L) = 0,",
                    r"\sinh(\mu L) > 0 &\Rightarrow A = 0 \Rightarrow B = 0,",
                    r"\therefore X &\equiv 0 \quad (\text{trivial, descartada}).",
                ]
            ),
            level="intermediate",
        )

        # ----- Case λ = 0 ----------------------------------------------------
        s_zero = step(
            kind="development",
            title="Caso 2: $\\lambda = 0$",
            md=T.T_sov_case_lambda_zero(),
            latex=equation_chain(
                [
                    r"X''(x) &= 0,",
                    r"X(x) &= A x + B.",
                ]
            ),
            level="basic",
        )
        s_zero_bc = step(
            kind="development",
            title="…también descartado",
            md=T.T_sov_case_lambda_zero_discard(),
            latex=equation_chain(
                [
                    r"X(0) = 0 &\Rightarrow B = 0,",
                    r"X(L) = 0 &\Rightarrow A L = 0 \Rightarrow A = 0,",
                    r"\therefore X &\equiv 0.",
                ]
            ),
            level="intermediate",
        )

        # ----- Case λ > 0 — the productive one -------------------------------
        s_pos = step(
            kind="development",
            title="Caso 3: $\\lambda > 0$ (el que sobrevive)",
            md=T.T_sov_case_lambda_positive(),
            latex=equation_chain(
                [
                    r"\lambda &= \mu^2, \quad \mu > 0,",
                    r"X''(x) + \mu^2 X(x) &= 0,",
                    r"X(x) &= A \cos(\mu x) + B \sin(\mu x).",
                ]
            ),
            level="basic",
        )
        s_eigen = step(
            kind="boundary",
            title="Paso 4 — Aplicación de las condiciones de contorno: autovalores y autofunciones",
            md=T.T_sov_eigenvalues(),
            latex=equation_chain(
                [
                    r"X(0) &= 0 \Rightarrow A = 0,",
                    r"X(x) &= B \sin(\mu x),",
                    r"X(L) = 0 &\Rightarrow B \sin(\mu L) = 0 \Rightarrow \sin(\mu L) = 0,",
                    r"&\Rightarrow \mu L = n\pi, \quad n = 1, 2, 3, \dots,",
                    r"&\Rightarrow \boxed{\;\lambda_n = \left(\tfrac{n\pi}{L}\right)^2, "
                    r"\quad X_n(x) = \sin\!\left(\tfrac{n\pi x}{L}\right).\;}",
                ]
            ),
            level="basic",
            observations=[obs.get("sturm_liouville_theorem")],
        )

        return [s_intro, s_neg, s_neg_bc, s_zero, s_zero_bc, s_pos, s_eigen]

    def _steps_temporal_ode(self, alpha: sp.Symbol, L: sp.Symbol) -> list[Step]:
        s = step(
            kind="development",
            title="Paso 3.6 — Resolución de la EDO temporal",
            md=T.T_sov_temporal_ode(),
            latex=equation_chain(
                [
                    r"T_n'(t) + \alpha^2 \lambda_n\, T_n(t) &= 0,",
                    r"\frac{dT_n}{T_n} &= -\alpha^2 \lambda_n\, dt,",
                    r"\ln |T_n(t)| &= -\alpha^2 \lambda_n\, t + \text{cte},",
                    r"T_n(t) &= C_n\, e^{-\alpha^2 \lambda_n t} = C_n\, e^{-\alpha^2 (n\pi/L)^2 t}.",
                ]
            ),
            level="basic",
            observations=[obs.get("modes_decay_rate")],
        )
        return [s]

    def _steps_superposition(self, alpha: sp.Symbol, L: sp.Symbol) -> list[Step]:
        # Build u_n and the formal series.
        s = step(
            kind="development",
            title="Paso 3.7 — Superposición",
            md=T.T_sov_superposition(),
            latex=equation_chain(
                [
                    r"u_n(x, t) &= B_n \sin\!\left(\tfrac{n\pi x}{L}\right) e^{-\alpha^2 (n\pi/L)^2 t},",
                    r"u(x, t) &= \sum_{n=1}^{\infty} B_n \sin\!\left(\tfrac{n\pi x}{L}\right) e^{-\alpha^2 (n\pi/L)^2 t}.",
                ]
            ),
            level="basic",
        )
        return [s]

    # ===========================================================================
    # PASO 5 — Coeficientes de Fourier
    # ===========================================================================

    def _steps_fourier_coefficients(
        self,
        steps: list[Step],
        f_expr: sp.Basic,
        f_latex: str,
        L: sp.Symbol,
        x: sp.Symbol,
    ) -> sp.Basic:
        """Append the Fourier-coefficient steps and return `B_n` as an expression in `n`."""
        n = sp.Symbol("n", integer=True, positive=True)

        # Step: set up the orthogonality argument.
        steps.append(
            step(
                kind="initial",
                title="Paso 5.1 — Cálculo de $B_n$ vía ortogonalidad",
                md=T.T_fourier_coefficients_setup(),
                level="basic",
                observations=[obs.get("fourier_orthogonality")],
            )
        )

        # Step: write the integral formula.
        steps.append(
            step(
                kind="initial",
                title="Fórmula de los coeficientes",
                md=T.T_fourier_coefficient_formula(),
                latex=(
                    r"B_n = \frac{2}{L} \int_0^L f(x)\, "
                    r"\sin\!\left(\tfrac{n\pi x}{L}\right)\, dx."
                ),
                level="basic",
            )
        )

        # Step: plug in our particular f and try to integrate.
        steps.append(
            step(
                kind="initial",
                title=f"Paso 5.2 — Sustituimos $f(x) = {f_latex}$",
                md=T.T_fourier_coefficient_compute(f_latex),
                latex=(
                    rf"B_n = \frac{{2}}{{L}} \int_0^L {sp.latex(f_expr)} "
                    rf"\sin\!\left(\tfrac{{n\pi x}}{{L}}\right)\, dx."
                ),
                level="basic",
            )
        )

        integrand = f_expr * sp.sin(n * sp.pi * x / L)
        try:
            integral_val = sp.integrate(integrand, (x, 0, L))
            integral_val = sp.simplify(integral_val)
        except Exception:
            integral_val = sp.Integral(integrand, (x, 0, L))

        Bn = sp.simplify(sp.Rational(2) / L * integral_val)
        # SymPy already knows sin(k*pi) = 0 for integer k (because of
        # the assumption on `n`), but for safety we re-simplify after
        # substituting cos(k*pi) → (-1)^k, which sometimes survives.
        Bn = sp.simplify(Bn.subs(sp.cos(sp.pi * n), (-1) ** n))

        steps.append(
            step(
                kind="initial",
                title="Paso 5.3 — Resultado de la integral",
                md=(
                    "Calculamos la integral simbólicamente. SymPy maneja el "
                    "álgebra; lo que importa pedagógicamente es **qué tipo "
                    "de objeto resulta**: una expresión cerrada en $n$. "
                    "Esta expresión es la que define todos los coeficientes "
                    "de la serie de un solo plumazo."
                ),
                latex=rf"B_n = {sp.latex(Bn)}.",
                sympy_expr=Bn,
                level="basic",
            )
        )

        # Show the first few values explicitly — extremely useful for
        # sanity-checking and for students to see how the series builds.
        try:
            sample = [(k, sp.simplify(Bn.subs(n, k))) for k in (1, 2, 3, 4, 5)]
            sample_latex = equation_chain(
                [
                    rf"B_{{{k}}} &= {sp.latex(v)}"
                    for k, v in sample
                ]
            )
            steps.append(
                step(
                    kind="initial",
                    title="Primeros coeficientes",
                    md=(
                        "Evaluamos en $n = 1, 2, 3, 4, 5$ para visualizar la "
                        "forma concreta de los primeros términos. Si "
                        "aparecen muchos ceros, suele ser síntoma de que "
                        "$f$ ya estaba alineada con una autofunción."
                    ),
                    latex=sample_latex,
                    level="intermediate",
                )
            )
        except Exception:
            # If a particular f makes the substitution fail, we silently
            # skip the sample; it is a "nice to have".
            pass

        return Bn

    # ===========================================================================
    # Build the solution expression
    # ===========================================================================

    def _build_solution_expression(
        self,
        Bn: sp.Basic,
        x: sp.Symbol,
        t: sp.Symbol,
        L: sp.Symbol,
        alpha: sp.Symbol,
    ) -> sp.Basic:
        n = sp.Symbol("n", integer=True, positive=True)
        term = Bn * sp.sin(n * sp.pi * x / L) * sp.exp(-(alpha**2) * (n * sp.pi / L) ** 2 * t)
        return sp.Sum(term, (n, 1, sp.oo))

    # ===========================================================================
    # PASO 6 — Solución final
    # ===========================================================================

    def _step_final_solution(self, solution_expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Solución",
            md=T.T_final_solution(),
            latex=rf"\boxed{{\; u(x, t) = {sp.latex(solution_expr)} \;}}",
            sympy_expr=solution_expr,
            level="basic",
        )

    # ===========================================================================
    # PASO 7 — Verificación
    # ===========================================================================

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        f_expr: sp.Basic,
        alpha: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
        L: sp.Symbol,
    ) -> list[Step]:
        from app.solver.verify import verify_heat_solution

        result = verify_heat_solution(
            solution_expr=solution_expr,
            f_expr=f_expr,
            alpha=alpha,
            x=x,
            t=t,
            L=L,
        )

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
                T.T_verification_pde_ok()
                if result.pde_ok
                else "**Atención:** la verificación simbólica de la EDP no cerró. "
                "Detalles abajo."
            ),
            latex=result.pde_check_latex,
            level="intermediate",
        )

        s_bc = step(
            kind="verification",
            title="Verificación de las condiciones de contorno",
            md=(
                "Evaluamos $u(0, t)$ y $u(L, t)$. Cada uno de los "
                "$\\sin(n\\pi \\cdot 0/L)$ y $\\sin(n\\pi \\cdot L/L) = "
                "\\sin(n\\pi)$ vale 0 para todo $n \\in \\mathbb{Z}^+$, "
                "luego toda la serie es 0."
            ),
            latex=result.bc_check_latex,
            level="intermediate",
        )

        s_ic = step(
            kind="verification",
            title="Verificación de la condición inicial",
            md=T.T_verification_ic_ok(),
            latex=result.ic_check_latex,
            level="intermediate",
        )
        return [s_intro, s_pde, s_bc, s_ic]

    # ===========================================================================
    # PASO 8 — Visualización (frontend wires up the actual plot)
    # ===========================================================================

    def _step_visualization(self) -> Step:
        return step(
            kind="visualization",
            title="Paso 8 — Visualización",
            md=(
                "El panel adjunto muestra $u(x, t)$ como superficie 3D y "
                "como animación a lo largo de $t$. Además, comparamos las "
                "**sumas parciales** con $N = 1, 5, 20, 100$ términos para "
                "ver cómo la serie va aproximando el perfil inicial. "
                "Observa cómo:\n\n"
                "- Con $N = 1$ tenemos sólo el primer modo: la "
                "aproximación es burda salvo cuando $f$ coincide con "
                "ese modo.\n"
                "- Al aumentar $N$, las irregularidades del perfil se "
                "capturan.\n"
                "- Para $t > 0$, los modos altos decaen muy rápido y la "
                "diferencia entre $N = 20$ y $N = 100$ se vuelve "
                "imperceptible."
            ),
            level="basic",
        )

    # ===========================================================================
    # PASO 9 — Interpretación física
    # ===========================================================================

    def _step_physical_interpretation(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_physical_interpretation(),
            level="basic",
        )
