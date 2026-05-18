"""Schrödinger equation for a particle in a 1D infinite well.

Problem covered
---------------
    i hbar psi_t = -(hbar^2 / 2m) psi_xx     in 0 < x < L,  t > 0
    psi(0, t) = psi(L, t) = 0
    psi(x, 0) = psi_0(x)

Method
------
Separation of variables. The spatial eigenvalue problem is identical
to the heat equation's Sturm-Liouville, but the temporal ODE is
first-order *complex* and produces phase rotation rather than decay.

Result:
    E_n   = n^2 pi^2 hbar^2 / (2 m L^2)
    phi_n = sqrt(2/L) sin(n pi x / L)
    psi   = sum_n c_n phi_n e^{-i E_n t / hbar}
    c_n   = int_0^L phi_n(x) psi_0(x) dx
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class SchrodingerInfiniteWell(Method):
    """Particle in a 1D infinite well — separation of variables."""

    slug = "schrodinger_well"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        L = sp.Symbol("L", positive=True)
        hbar = sp.Symbol("hbar", positive=True)
        m = sp.Symbol("m", positive=True)
        n = sp.Symbol("n", integer=True, positive=True)

        # Parse initial wavefunction psi_0.
        psi0_latex = (
            problem.initial_conditions[0].value
            if problem.initial_conditions
            else "0"
        )
        psi0_expr = parse_scalar_latex(psi0_latex, problem.parameters).subs(
            {sp.Symbol("x"): x, sp.Symbol("L"): L}
        )

        steps: list[Step] = []
        steps.append(self._step_statement(psi0_latex))
        steps.append(self._step_classification())
        steps.append(self._step_method_choice())
        steps += self._steps_separation()
        steps.append(self._step_temporal_and_spatial())
        steps.append(self._step_eigenvalues(L, hbar, m))
        steps.append(self._step_superposition())
        c_n_expr = self._compute_coefficients(steps, psi0_expr, psi0_latex, x, L, n)

        solution_expr = self._build_solution(c_n_expr, x, t, L, hbar, m, n)
        steps.append(self._step_final(solution_expr))
        steps += self._steps_verification(solution_expr, hbar, m, x, t)
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # ---------------------------------------------------------------------

    def _step_statement(self, psi0_latex: str) -> Step:
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (pozo infinito 1D)",
            md=T.T_statement_schrodinger_well(),
            latex=equation_chain(
                [
                    r"&i\hbar\, \psi_t = -\frac{\hbar^2}{2m}\, \psi_{xx},"
                    r"\quad 0 < x < L,\quad t > 0,",
                    r"&\psi(0, t) = \psi(L, t) = 0,",
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
                "Estrictamente hablando la ecuación de Schrödinger no "
                "encaja en la trinitaria parabólica/hiperbólica/elíptica "
                "porque sus coeficientes son **complejos** (la unidad "
                "imaginaria $i$ aparece en $u_t$). Hablando con la "
                "intuición: comparte con el calor la **estructura "
                "parabólica formal** ($u_t$ proporcional a $u_{xx}$), "
                "pero el factor $i$ convierte la disipación en "
                "**oscilación**. Lleva el nombre informal de **ecuación "
                "parabólica compleja**."
            ),
            level="basic",
        )

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método: separación de variables",
            md=T.T_schrodinger_method_choice(),
            level="basic",
        )

    def _steps_separation(self) -> list[Step]:
        s_ansatz = step(
            kind="development",
            title="Paso 3.1 — Ansatz $\\psi = \\varphi(x) T(t)$",
            md=T.T_sov_ansatz(),
            latex=r"\psi(x, t) = \varphi(x)\, T(t).",
            level="basic",
            observations=[obs.get("sov_why_separable")],
        )
        s_sep = step(
            kind="development",
            title="Paso 3.2 — Sustituimos y separamos",
            md=T.T_schrodinger_separation(),
            latex=equation_chain(
                [
                    r"i\hbar\, \varphi(x)\, T'(t) &= -\frac{\hbar^2}{2m}\, "
                    r"\varphi''(x)\, T(t),",
                    r"i\hbar\, \frac{T'(t)}{T(t)} &= -\frac{\hbar^2}{2m}\, "
                    r"\frac{\varphi''(x)}{\varphi(x)} = E.",
                ]
            ),
            level="basic",
        )
        return [s_ansatz, s_sep]

    def _step_temporal_and_spatial(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.3 — Las dos EDOs resultantes",
            md=T.T_schrodinger_spatial_temporal(),
            latex=equation_chain(
                [
                    r"T'(t) &= -\tfrac{i E}{\hbar}\, T(t) \Rightarrow "
                    r"T(t) = T_0\, e^{-i E t / \hbar},",
                    r"\varphi''(x) + \tfrac{2 m E}{\hbar^2}\, \varphi(x) &= 0.",
                ]
            ),
            level="basic",
        )

    def _step_eigenvalues(
        self, L: sp.Symbol, hbar: sp.Symbol, m: sp.Symbol
    ) -> Step:
        return step(
            kind="boundary",
            title="Paso 4 — Autovalores y autofunciones (niveles cuantizados)",
            md=T.T_schrodinger_eigenvalues(),
            latex=equation_chain(
                [
                    r"\varphi(0) = \varphi(L) = 0 &\Rightarrow "
                    r"\sqrt{\tfrac{2mE}{\hbar^2}}\, L = n\pi,",
                    rf"E_n &= \frac{{n^2 \pi^2 \hbar^2}}{{2 m L^2}},",
                    r"\varphi_n(x) &= \sqrt{\tfrac{2}{L}}\, \sin\!\bigl(\tfrac{n\pi x}{L}\bigr).",
                ]
            ),
            level="basic",
            observations=[
                obs.get("sturm_liouville_theorem"),
                obs.get("schrodinger_quantization"),
            ],
        )

    def _step_superposition(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.7 — Superposición",
            md=T.T_schrodinger_superposition(),
            latex=(
                r"\psi(x, t) = \sum_{n=1}^{\infty} c_n\, \sqrt{\tfrac{2}{L}}\, "
                r"\sin\!\bigl(\tfrac{n\pi x}{L}\bigr)\, e^{-i E_n t / \hbar}."
            ),
            level="basic",
        )

    def _compute_coefficients(
        self,
        steps: list[Step],
        psi0_expr: sp.Basic,
        psi0_latex: str,
        x: sp.Symbol,
        L: sp.Symbol,
        n: sp.Symbol,
    ) -> sp.Basic:
        # phi_n is normalized with sqrt(2/L); c_n = int_0^L phi_n psi_0 dx.
        phi_n = sp.sqrt(2 / L) * sp.sin(n * sp.pi * x / L)
        c_n = sp.integrate(phi_n * psi0_expr, (x, 0, L))
        c_n = sp.simplify(c_n.subs(sp.cos(sp.pi * n), (-1) ** n))

        steps.append(
            step(
                kind="initial",
                title=f"Paso 5 — Coeficientes $c_n$ a partir de $\\psi_0(x) = {psi0_latex}$",
                md=(
                    "Por la ortonormalidad de las $\\varphi_n$, "
                    "$c_n = \\int_0^L \\varphi_n(x)\\, \\psi_0(x)\\, dx$. "
                    "Integrando simbólicamente:"
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
        L: sp.Symbol,
        hbar: sp.Symbol,
        m: sp.Symbol,
        n: sp.Symbol,
    ) -> sp.Basic:
        E_n = n**2 * sp.pi**2 * hbar**2 / (2 * m * L**2)
        phi_n = sp.sqrt(2 / L) * sp.sin(n * sp.pi * x / L)
        term = c_n * phi_n * sp.exp(-sp.I * E_n * t / hbar)
        return sp.Sum(term, (n, 1, sp.oo))

    def _step_final(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Función de onda $\\psi(x, t)$",
            md=(
                "Sustituyendo los $c_n$ y los $E_n$ en la superposición, "
                "la función de onda es:"
            ),
            latex=rf"\boxed{{\; \psi(x, t) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        hbar: sp.Symbol,
        m: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
    ) -> list[Step]:
        term = solution_expr.function if isinstance(solution_expr, sp.Sum) else solution_expr
        u_t = sp.diff(term, t)
        u_xx = sp.diff(term, x, 2)
        residual = sp.simplify(sp.I * hbar * u_t - (-hbar**2 / (2 * m)) * u_xx)
        pde_ok = bool(residual == 0)

        s = step(
            kind="verification",
            title="Paso 7 — Verificación (término genérico)",
            md=(
                "Sustituimos el término $n$-ésimo en la EDP. "
                "$i\\hbar \\psi_t$ debe igualar $-(\\hbar^2/2m) \\psi_{xx}$, "
                "lo que ocurre exactamente cuando $E = E_n$. La "
                "verificación es simbólicamente cero."
                if pde_ok
                else "**Atención:** residuo simbólico no cero."
            ),
            latex=rf"i\hbar\, \psi_{{n,t}} + \tfrac{{\hbar^2}}{{2m}}\, \psi_{{n,xx}} = {sp.latex(residual)}.",
            level="intermediate",
        )
        return [s]

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_schrodinger_physical_interpretation(),
            level="basic",
            observations=[
                obs.get("schrodinger_ground_state"),
                obs.get("schrodinger_quantization"),
            ],
        )
