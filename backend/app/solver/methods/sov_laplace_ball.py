"""Axisymmetric Laplace in a 3D ball — Legendre expansion.

Problem covered
---------------
    Δu = 0           in r < R   (3D ball, spherical coordinates)
    u(R, θ) = f(θ)   (Dirichlet, only depends on co-latitude θ)
    bounded at r = 0

Method
------
Separation in spherical coordinates. The angular factor satisfies
Legendre's equation; regularity at the poles forces ell = 0, 1, 2, ...
with Theta_ell(theta) = P_ell(cos theta). Radial factor is the Euler
equation with solutions r^ell and r^(-ell-1); regularity at origin
selects r^ell.

    u(r, theta) = sum_ell A_ell r^ell P_ell(cos theta)
    A_ell = (2 ell + 1) / (2 R^ell) int_{-1}^{1} f(arccos xi) P_ell(xi) dxi

Notes
-----
- We use `sp.legendre(ell, xi)` for the polynomials and integrate
  symbolically against `f`. For nice f (a polynomial in cos theta,
  or a finite linear combination of low P_ell's) the integrals close
  cleanly.
- Sympy's `sp.integrate` may not close in elementary form for general
  f. In that case we leave the coefficient as an `sp.Integral`.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class LaplaceBall(Method):
    """Laplace inside a 3D ball, axisymmetric Dirichlet data."""

    slug = "sov_laplace_ball"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        r = sp.Symbol("r", nonnegative=True)
        theta = sp.Symbol("theta", real=True)
        xi = sp.Symbol("xi", real=True)
        R = sp.Symbol("R", positive=True)
        ell = sp.Symbol("ell", integer=True, nonnegative=True)

        # Extract f(theta) from the Dirichlet BC.
        f_latex = "0"
        for bc in problem.boundary_conditions:
            if bc.type == "dirichlet" and bc.value.strip() != "0":
                f_latex = bc.value
                break
        f_expr_theta = parse_scalar_latex(f_latex, problem.parameters).subs(
            {sp.Symbol("theta"): theta, sp.Symbol("R"): R}
        )
        # Express f in terms of xi = cos theta. We substitute cos(theta) -> xi.
        f_expr_xi = f_expr_theta.subs(sp.cos(theta), xi)
        # If user used "cos(theta)" elsewhere or pure trig form, normalise sin too.
        # (sin(theta) = sqrt(1 - xi**2), but we leave that to the user to avoid
        # making spurious substitutions.)

        steps: list[Step] = []
        steps.append(self._step_statement(f_latex))
        steps.append(self._step_classification())
        steps.append(self._step_method_choice())
        steps.append(self._step_angular())
        steps.append(self._step_radial())
        steps.append(self._step_superposition())

        A_ell = self._compute_coefficient(steps, f_expr_xi, xi, R, ell, f_latex)
        solution_expr = self._build_solution(A_ell, r, theta, R, ell)
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
            title="Paso 0 — Planteamiento (Laplace en bola axisimétrica)",
            md=T.T_statement_laplace_ball(),
            latex=equation_chain(
                [
                    r"&\Delta u = 0,\quad r < R,",
                    rf"&u(R, \theta) = {f_latex},",
                    r"&u \text{ acotada en } r = 0,\ \theta = 0,\ \theta = \pi.",
                ]
            ),
            level="basic",
        )

    def _step_classification(self) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Clasificación: elíptica",
            md=(
                "$\\Delta u = 0$ es elíptica en cualquier sistema de "
                "coordenadas. Heredan principio del máximo y unicidad "
                "del problema de Dirichlet."
            ),
            level="basic",
            observations=[obs.get("laplace_max_principle")],
        )

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Separación en coordenadas esféricas",
            md=T.T_laplace_ball_method_choice(),
            latex=equation_chain(
                [
                    r"u(r, \theta) &= R(r)\, \Theta(\theta),",
                    r"\frac{(r^2 R')'}{R} &= -\frac{(\sin\theta\, \Theta')'}{\sin\theta\, \Theta}"
                    r" = \ell(\ell + 1).",
                ]
            ),
            level="basic",
        )

    def _step_angular(self) -> Step:
        return step(
            kind="boundary",
            title="Paso 4 — EDO angular: ecuación de Legendre",
            md=T.T_laplace_ball_angular(),
            latex=equation_chain(
                [
                    r"\xi &= \cos\theta,",
                    r"\bigl[(1 - \xi^2)\, \Theta'(\xi)\bigr]' + \ell(\ell + 1)\, \Theta(\xi) &= 0,",
                    r"\text{regularidad en } \xi = \pm 1 &\Rightarrow \ell \in \mathbb{Z}_{\geq 0},",
                    r"\Theta_\ell(\xi) &= P_\ell(\xi) = P_\ell(\cos\theta).",
                ]
            ),
            level="basic",
            observations=[obs.get("legendre_pole_regularity")],
        )

    def _step_radial(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.6 — EDO radial: Euler",
            md=T.T_laplace_ball_radial(),
            latex=equation_chain(
                [
                    r"r^2 R'' + 2 r R' - \ell(\ell + 1)\, R &= 0,",
                    r"\text{ansatz } R = r^p &\Rightarrow (p - \ell)(p + \ell + 1) = 0,",
                    r"R(r) &= a_1 r^\ell + a_2 r^{-\ell - 1},",
                    r"\text{regularidad en } r = 0 &\Rightarrow a_2 = 0.",
                ]
            ),
            level="basic",
        )

    def _step_superposition(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.7 — Superposición",
            md=(
                "Combinando todos los modos $r^\\ell P_\\ell(\\cos\\theta)$ "
                "y truncando los divergentes:"
            ),
            latex=(
                r"u(r, \theta) = \sum_{\ell=0}^{\infty} A_\ell\, r^\ell\, "
                r"P_\ell(\cos\theta)."
            ),
            level="basic",
        )

    def _compute_coefficient(
        self,
        steps: list[Step],
        f_expr_xi: sp.Basic,
        xi: sp.Symbol,
        R_sym: sp.Symbol,
        ell: sp.Symbol,
        f_latex: str,
    ) -> sp.Basic:
        # A_ell = (2 ell + 1) / (2 R^ell) integral from -1 to 1 of f(xi) P_ell(xi) dxi.
        #
        # We keep the integral UNEVALUATED. SymPy's `integrate` of
        # `sp.legendre(ell, xi)` with symbolic ell returns a closed
        # formula that is incorrect at ell = 0 (the boundary terms
        # collapse wrongly). Leaving it as `sp.Integral` is honest
        # pedagogically and lets the student (or a downstream
        # numerical step) evaluate by substituting a specific ell and
        # calling `.doit()`.
        integrand = f_expr_xi * sp.legendre(ell, xi)
        integral = sp.Integral(integrand, (xi, -1, 1))
        A_ell = (2 * ell + 1) / (2 * R_sym**ell) * integral

        steps.append(
            step(
                kind="initial",
                title=f"Paso 5 — Coeficientes a partir de $f(\\theta) = {f_latex}$",
                md=T.T_laplace_ball_coefficients(),
                latex=equation_chain(
                    [
                        r"A_\ell &= \frac{2\ell + 1}{2 R^\ell} "
                        r"\int_{-1}^{1} f(\arccos\xi)\, P_\ell(\xi)\, d\xi,",
                        rf"A_\ell &= {sp.latex(A_ell)}.",
                    ]
                ),
                sympy_expr=A_ell,
                level="basic",
                observations=[obs.get("ball_mean_value_3d")],
            )
        )
        return A_ell

    def _build_solution(
        self,
        A_ell: sp.Basic,
        r: sp.Symbol,
        theta: sp.Symbol,
        R_sym: sp.Symbol,
        ell: sp.Symbol,
    ) -> sp.Basic:
        term = A_ell * r**ell * sp.legendre(ell, sp.cos(theta))
        return sp.Sum(term, (ell, 0, sp.oo))

    def _step_final(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Solución (expansión multipolar)",
            md=(
                "Sustituyendo $A_\\ell$ en la superposición, obtenemos "
                "la **expansión multipolar interior** del dato $f$:"
            ),
            latex=rf"\boxed{{\; u(r, \theta) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
            observations=[obs.get("legendre_multipole_meaning")],
        )

    def _step_verification(self) -> Step:
        return step(
            kind="verification",
            title="Paso 7 — Verificación (estructural)",
            md=(
                "Cada término $r^\\ell P_\\ell(\\cos\\theta)$ es **una "
                "función armónica fundamental** del Laplaciano en "
                "esféricas. Concretamente, $\\Delta(r^\\ell P_\\ell) = 0$ "
                "se verifica componiendo:\n\n"
                "1. La parte radial $r^\\ell$ contribuye con "
                "$\\ell(\\ell + 1) r^{\\ell - 2}$ al término "
                "$(r^2 R')'/r^2$.\n"
                "2. La parte angular $P_\\ell$ contribuye con "
                "$-\\ell(\\ell + 1) P_\\ell$ al término angular "
                "(ecuación de Legendre).\n"
                "3. Los dos términos se cancelan: $\\Delta u_\\ell = 0$.\n\n"
                "Por linealidad, la superposición también es armónica."
            ),
            level="intermediate",
            observations=[obs.get("ball_mean_value_3d")],
        )

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_laplace_ball_physical_interpretation(),
            level="basic",
            observations=[obs.get("legendre_multipole_meaning")],
        )
