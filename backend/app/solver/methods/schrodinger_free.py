"""Schrödinger equation for a free particle on the real line.

Problem covered
---------------
    iℏ ψ_t = -ℏ²/(2m) ψ_xx        x ∈ ℝ,   t > 0
    ψ(x, 0) = ψ_0(x)

Solution
--------
    ψ(x, t) = ∫_{-∞}^{∞} K(x - y, t) ψ_0(y) dy

with the **free-particle propagator**

    K(x, t) = √(m/(2π i ℏ t)) exp(i m x² / (2 ℏ t)).

This is the Wick rotation (t → it) of the heat kernel:

    G(x, t) = (1/√(4π α² t)) exp(-x²/(4 α² t))  ← heat
    K(x, t) = √(m/(2π i ℏ t)) exp(i m x² /(2 ℏ t))  ← Schrödinger

with the substitution α² ↔ iℏ/(2m). The same convolution structure;
radically different physics: real Gaussian smoothing (Δx ~ √t) vs.
complex Gaussian dispersion (Δx ~ t at large t, unitary L² norm).

Pedagogical contrast
--------------------
- Heat (real line, fourier_heat_line): real Gaussian, diffusive,
  norm not conserved (decays to zero), Δx ~ √t.
- Schrödinger free (this method): complex Gaussian, dispersive,
  L² norm conserved (unitarity), Δx ~ t at long times.
- Schrödinger oscillator: discrete spectrum, equispaced levels,
  bound states with Hermite eigenfunctions.
- Schrödinger well: discrete spectrum, n² spacing, particle in a box.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class SchrodingerFreeLine(Method):
    """Fourier-transform solution of the free Schrödinger equation on ℝ."""

    slug = "schrodinger_free"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        y = sp.Symbol("y", real=True)
        k = sp.Symbol("k", real=True)
        hbar = sp.Symbol("hbar", positive=True)
        m = sp.Symbol("m", positive=True)

        # ---------- Parse ψ_0(x) ---------------------------------------------
        psi0_latex = "0"
        for ic in problem.initial_conditions:
            if ic.order == 0:
                psi0_latex = ic.value
                break
        psi0_expr = parse_scalar_latex(psi0_latex, problem.parameters).subs(
            sp.Symbol("x"), x
        )

        steps: list[Step] = []

        # ===== PASO 0 — Statement =============================================
        steps.append(self._step_statement(psi0_latex))

        # ===== PASO 1 — Classification ========================================
        steps.append(self._step_classification(hbar, m))

        # ===== PASO 2 — Method choice =========================================
        steps.append(self._step_method_choice())

        # ===== PASO 3 — Development ==========================================
        steps.append(self._step_pde_to_ode(k, hbar, m))
        steps.append(self._step_solve_ode(k, hbar, m, t))
        steps.append(self._step_inverse(hbar, m, x, t))

        # ===== PASO 5 — Apply ψ_0 ============================================
        steps.append(self._step_apply_initial(psi0_latex))

        # ===== PASO 6 — Final formula =========================================
        solution_expr = self._build_solution_expression(
            psi0_expr, hbar, m, x, t, y
        )
        steps.append(self._step_final_formula(solution_expr))

        # ===== PASO 7 — Verification =========================================
        steps += self._steps_verification(hbar, m, x, t)

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

    def _step_statement(self, psi0_latex: str) -> Step:
        latex = equation_chain(
            [
                r"&\text{EDP:} \quad i\hbar\, \psi_t = "
                r"-\frac{\hbar^2}{2m}\, \psi_{xx}, "
                r"\quad x \in \mathbb{R},\quad t > 0,",
                rf"&\text{{estado inicial:}} \quad \psi(x, 0) = {psi0_latex}.",
            ]
        )
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (partícula libre en la recta)",
            md=T.T_statement_schrodinger_free(),
            latex=latex,
            level="basic",
        )

    # ===========================================================================
    # PASO 1
    # ===========================================================================

    def _step_classification(self, hbar: sp.Symbol, m: sp.Symbol) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Clasificación (Schrödinger, parabólica compleja)",
            md=(
                "La EDP es de **segundo orden en $x$** y **primer orden en "
                "$t$**, igual que el calor — pero con un coeficiente "
                "**imaginario** delante de $\\psi_t$. Esto la sitúa entre "
                "el calor (parabólica real) y la onda (hiperbólica):"
            ),
            latex=equation_chain(
                [
                    r"i\hbar\, \psi_t &= -\tfrac{\hbar^2}{2m}\, \psi_{xx} "
                    r"\quad \Leftrightarrow \quad "
                    r"\psi_t = i\, \tfrac{\hbar}{2m}\, \psi_{xx},",
                    r"&\text{coeficiente: } i\,\hbar/(2m) \in i\mathbb{R}_+ \Rightarrow "
                    r"\text{difusión compleja}.",
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
            md=T.T_schrodinger_free_method_choice(),
            latex=(
                r"\mathcal{F}[\psi_{xx}](k, t) = -k^2\, \hat\psi(k, t),\qquad "
                r"\mathcal{F}[\psi_t](k, t) = \partial_t \hat\psi(k, t)."
            ),
            level="basic",
            observations=[obs.get("fourier_transform_diagonalizes_pde")],
        )

    # ===========================================================================
    # PASO 3 — Development
    # ===========================================================================

    def _step_pde_to_ode(
        self, k: sp.Symbol, hbar: sp.Symbol, m: sp.Symbol
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3.1 — La EDP se transforma en una EDO en $t$",
            md=T.T_schrodinger_free_pde_to_ode(),
            latex=equation_chain(
                [
                    r"i\hbar\, \psi_t = -\tfrac{\hbar^2}{2m}\, \psi_{xx} "
                    r"&\xrightarrow{\mathcal{F}_x} "
                    r"i\hbar\, \partial_t \hat\psi(k, t) "
                    r"= \tfrac{\hbar^2 k^2}{2m}\, \hat\psi(k, t),",
                    r"&\quad \partial_t \hat\psi = -i\, \omega(k)\, \hat\psi, "
                    r"\quad \omega(k) = \tfrac{\hbar k^2}{2m}.",
                ]
            ),
            level="basic",
            observations=[obs.get("schrodinger_dispersion")],
        )

    def _step_solve_ode(
        self,
        k: sp.Symbol,
        hbar: sp.Symbol,
        m: sp.Symbol,
        t: sp.Symbol,
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3.2 — Solución de la EDO modal",
            md=T.T_schrodinger_free_solve_ode(),
            latex=equation_chain(
                [
                    r"\partial_t \hat\psi &= -i\omega(k)\, \hat\psi "
                    r"\quad \Rightarrow \quad "
                    r"\hat\psi(k, t) = \hat\psi_0(k)\, e^{-i\hbar k^2 t/(2m)}.",
                    r"|\hat\psi(k, t)| &= |\hat\psi_0(k)| "
                    r"\quad (\text{módulo conservado en cada modo}).",
                ]
            ),
            level="intermediate",
        )

    def _step_inverse(
        self,
        hbar: sp.Symbol,
        m: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3.3 — Inversa: convolución con el propagador libre",
            md=T.T_schrodinger_free_inverse(),
            latex=equation_chain(
                [
                    r"\psi(x, t) &= \mathcal{F}^{-1}\!\bigl[\hat\psi_0(k)\, "
                    r"e^{-i\hbar k^2 t/(2m)}\bigr](x) = (\psi_0 * K)(x, t),",
                    r"K(x, t) &= \sqrt{\frac{m}{2\pi i \hbar t}}\, "
                    r"\exp\!\left(\frac{i m x^2}{2 \hbar t}\right).",
                ]
            ),
            level="intermediate",
            observations=[obs.get("wick_rotation_heat_to_schrodinger")],
        )

    # ===========================================================================
    # PASO 5
    # ===========================================================================

    def _step_apply_initial(self, psi0_latex: str) -> Step:
        return step(
            kind="initial",
            title="Paso 5 — Incorporación del estado inicial",
            md=(
                "La transformada $\\hat\\psi_0(k)$ entra explícitamente "
                "en la convolución; cuando invertimos, $\\hat\\psi_0$ "
                "se traduce en $\\psi_0$ apareciendo como factor en "
                "el integrando. Para nuestro problema concreto: "
                f"$\\psi_0(x) = {psi0_latex}$."
            ),
            latex=rf"\psi_0(x) = {psi0_latex}.",
            level="basic",
        )

    # ===========================================================================
    # PASO 6 — Final formula
    # ===========================================================================

    def _build_solution_expression(
        self,
        psi0_expr: sp.Basic,
        hbar: sp.Symbol,
        m: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
        y: sp.Symbol,
    ) -> sp.Basic:
        """Build ψ(x, t) = √(m/(2π i ℏ t)) ∫ exp(im(x-y)²/(2ℏt)) ψ_0(y) dy.

        We attempt to evaluate the integral symbolically: for a Gaussian
        ψ_0(x) = exp(-a x²), SymPy can produce the well-known dispersed
        Gaussian. Otherwise we keep it as an unevaluated Integral and
        let the numerical sampler handle it.
        """
        psi0_of_y = psi0_expr.subs(x, y)
        kernel = sp.exp(sp.I * m * (x - y) ** 2 / (2 * hbar * t))
        prefactor = sp.sqrt(m / (2 * sp.pi * sp.I * hbar * t))

        integrand = kernel * psi0_of_y
        integral = sp.Integral(integrand, (y, -sp.oo, sp.oo))

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

    def _step_final_formula(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Fórmula final (propagador libre)",
            md=T.T_schrodinger_free_final_formula(),
            latex=rf"\boxed{{\; \psi(x, t) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    # ===========================================================================
    # PASO 7 — Verification
    # ===========================================================================

    def _steps_verification(
        self,
        hbar: sp.Symbol,
        m: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
    ) -> list[Step]:
        # Symbolic verification on the propagator itself: iℏ K_t = -(ℏ²/2m) K_xx.
        K = sp.sqrt(m / (2 * sp.pi * sp.I * hbar * t)) * sp.exp(
            sp.I * m * x**2 / (2 * hbar * t)
        )
        K_t = sp.simplify(sp.diff(K, t))
        K_xx = sp.simplify(sp.diff(K, x, 2))
        lhs = sp.simplify(sp.I * hbar * K_t)
        rhs = sp.simplify(-(hbar**2) / (2 * m) * K_xx)
        residual = sp.simplify(lhs - rhs)

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "Como en el calor, la verificación se traslada al "
                "**propagador** $K$: si $K$ satisface la ecuación de "
                "Schrödinger libre, también la satisface $\\psi = "
                "\\psi_0 * K$ (linealidad de $\\partial_x$ y "
                "$\\partial_t$ + regla de convolución). Comprobamos "
                "directamente $i\\hbar K_t = -(\\hbar^2/2m) K_{xx}$."
            ),
            level="basic",
        )
        s_propagator = step(
            kind="verification",
            title="Verificación del propagador: $i\\hbar K_t = -(\\hbar^2/2m) K_{xx}$",
            md=(
                "Derivando explícitamente el propagador libre:"
                if residual == 0
                else "**Atención:** el residuo no se simplificó a cero."
            ),
            latex=equation_chain(
                [
                    rf"i\hbar\, K_t &= {sp.latex(lhs)},",
                    rf"-\tfrac{{\hbar^2}}{{2m}}\, K_{{xx}} &= {sp.latex(rhs)},",
                    rf"i\hbar\, K_t - \bigl(-\tfrac{{\hbar^2}}{{2m}}\, K_{{xx}}\bigr) "
                    rf"&= {sp.latex(residual)}.",
                ]
            ),
            level="intermediate",
        )
        s_unitarity = step(
            kind="verification",
            title="Conservación de la norma $L^2$ (unitariedad)",
            md=(
                "Una propiedad esencial de Schrödinger: la **probabilidad "
                "total se conserva**. En el dominio de Fourier es "
                "inmediata, porque el factor $e^{-i\\omega(k) t}$ tiene "
                "módulo $1$ y la transformada de Fourier preserva la "
                "norma $L^2$ (teorema de Plancherel):"
            ),
            latex=equation_chain(
                [
                    r"\int |\psi(x, t)|^2\, dx "
                    r"&\overset{\text{Plancherel}}{=} "
                    r"\frac{1}{2\pi}\int |\hat\psi(k, t)|^2\, dk",
                    r"&= \frac{1}{2\pi}\int |\hat\psi_0(k)|^2\, "
                    r"\underbrace{|e^{-i\omega(k) t}|^2}_{=\,1}\, dk",
                    r"&= \int |\psi_0(x)|^2\, dx.",
                ]
            ),
            level="exhaustive",
            observations=[obs.get("schrodinger_no_bound_states")],
        )
        return [s_intro, s_propagator, s_unitarity]

    # ===========================================================================
    # PASOS 8 y 9
    # ===========================================================================

    def _step_visualization(self) -> Step:
        return step(
            kind="visualization",
            title="Paso 8 — Visualización ($|\\psi|^2$)",
            md=(
                "Como $\\psi$ es **compleja**, graficamos la "
                "**densidad de probabilidad** $|\\psi(x, t)|^2$ "
                "(lo único medible).\n\n"
                "Si el estado inicial es un paquete gaussiano $\\psi_0 = "
                "e^{-x^2}$, se espera observar:\n\n"
                "- **Ensanchamiento monótono** del paquete con $t$ "
                "(dispersión: cada componente $k$ viaja a su propia "
                "velocidad $v_\\phi = \\hbar k / (2m)$).\n"
                "- **Conservación del área bajo $|\\psi|^2$** "
                "(unitariedad, contrasta con el calor).\n"
                "- **Disminución del pico central** (la masa se "
                "redistribuye en una región más ancha).\n\n"
                "Si añadiéramos un momento inicial $e^{ik_0 x}$ al "
                "paquete, veríamos además **desplazamiento del centro** "
                "a velocidad de grupo $v_g = \\hbar k_0 / m$."
            ),
            level="basic",
            observations=[obs.get("schrodinger_wave_packet_spreading")],
        )

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_schrodinger_free_physical_interpretation(),
            level="basic",
            observations=[
                obs.get("schrodinger_dispersion"),
                obs.get("wick_rotation_heat_to_schrodinger"),
            ],
        )
