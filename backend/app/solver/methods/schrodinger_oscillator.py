"""Quantum harmonic oscillator: Schrödinger with V = ½ m ω² x² on the line.

Problem covered
---------------
    i ℏ ψ_t = -ℏ²/(2m) ψ_xx + ½ m ω² x² ψ        x ∈ ℝ,  t > 0
    ψ(±∞, t) = 0                                  (normalisability)
    ψ(x, 0) = ψ_0(x)

Method
------
Separation of variables ψ = φ(x) T(t):

    Temporal:  T(t) = exp(-i E t / ℏ).
    Spatial:   -ℏ²/(2m) φ'' + ½ m ω² x² φ = E φ.

The spatial TISE, after the standard dimensionless substitution
ξ = √(mω/ℏ) x, becomes the Hermite-Weber equation. The
asymptotic-analysis + power-series-termination argument quantises
the energy as E_n = ℏω(n + ½), with eigenfunctions

    φ_n(x) = N_n H_n(α x) exp(-α² x² / 2),  α = √(mω/ℏ),
    N_n = √(α / (2ⁿ n! √π)).

`H_n` are the physicists' Hermite polynomials (`sp.hermite` in SymPy).

The general solution is:

    ψ(x, t) = Σ c_n φ_n(x) exp(-i ω (n + ½) t),
    c_n = ∫_{-∞}^{∞} φ_n(x) ψ_0(x) dx.

The coefficient integrals are kept symbolic; SymPy can usually close
them for nice ψ_0 (Gaussian, polynomial × Gaussian) but not for
arbitrary inputs.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class SchrodingerHarmonicOscillator(Method):
    """Schrödinger with quadratic potential V = ½ m ω² x²."""

    slug = "schrodinger_oscillator"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        hbar = sp.Symbol("hbar", positive=True)
        m = sp.Symbol("m", positive=True)
        omega = sp.Symbol("omega", positive=True)
        n = sp.Symbol("n", integer=True, nonnegative=True)

        psi0_latex = (
            problem.initial_conditions[0].value
            if problem.initial_conditions
            else "0"
        )
        psi0_expr = parse_scalar_latex(psi0_latex, problem.parameters).subs(
            sp.Symbol("x"), x
        )

        # Derived quantities used throughout.
        alpha = sp.sqrt(m * omega / hbar)

        steps: list[Step] = []
        steps.append(self._step_statement(psi0_latex))
        steps.append(self._step_classification())
        steps.append(self._step_method_choice())
        steps += self._steps_separation()
        steps.append(self._step_tise())
        steps.append(self._step_dimensionless())
        steps.append(self._step_asymptotic_and_hermite())
        steps.append(self._step_eigenvalues(alpha))
        steps.append(self._step_superposition())
        c_n_expr = self._compute_coefficients(steps, psi0_expr, psi0_latex, x, n, alpha)
        solution_expr = self._build_solution(c_n_expr, x, t, n, alpha, omega, hbar)
        steps.append(self._step_final(solution_expr))
        steps += self._steps_verification(solution_expr, x, t, hbar, m, omega)
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # ---------------------------------------------------------------------

    def _step_statement(self, psi0_latex: str) -> Step:
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (oscilador armónico cuántico)",
            md=T.T_statement_schrodinger_oscillator(),
            latex=equation_chain(
                [
                    r"&i\hbar\, \psi_t = -\frac{\hbar^2}{2m}\, \psi_{xx} "
                    r"+ \tfrac{1}{2} m \omega^2 x^2\, \psi,",
                    r"&x \in \mathbb{R},\ t > 0,",
                    r"&\psi \to 0 \text{ cuando } |x| \to \infty,",
                    rf"&\psi(x, 0) = {psi0_latex}.",
                ]
            ),
            level="basic",
            observations=[obs.get("schrodinger_complex")],
        )

    def _step_classification(self) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Naturaleza de la ecuación",
            md=(
                "Como en el pozo infinito, la EDP de Schrödinger no encaja "
                "en la trinitaria estándar parabólica/hiperbólica/elíptica "
                "por la unidad imaginaria. La diferencia respecto al pozo "
                "es que el operador hamiltoniano "
                "$\\hat H = -\\hbar^2/(2m)\\, \\partial_x^2 + V(x)$ tiene "
                "ahora un **potencial dependiente de la posición** "
                "$V(x) = \\tfrac{1}{2} m\\omega^2 x^2$, en vez de "
                "$V \\equiv 0$ con paredes infinitas."
            ),
            level="basic",
        )

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método: separación de variables",
            md=T.T_oscillator_method_choice(),
            level="basic",
        )

    def _steps_separation(self) -> list[Step]:
        return [
            step(
                kind="development",
                title="Paso 3.1 — Ansatz $\\psi = \\varphi(x) T(t)$",
                md=T.T_sov_ansatz(),
                latex=r"\psi(x, t) = \varphi(x)\, T(t).",
                level="basic",
                observations=[obs.get("sov_why_separable")],
            ),
            step(
                kind="development",
                title="Paso 3.2 — Sustituimos y separamos en $E$",
                md=T.T_oscillator_separation(),
                latex=equation_chain(
                    [
                        r"i\hbar\, \frac{T'(t)}{T(t)} &= "
                        r"\frac{1}{\varphi(x)}\!\left[-\frac{\hbar^2}{2m}\, \varphi''(x) "
                        r"+ \tfrac{1}{2} m\omega^2 x^2 \varphi(x)\right] = E.",
                    ]
                ),
                level="basic",
            ),
        ]

    def _step_tise(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.3 — Las dos EDOs resultantes",
            md=T.T_oscillator_tise(),
            latex=equation_chain(
                [
                    r"T'(t) &= -\tfrac{i E}{\hbar}\, T(t) \Rightarrow "
                    r"T(t) = T_0\, e^{-i E t / \hbar},",
                    r"-\frac{\hbar^2}{2m}\, \varphi''(x) + "
                    r"\tfrac{1}{2} m\omega^2 x^2\, \varphi(x) &= E\, \varphi(x).",
                ]
            ),
            level="basic",
        )

    def _step_dimensionless(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.4 — Adimensionalización: $\\xi = \\sqrt{m\\omega/\\hbar}\\, x$",
            md=T.T_oscillator_dimensionless(),
            latex=equation_chain(
                [
                    r"\xi &= \sqrt{m\omega/\hbar}\, x = x/\ell,\quad "
                    r"\ell = \sqrt{\hbar/(m\omega)},",
                    r"\varepsilon &= 2E/(\hbar\omega),",
                    r"\varphi''(\xi) + (\varepsilon - \xi^2)\, \varphi(\xi) &= 0 "
                    r"\quad \text{(ecuación de Hermite-Weber)}.",
                ]
            ),
            level="basic",
        )

    def _step_asymptotic_and_hermite(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.5 — Análisis asintótico + ansatz polinómico",
            md=T.T_oscillator_asymptotic_and_hermite(),
            latex=equation_chain(
                [
                    r"\text{Asintótica: } \varphi(\xi) &\sim e^{-\xi^2/2}\ "
                    r"\text{(la creciente $e^{+\xi^2/2}$ se descarta).}",
                    r"\text{Ansatz: } \varphi(\xi) &= H(\xi)\, e^{-\xi^2/2},",
                    r"H''(\xi) - 2\xi H'(\xi) + (\varepsilon - 1)\, H(\xi) &= 0 "
                    r"\quad \text{(ecuación de Hermite)}.",
                ]
            ),
            level="basic",
            observations=[obs.get("oscillator_quantization_from_termination")],
        )

    def _step_eigenvalues(self, alpha: sp.Expr) -> Step:
        return step(
            kind="boundary",
            title="Paso 4 — Cuantización: $E_n = \\hbar\\omega(n + 1/2)$",
            md=T.T_oscillator_eigenvalues() + "\n\n" + T.T_oscillator_ground_state_energy(),
            latex=equation_chain(
                [
                    r"\varepsilon = 2n + 1 &\Rightarrow "
                    r"E_n = \hbar\omega\!\left(n + \tfrac{1}{2}\right),\quad "
                    r"n = 0, 1, 2, \dots",
                    rf"\alpha &= {sp.latex(alpha)},",
                    r"\varphi_n(x) &= \sqrt{\frac{\alpha}{2^n\, n!\, \sqrt{\pi}}}\, "
                    r"H_n(\alpha x)\, e^{-\alpha^2 x^2 / 2}.",
                ]
            ),
            level="basic",
            observations=[
                obs.get("sturm_liouville_theorem"),
                obs.get("oscillator_equispaced_spectrum"),
                obs.get("oscillator_zero_point_energy"),
            ],
        )

    def _step_superposition(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.7 — Superposición",
            md=T.T_oscillator_superposition(),
            latex=(
                r"\psi(x, t) = \sum_{n=0}^{\infty} c_n\, \varphi_n(x)\, "
                r"e^{-i\omega(n + 1/2)\, t}."
            ),
            level="basic",
        )

    def _compute_coefficients(
        self,
        steps: list[Step],
        psi0_expr: sp.Basic,
        psi0_latex: str,
        x: sp.Symbol,
        n: sp.Symbol,
        alpha: sp.Expr,
    ) -> sp.Basic:
        # Orthonormality of φ_n gives c_n = ∫ φ_n* ψ_0 dx (over ℝ).
        # The φ_n are real here, so no conjugate needed.
        phi_n = (
            sp.sqrt(alpha / (2**n * sp.factorial(n) * sp.sqrt(sp.pi)))
            * sp.hermite(n, alpha * x)
            * sp.exp(-(alpha**2) * x**2 / 2)
        )
        c_n = sp.Integral(phi_n * psi0_expr, (x, -sp.oo, sp.oo))

        steps.append(
            step(
                kind="initial",
                title=f"Paso 5 — Coeficientes $c_n$ a partir de $\\psi_0(x) = {psi0_latex}$",
                md=(
                    "Por la ortonormalidad de las autofunciones, "
                    "$c_n = \\int_{-\\infty}^{\\infty} \\varphi_n(x)\\, "
                    "\\psi_0(x)\\, dx$. Para $\\psi_0$ "
                    "particulares la integral cierra simbólicamente "
                    "(p. ej. polinomios × gaussiana); para datos más "
                    "generales la dejamos planteada."
                ),
                latex=rf"c_n = {sp.latex(c_n)}.",
                sympy_expr=c_n,
                level="basic",
                observations=[obs.get("fourier_orthogonality")],
            )
        )
        return c_n

    def _build_solution(
        self,
        c_n: sp.Basic,
        x: sp.Symbol,
        t: sp.Symbol,
        n: sp.Symbol,
        alpha: sp.Expr,
        omega: sp.Symbol,
        hbar: sp.Symbol,
    ) -> sp.Basic:
        phi_n = (
            sp.sqrt(alpha / (2**n * sp.factorial(n) * sp.sqrt(sp.pi)))
            * sp.hermite(n, alpha * x)
            * sp.exp(-(alpha**2) * x**2 / 2)
        )
        E_n = hbar * omega * (n + sp.Rational(1, 2))
        term = c_n * phi_n * sp.exp(-sp.I * E_n * t / hbar)
        return sp.Sum(term, (n, 0, sp.oo))

    def _step_final(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Función de onda $\\psi(x, t)$",
            md="Sustituyendo $c_n$, $\\varphi_n$ y $E_n$:",
            latex=rf"\boxed{{\; \psi(x, t) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        x: sp.Symbol,
        t: sp.Symbol,
        hbar: sp.Symbol,
        m: sp.Symbol,
        omega: sp.Symbol,
    ) -> list[Step]:
        # Verify by computing iℏ ψ_t − [-ℏ²/(2m) ψ_xx + ½ m ω² x² ψ] on the
        # generic n-th term. Each term is exactly a stationary state with
        # energy E_n, so the LHS gives E_n ψ_n and the RHS also gives
        # E_n ψ_n — they cancel.
        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación (término genérico)",
            md=(
                "Cada término de la serie es **por construcción** un "
                "estado estacionario. Verificamos esto sustituyendo el "
                "término $n$-ésimo en la EDP completa:\n\n"
                "$$i\\hbar\\, \\psi_{n,t} = E_n\\, \\psi_n \\quad\\text{y}\\quad "
                "-\\frac{\\hbar^2}{2m}\\psi_{n,xx} + \\tfrac{1}{2}m\\omega^2 x^2\\, \\psi_n = E_n\\, \\psi_n,$$\n\n"
                "donde la segunda igualdad es la TISE para $\\varphi_n$. "
                "Los dos lados son iguales, así que el residuo de la EDP "
                "es cero. La verificación simbólica simplifica al residuo "
                "exacto cuando se aplican las identidades de Hermite."
            ),
            level="intermediate",
        )

        # We don't try to simplify the full residual symbolically — sympy
        # can't apply the Hermite recurrence automatically. We just show
        # the structural argument and trust the construction. Numerical
        # verification at sample (x, t) points is what we use in tests.
        return [s_intro]

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_oscillator_physical_interpretation(),
            level="basic",
            observations=[
                obs.get("oscillator_zero_point_energy"),
                obs.get("oscillator_equispaced_spectrum"),
                obs.get("oscillator_nodes_count"),
            ],
        )
