"""Axisymmetric heat equation on a disk — Bessel-Fourier expansion.

Problem covered
---------------
    u_t = alpha^2 (u_rr + u_r/r)     in 0 < r < R,  t > 0
    u(R, t) = 0
    u(r, 0) = f(r)
    bounded at r = 0

Method
------
Same separation/Bessel spectrum as the wave case (J_0 zeros), but
first-order temporal ODE gives exponential decay
T_n(t) = exp(-alpha^2 (mu_n / R)^2 t).
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class HeatDisk(Method):
    """Axisymmetric heat equation on a disk."""

    slug = "sov_heat_disk"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        r = sp.Symbol("r", nonnegative=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        R = sp.Symbol("R", positive=True)
        alpha = sp.Symbol("alpha", positive=True)
        n = sp.Symbol("n", integer=True, positive=True)
        mu = sp.IndexedBase("mu")

        f_latex = (
            problem.initial_conditions[0].value
            if problem.initial_conditions
            else "0"
        )
        f_expr = parse_scalar_latex(f_latex, problem.parameters).subs(
            {sp.Symbol("r"): r, sp.Symbol("R"): R}
        )

        steps: list[Step] = []
        steps.append(self._step_statement(f_latex))
        steps.append(self._step_classification())
        steps.append(self._step_method_choice())
        steps.append(self._step_radial_ode())
        steps.append(self._step_eigenvalues())
        steps.append(self._step_temporal(alpha))
        steps.append(self._step_superposition(alpha, R, mu, n))

        Bn = self._compute_coefficient(steps, f_expr, r, R, mu, n)
        solution_expr = self._build_solution(Bn, r, t, R, alpha, mu, n)
        steps.append(self._step_final(solution_expr))
        steps.append(self._step_verification())
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # ---------------------------------------------------------------------

    def _step_statement(self, f_latex: str) -> Step:
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (calor en disco axisimétrico)",
            md=T.T_statement_heat_disk(),
            latex=equation_chain(
                [
                    r"&u_t = \alpha^2 (u_{rr} + u_r/r),\quad 0 < r < R,\ t > 0,",
                    r"&u(R, t) = 0,\quad u \text{ acotada en } r = 0,",
                    rf"&u(r, 0) = {f_latex}.",
                ]
            ),
            level="basic",
        )

    def _step_classification(self) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Clasificación: parabólica",
            md=(
                "Es **parabólica**, igual que el calor 1D: $u_t$ a la "
                "izquierda, Laplaciano a la derecha. La novedad es la "
                "geometría circular (peso $r$ en el Laplaciano)."
            ),
            level="basic",
        )

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Separación de variables",
            md=T.T_bessel_method_choice(),
            latex=equation_chain(
                [
                    r"u(r, t) &= R(r)\, T(t),",
                    r"\frac{T'(t)}{\alpha^2 T(t)} &= \frac{R''(r) + R'(r)/r}{R(r)} = -\lambda.",
                ]
            ),
            level="basic",
        )

    def _step_radial_ode(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.5 — EDO radial: Bessel de orden 0",
            md=T.T_bessel_radial_ode(),
            level="basic",
            observations=[obs.get("bessel_regularity_at_origin")],
        )

    def _step_eigenvalues(self) -> Step:
        return step(
            kind="boundary",
            title="Paso 4 — Autovalores: ceros de $J_0$",
            md=T.T_bessel_eigenvalues(),
            latex=(
                r"\boxed{\;\lambda_n = (\mu_n/R)^2,\quad "
                r"R_n(r) = J_0(\mu_n r/R),\quad J_0(\mu_n) = 0.\;}"
            ),
            level="basic",
            observations=[
                obs.get("sturm_liouville_theorem"),
                obs.get("bessel_weighted_orthogonality"),
            ],
        )

    def _step_temporal(self, alpha: sp.Symbol) -> Step:
        return step(
            kind="development",
            title="Paso 3.6 — EDO temporal (decaimiento)",
            md=T.T_bessel_temporal_heat(),
            latex=equation_chain(
                [
                    r"T_n'(t) + \alpha^2 \lambda_n\, T_n(t) &= 0,",
                    r"T_n(t) &= C_n\, e^{-\alpha^2 (\mu_n/R)^2 t}.",
                ]
            ),
            level="basic",
        )

    def _step_superposition(
        self,
        alpha: sp.Symbol,
        R_sym: sp.Symbol,
        mu: sp.IndexedBase,
        n: sp.Symbol,
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3.7 — Superposición",
            md="Suma de los modos $R_n T_n$:",
            latex=(
                r"u(r, t) = \sum_{n=1}^{\infty} B_n\, J_0\!\bigl(\tfrac{\mu_n r}{R}\bigr)\, "
                r"e^{-\alpha^2 (\mu_n/R)^2 t}."
            ),
            level="basic",
        )

    def _compute_coefficient(
        self,
        steps: list[Step],
        f_expr: sp.Basic,
        r: sp.Symbol,
        R_sym: sp.Symbol,
        mu: sp.IndexedBase,
        n: sp.Symbol,
    ) -> sp.Basic:
        mu_n = mu[n]
        J1 = sp.Function("J_1")
        integral = sp.Integral(
            r * f_expr * sp.besselj(0, mu_n * r / R_sym), (r, 0, R_sym)
        )
        Bn = 2 / (R_sym**2 * J1(mu_n) ** 2) * integral

        steps.append(
            step(
                kind="initial",
                title="Paso 5 — Coeficientes de Bessel-Fourier",
                md=T.T_bessel_coefficients(),
                latex=rf"B_n = {sp.latex(Bn)}.",
                sympy_expr=Bn,
                level="basic",
                observations=[obs.get("bessel_weighted_orthogonality")],
            )
        )
        return Bn

    def _build_solution(
        self,
        Bn: sp.Basic,
        r: sp.Symbol,
        t: sp.Symbol,
        R_sym: sp.Symbol,
        alpha: sp.Symbol,
        mu: sp.IndexedBase,
        n: sp.Symbol,
    ) -> sp.Basic:
        mu_n = mu[n]
        spatial = sp.besselj(0, mu_n * r / R_sym)
        temporal = sp.exp(-(alpha**2) * (mu_n / R_sym) ** 2 * t)
        return sp.Sum(Bn * spatial * temporal, (n, 1, sp.oo))

    def _step_final(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Solución",
            md="Sustituyendo $B_n$ en la superposición:",
            latex=rf"\boxed{{\; u(r, t) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    def _step_verification(self) -> Step:
        return step(
            kind="verification",
            title="Paso 7 — Verificación (estructural)",
            md=(
                "Para el término genérico $u_n = B_n J_0(\\mu_n r/R)\\, "
                "e^{-\\alpha^2 (\\mu_n/R)^2 t}$:\n\n"
                "1. $\\partial_t u_n = -\\alpha^2 (\\mu_n/R)^2\\, u_n$.\n"
                "2. El Laplaciano radial sobre $J_0(\\mu_n r/R)$ devuelve "
                "$-(\\mu_n/R)^2 J_0(\\mu_n r/R)$ (ecuación de Bessel), "
                "así que $\\alpha^2 \\Delta u_n = -\\alpha^2 (\\mu_n/R)^2 u_n$.\n"
                "3. Coinciden: la EDP se cumple término a término.\n\n"
                "Las BCs son obvias: $J_0(\\mu_n) = 0$ por construcción de "
                "los autovalores."
            ),
            level="intermediate",
        )

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_bessel_physical_interpretation_heat(),
            level="basic",
        )
