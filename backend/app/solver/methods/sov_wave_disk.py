"""Axisymmetric wave equation on a disk — Bessel-Fourier expansion.

Problem covered
---------------
    u_tt = c^2 (u_rr + u_r/r)    in 0 < r < R,  t > 0
    u(R, t) = 0                  (clamped boundary)
    u(r, 0) = f(r)               (initial profile, radially symmetric)
    u_t(r, 0) = g(r)             (initial velocity)
    bounded at r = 0

Method
------
Separation of variables gives radial Bessel ODE -> J_0(mu_n r / R) with
mu_n = n-th positive zero of J_0. Temporal ODE is harmonic with
frequency omega_n = c mu_n / R. Solution:

    u(r, t) = sum_n J_0(mu_n r/R) [A_n cos(omega_n t) + B_n sin(omega_n t)]

where A_n, B_n come from r-weighted Bessel-Fourier projection of f, g.

Notes on symbolic handling
--------------------------
- The Bessel zeros mu_n are transcendental; we keep them as
  `sp.IndexedBase("mu")[n]` and only ever substitute numerical values
  in the plotting step (not implemented in this phase).
- The coefficient integrals usually do NOT close in elementary form,
  so we keep them as `sp.Integral`. The student sees the formula and
  understands it's an honest Bessel-Fourier projection.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class WaveDisk(Method):
    """Axisymmetric vibrating drum (clamped circular membrane)."""

    slug = "sov_wave_disk"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        r = sp.Symbol("r", nonnegative=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        R = sp.Symbol("R", positive=True)
        c = sp.Symbol("c", positive=True)
        n = sp.Symbol("n", integer=True, positive=True)
        mu = sp.IndexedBase("mu")  # mu[n] = n-th positive zero of J_0

        # Parse f (position) and g (velocity) from ICs.
        f_latex = "0"
        g_latex = "0"
        for ic in problem.initial_conditions:
            if ic.order == 0:
                f_latex = ic.value
            elif ic.order == 1:
                g_latex = ic.value
        f_expr = parse_scalar_latex(f_latex, problem.parameters).subs(
            {sp.Symbol("r"): r, sp.Symbol("R"): R}
        )
        g_expr = parse_scalar_latex(g_latex, problem.parameters).subs(
            {sp.Symbol("r"): r, sp.Symbol("R"): R}
        )

        steps: list[Step] = []
        steps.append(self._step_statement(f_latex, g_latex))
        steps.append(self._step_classification())
        steps.append(self._step_method_choice())
        steps += self._steps_separation()
        steps.append(self._step_radial_ode(mu, n))
        steps.append(self._step_eigenvalues(R, mu, n))
        steps.append(self._step_temporal_wave(c, R, mu, n))
        steps.append(self._step_superposition(c, R, mu, n))
        An, Bn = self._compute_coefficients(steps, f_expr, g_expr, r, R, c, mu, n)
        solution_expr = self._build_solution(An, Bn, r, t, R, c, mu, n)
        steps.append(self._step_final(solution_expr))
        steps += self._steps_verification()
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # ---------------------------------------------------------------------

    def _step_statement(self, f_latex: str, g_latex: str) -> Step:
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (membrana circular axisimétrica)",
            md=T.T_statement_wave_disk(),
            latex=equation_chain(
                [
                    r"&u_{tt} = c^2 (u_{rr} + u_r/r),\quad 0 < r < R,\ t > 0,",
                    r"&u(R, t) = 0,\quad u \text{ acotada en } r = 0,",
                    rf"&u(r, 0) = {f_latex},\quad u_t(r, 0) = {g_latex}.",
                ]
            ),
            level="basic",
            observations=[obs.get("wave_needs_two_ics")],
        )

    def _step_classification(self) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Clasificación: hiperbólica",
            md=(
                "Como en la cuerda 1D, el operador $\\partial_t^2 - c^2 \\Delta$ "
                "es hiperbólico (las direcciones temporal y espacial entran "
                "ambas a segundo orden, con signos opuestos). La novedad "
                "geométrica es el término $u_r/r$ del Laplaciano en polares."
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
                    r"\frac{T''(t)}{c^2 T(t)} &= \frac{R''(r) + R'(r)/r}{R(r)} = -\lambda.",
                ]
            ),
            level="basic",
        )

    def _steps_separation(self) -> list[Step]:
        # No new steps beyond method_choice (which already shows the separation).
        return []

    def _step_radial_ode(self, mu: sp.IndexedBase, n: sp.Symbol) -> Step:
        return step(
            kind="development",
            title="Paso 3.5 — EDO radial: ecuación de Bessel de orden cero",
            md=T.T_bessel_radial_ode(),
            latex=equation_chain(
                [
                    r"R''(r) + \frac{R'(r)}{r} + \lambda R(r) &= 0,",
                    r"\text{con cambio } s = \sqrt{\lambda}\, r:",
                    r"s^2 \tilde R''(s) + s \tilde R'(s) + s^2 \tilde R(s) &= 0 "
                    r"\quad \text{(Bessel, orden 0)},",
                    r"R(r) &= c_1 J_0(\sqrt{\lambda}\, r) + c_2 Y_0(\sqrt{\lambda}\, r),",
                    r"\text{regularidad en } r = 0 &\Rightarrow c_2 = 0.",
                ]
            ),
            level="basic",
            observations=[obs.get("bessel_regularity_at_origin")],
        )

    def _step_eigenvalues(
        self, R_sym: sp.Symbol, mu: sp.IndexedBase, n: sp.Symbol
    ) -> Step:
        return step(
            kind="boundary",
            title="Paso 4 — Autovalores: ceros de $J_0$",
            md=T.T_bessel_eigenvalues(),
            latex=equation_chain(
                [
                    r"R(R) = 0 &\Rightarrow J_0(\sqrt{\lambda}\, R) = 0,",
                    r"&\Rightarrow \sqrt{\lambda_n}\, R = \mu_n,\quad "
                    r"\mu_n \text{ = }n\text{-ésimo cero positivo de }J_0,",
                    rf"\boxed{{\;\lambda_n = (\mu_n/R)^2,\quad "
                    rf"R_n(r) = J_0(\mu_n r/R).\;}}",
                ]
            ),
            level="basic",
            observations=[
                obs.get("sturm_liouville_theorem"),
                obs.get("bessel_weighted_orthogonality"),
            ],
        )

    def _step_temporal_wave(
        self, c: sp.Symbol, R_sym: sp.Symbol, mu: sp.IndexedBase, n: sp.Symbol
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3.6 — EDO temporal (oscilación)",
            md=T.T_bessel_temporal_wave(),
            latex=equation_chain(
                [
                    r"T_n'' + c^2 \lambda_n\, T_n &= 0,",
                    r"\omega_n &= c \sqrt{\lambda_n} = c\mu_n/R,",
                    r"T_n(t) &= A_n \cos(\omega_n t) + B_n \sin(\omega_n t).",
                ]
            ),
            level="basic",
            observations=[obs.get("bessel_inharmonic_drum")],
        )

    def _step_superposition(
        self, c: sp.Symbol, R_sym: sp.Symbol, mu: sp.IndexedBase, n: sp.Symbol
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3.7 — Superposición",
            md=(
                "La solución general es la suma de todos los modos "
                "$R_n(r) T_n(t)$ con sus dos componentes temporales:"
            ),
            latex=(
                r"u(r, t) = \sum_{n=1}^{\infty} J_0\!\bigl(\tfrac{\mu_n r}{R}\bigr)\,"
                r"\bigl[A_n \cos(\omega_n t) + B_n \sin(\omega_n t)\bigr],"
                r"\quad \omega_n = c\mu_n/R."
            ),
            level="basic",
        )

    def _compute_coefficients(
        self,
        steps: list[Step],
        f_expr: sp.Basic,
        g_expr: sp.Basic,
        r: sp.Symbol,
        R_sym: sp.Symbol,
        c: sp.Symbol,
        mu: sp.IndexedBase,
        n: sp.Symbol,
    ) -> tuple[sp.Basic, sp.Basic]:
        mu_n = mu[n]
        J1 = sp.Function("J_1")
        # We keep the coefficients as integrals: closing them symbolically
        # would require sympy to know identities of Bessel functions that it
        # doesn't simplify automatically.
        An_integral = sp.Integral(
            r * f_expr * sp.besselj(0, mu_n * r / R_sym), (r, 0, R_sym)
        )
        An = 2 / (R_sym**2 * J1(mu_n) ** 2) * An_integral

        omega_n = c * mu_n / R_sym
        Bn_integral = sp.Integral(
            r * g_expr * sp.besselj(0, mu_n * r / R_sym), (r, 0, R_sym)
        )
        Bn = 2 / (omega_n * R_sym**2 * J1(mu_n) ** 2) * Bn_integral

        steps.append(
            step(
                kind="initial",
                title="Paso 5 — Coeficientes Bessel-Fourier",
                md=T.T_bessel_coefficients(),
                latex=equation_chain(
                    [
                        rf"A_n &= {sp.latex(An)},",
                        rf"B_n &= {sp.latex(Bn)}.",
                    ]
                ),
                sympy_expr=An,
                level="basic",
                observations=[obs.get("bessel_weighted_orthogonality")],
            )
        )
        return An, Bn

    def _build_solution(
        self,
        An: sp.Basic,
        Bn: sp.Basic,
        r: sp.Symbol,
        t: sp.Symbol,
        R_sym: sp.Symbol,
        c: sp.Symbol,
        mu: sp.IndexedBase,
        n: sp.Symbol,
    ) -> sp.Basic:
        mu_n = mu[n]
        omega_n = c * mu_n / R_sym
        spatial = sp.besselj(0, mu_n * r / R_sym)
        temporal = An * sp.cos(omega_n * t) + Bn * sp.sin(omega_n * t)
        return sp.Sum(spatial * temporal, (n, 1, sp.oo))

    def _step_final(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Solución",
            md=(
                "Sustituyendo los coeficientes $A_n$ y $B_n$ en la "
                "superposición:"
            ),
            latex=rf"\boxed{{\; u(r, t) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    def _steps_verification(self) -> list[Step]:
        s = step(
            kind="verification",
            title="Paso 7 — Verificación (estructural)",
            md=(
                "La verificación simbólica directa requiere aplicar la "
                "ecuación de Bessel "
                "$s^2 J_0''(s) + s J_0'(s) + s^2 J_0(s) = 0$, identidad "
                "que SymPy no usa automáticamente al simplificar. "
                "La argumentación pedagógica es:\n\n"
                "1. Cada modo $J_0(\\mu_n r/R) \\cos(c\\mu_n t/R)$ "
                "satisface $u_{tt} = -c^2(\\mu_n/R)^2 u$ trivialmente, "
                "ya que la dependencia temporal es coseno.\n"
                "2. El operador Laplaciano radial sobre "
                "$J_0(\\mu_n r/R)$ devuelve $-(\\mu_n/R)^2 J_0(\\mu_n r/R)$ "
                "por la ecuación de Bessel.\n"
                "3. Por tanto $u_{tt} - c^2 \\Delta u = 0$ término a término.\n\n"
                "Numéricamente (con `scipy.special.j0`) la verificación "
                "se hace en cualquier punto."
            ),
            level="intermediate",
        )
        return [s]

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_bessel_physical_interpretation_wave(),
            level="basic",
            observations=[obs.get("bessel_inharmonic_drum")],
        )
