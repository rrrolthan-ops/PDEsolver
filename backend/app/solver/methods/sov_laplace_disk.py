"""Separation of variables for Laplace's equation on a disk.

Problem covered
---------------
    Δu = 0           in r < R, θ ∈ [0, 2π)
    u(R, θ) = f(θ)   (Dirichlet on the boundary)
    bounded at r = 0, periodic in θ

In polar coordinates, Δu = u_rr + (1/r) u_r + (1/r²) u_θθ.

Key pedagogical points
----------------------
- Periodicity (NOT a Dirichlet condition) is what quantises the modes.
- Regularity at the origin discards r^(-n) and ln r.
- The series sums up to the Poisson integral formula, which we display
  as a culminating remark (without integrating it ourselves).
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class SeparationOfVariablesLaplaceDisk(Method):
    """Laplace on a disk by separation in polar coordinates."""

    slug = "sov_laplace_disk"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        r = sp.Symbol("r", nonnegative=True)
        theta = sp.Symbol("theta", real=True)
        R = sp.Symbol("R", positive=True)

        # Extract f(theta) from the boundary condition.
        f_latex = "0"
        for bc in problem.boundary_conditions:
            if bc.type == "dirichlet" and bc.value.strip() != "0":
                f_latex = bc.value
                break
        f_expr = parse_scalar_latex(f_latex, problem.parameters).subs(
            {sp.Symbol("theta"): theta, sp.Symbol("R"): R}
        )

        steps: list[Step] = []
        steps.append(self._step_statement(f_latex))
        steps.append(self._step_classification())
        steps.append(self._step_method_choice())
        steps += self._steps_separation()
        steps.append(self._step_angular())
        steps.append(self._step_radial())
        steps.append(self._step_superposition())

        a_n_expr, b_n_expr, a0_expr = self._steps_boundary(
            steps, f_expr, f_latex, theta, R
        )

        solution_expr = self._build_solution(a0_expr, a_n_expr, b_n_expr, r, theta, R)
        steps.append(self._step_final(solution_expr))
        steps.append(self._step_poisson_kernel())
        steps += self._steps_verification(solution_expr, f_expr, r, theta, R)
        steps.append(self._step_visualization())
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # -----------------------------------------------------------------------

    def _step_statement(self, f_latex: str) -> Step:
        latex = equation_chain(
            [
                r"&\Delta u = u_{rr} + \tfrac{1}{r} u_r + "
                r"\tfrac{1}{r^2} u_{\theta\theta} = 0,\quad r < R,\ \theta \in [0, 2\pi),",
                rf"&u(R, \theta) = {f_latex},",
                r"&\text{regularidad en } r = 0,\quad u\text{ es } 2\pi\text{-periódica en }\theta.",
            ]
        )
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (Laplace en disco)",
            md=T.T_statement_laplace_disk(),
            latex=latex,
            level="basic",
        )

    def _step_classification(self) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Clasificación (elíptica)",
            md=(
                "El Laplaciano es elíptico en cualquier sistema de "
                "coordenadas. Las soluciones son armónicas y heredan el "
                "principio del máximo y el teorema del valor medio."
            ),
            observations=[obs.get("laplace_max_principle")],
            level="basic",
        )

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Separación en coordenadas polares",
            md=T.T_disk_method_choice(),
            level="basic",
        )

    def _steps_separation(self) -> list[Step]:
        s_ansatz = step(
            kind="development",
            title="Paso 3.1 — Ansatz separable",
            md=T.T_sov_ansatz(),
            latex=r"u(r, \theta) = P(r)\, \Phi(\theta).",
            level="basic",
            observations=[obs.get("sov_why_separable")],
        )
        s_separate = step(
            kind="development",
            title="Paso 3.2 — Separamos en dos EDOs",
            md=(
                "Sustituimos $u = P\\Phi$ en $r^2 \\Delta u = 0$ "
                "(multiplicar por $r^2$ libera de los coeficientes "
                "variables más molestos):"
            ),
            latex=equation_chain(
                [
                    r"r^2 P''\Phi + r P'\Phi + P\Phi'' &= 0,",
                    r"\frac{r^2 P'' + r P'}{P} = -\frac{\Phi''}{\Phi} &= \lambda.",
                ]
            ),
            level="basic",
        )
        return [s_ansatz, s_separate]

    def _step_angular(self) -> Step:
        return step(
            kind="boundary",
            title="Paso 4 — Periodicidad fija los autovalores",
            md=T.T_disk_angular_periodicity(),
            latex=equation_chain(
                [
                    r"\Phi'' + \lambda \Phi &= 0,",
                    r"\Phi(\theta + 2\pi) &= \Phi(\theta),",
                    r"&\Rightarrow \lambda_n = n^2,\ n = 0, 1, 2, \dots",
                    r"&\Rightarrow \Phi_n \in \{\cos(n\theta),\ \sin(n\theta)\}.",
                ]
            ),
            level="basic",
            observations=[obs.get("disk_periodicity")],
        )

    def _step_radial(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.6 — EDO radial (ecuación de Euler)",
            md=T.T_disk_radial_euler(),
            latex=equation_chain(
                [
                    r"r^2 P'' + r P' - n^2 P &= 0,",
                    r"\text{ansatz } P = r^p &\Rightarrow p^2 = n^2,",
                    r"\Rightarrow P(r) &= A r^n + B r^{-n}\quad(n \geq 1),",
                    r"\Rightarrow P(r) &= A + B \ln r\quad(n = 0),",
                    r"\text{regularidad en } r = 0 &\Rightarrow B = 0.",
                ]
            ),
            level="basic",
            observations=[obs.get("disk_origin_regularity")],
        )

    def _step_superposition(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.7 — Superposición",
            md=(
                "Combinando todos los modos angulares (incluido $n = 0$) "
                "con sus partes radiales regulares:"
            ),
            latex=(
                r"u(r, \theta) = \tfrac{a_0}{2} + \sum_{n=1}^{\infty} "
                r"r^n\bigl[a_n \cos(n\theta) + b_n \sin(n\theta)\bigr]."
            ),
            level="basic",
        )

    def _steps_boundary(
        self,
        steps: list[Step],
        f_expr: sp.Basic,
        f_latex: str,
        theta: sp.Symbol,
        R: sp.Symbol,
    ) -> tuple[sp.Basic, sp.Basic, sp.Basic]:
        n = sp.Symbol("n", integer=True, positive=True)

        steps.append(
            step(
                kind="initial",
                title="Paso 5 — Aplicación del dato $u(R, \\theta) = f(\\theta)$",
                md=T.T_disk_fourier_coefficients(),
                latex=equation_chain(
                    [
                        r"a_0 &= \frac{1}{\pi} \int_0^{2\pi} f(\theta)\, d\theta,",
                        r"a_n &= \frac{1}{\pi R^n} \int_0^{2\pi} f(\theta) \cos(n\theta)\, d\theta,",
                        r"b_n &= \frac{1}{\pi R^n} \int_0^{2\pi} f(\theta) \sin(n\theta)\, d\theta.",
                    ]
                ),
                level="basic",
                observations=[obs.get("fourier_orthogonality")],
            )
        )

        steps.append(
            step(
                kind="initial",
                title=f"Paso 5.1 — Sustituimos $f(\\theta) = {f_latex}$",
                md="Procedemos con las integrales sobre $[0, 2\\pi]$:",
                level="basic",
            )
        )

        a0_integral = sp.integrate(f_expr, (theta, 0, 2 * sp.pi))
        a0 = sp.simplify(a0_integral / sp.pi)

        an_integral = sp.integrate(f_expr * sp.cos(n * theta), (theta, 0, 2 * sp.pi))
        an = sp.simplify(an_integral / (sp.pi * R**n))
        an = sp.simplify(an.subs(sp.cos(2 * sp.pi * n), 1).subs(sp.sin(2 * sp.pi * n), 0))

        bn_integral = sp.integrate(f_expr * sp.sin(n * theta), (theta, 0, 2 * sp.pi))
        bn = sp.simplify(bn_integral / (sp.pi * R**n))
        bn = sp.simplify(bn.subs(sp.cos(2 * sp.pi * n), 1).subs(sp.sin(2 * sp.pi * n), 0))

        steps.append(
            step(
                kind="initial",
                title="Resultado de las integrales",
                md="Integrando simbólicamente:",
                latex=equation_chain(
                    [
                        rf"a_0 &= {sp.latex(a0)},",
                        rf"a_n &= {sp.latex(an)},",
                        rf"b_n &= {sp.latex(bn)}.",
                    ]
                ),
                level="basic",
            )
        )

        return an, bn, a0

    def _build_solution(
        self,
        a0: sp.Basic,
        an: sp.Basic,
        bn: sp.Basic,
        r: sp.Symbol,
        theta: sp.Symbol,
        R: sp.Symbol,
    ) -> sp.Basic:
        n = sp.Symbol("n", integer=True, positive=True)
        term = r**n * (an * sp.cos(n * theta) + bn * sp.sin(n * theta))
        return a0 / 2 + sp.Sum(term, (n, 1, sp.oo))

    def _step_final(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Solución",
            md="Sustituyendo en la superposición:",
            latex=rf"\boxed{{\; u(r, \theta) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    def _step_poisson_kernel(self) -> Step:
        return step(
            kind="final",
            title="Paso 6.1 — Forma cerrada: la fórmula integral de Poisson",
            md=T.T_disk_poisson_kernel_note(),
            level="intermediate",
            observations=[obs.get("disk_mean_value")],
        )

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        f_expr: sp.Basic,
        r: sp.Symbol,
        theta: sp.Symbol,
        R: sp.Symbol,
    ) -> list[Step]:
        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "Comprobamos que cada término satisface $\\Delta u = 0$ "
                "en polares y la condición de frontera."
            ),
            level="basic",
        )

        # Verify the generic n-term: u_n = r^n cos(nθ) (or sin) satisfies Δu = 0.
        n = sp.Symbol("n", integer=True, positive=True)
        u_n_cos = r**n * sp.cos(n * theta)
        laplacian = sp.diff(u_n_cos, r, 2) + sp.diff(u_n_cos, r) / r + sp.diff(u_n_cos, theta, 2) / r**2
        residual = sp.simplify(laplacian)
        pde_ok = bool(residual == 0)

        s_pde = step(
            kind="verification",
            title="Verificación: cada término es armónico",
            md=(
                "Calculamos $\\Delta(r^n \\cos(n\\theta))$ en polares. "
                "Las dos primeras derivadas radiales suman "
                "$n^2 r^{n-2} \\cos(n\\theta)$, y la derivada angular "
                "segunda da $-n^2 r^{n-2} \\cos(n\\theta)$. **Se cancelan "
                "exactamente.**"
                if pde_ok
                else "**Atención:** el residuo no se anuló."
            ),
            latex=rf"\Delta(r^n \cos(n\theta)) = {sp.latex(residual)}.",
            level="intermediate",
        )

        s_bc = step(
            kind="verification",
            title="Verificación: $u(R, \\theta) = f(\\theta)$",
            md=(
                "Por construcción de los coeficientes como serie de "
                "Fourier de $f$ sobre $[0, 2\\pi]$:"
            ),
            latex=(
                rf"u(R, \theta) \overset{{!}}{{=}} {sp.latex(f_expr)}."
            ),
            level="intermediate",
        )
        return [s_intro, s_pde, s_bc]

    def _step_visualization(self) -> Step:
        return step(
            kind="visualization",
            title="Paso 8 — Visualización",
            md=(
                "Para ver la solución, graficamos $u(x, y) = u(r, \\theta)$ "
                "con $x = r\\cos\\theta$, $y = r\\sin\\theta$. Observa "
                "cómo el dato de frontera $f(\\theta)$ se **suaviza al "
                "entrar al disco**: los modos angulares altos (con $n$ "
                "grande) decaen como $(r/R)^n$, que es rápido cerca del "
                "centro."
            ),
            level="basic",
        )

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_disk_physical_interpretation(),
            level="basic",
            observations=[obs.get("disk_mean_value")],
        )
