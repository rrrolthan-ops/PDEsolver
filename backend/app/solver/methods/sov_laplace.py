"""Separation of variables for Laplace's equation on a rectangle.

Problem covered
---------------
    u_xx + u_yy = 0          in 0 < x < a,  0 < y < b
    u(0, y) = u(a, y) = 0    (homogeneous on left & right)
    u(x, 0) = 0              (homogeneous at the bottom)
    u(x, b) = f(x)           (the only nonhomogeneous side)

This is the canonical Dirichlet-on-three-sides + data-on-the-fourth
setup that every PDE textbook uses to introduce Laplace SOV. More
general Dirichlet problems can be decomposed into four such subproblems
by superposition; we'll add that in Phase 2-Slice-B.

Key pedagogical points
----------------------
- The constant of separation forces a SIGN ASYMMETRY: one direction
  oscillates (sin/cos), the other is hyperbolic (sinh/cosh). Students
  often get the sign wrong here.
- BCs select which direction is the oscillating one (the one with
  homogeneous conditions at both ends).
- Each mode contributes `sin(nπx/a) · sinh(nπy/a)` to the solution.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class SeparationOfVariablesLaplaceRect(Method):
    """Separation of variables for Laplace's equation on [0, a] × [0, b]."""

    slug = "sov_laplace_rect"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        y = sp.Symbol("y", real=True)
        a = sp.Symbol("a", positive=True)
        b = sp.Symbol("b", positive=True)

        # ---------- Extract the boundary profile f(x) -------------------------
        # By convention we expect the nonhomogeneous BC to be `u(x, b) = f`,
        # encoded with where="y=b". If the user wired it differently, we
        # still pick the first non-"value=0" Dirichlet BC.
        f_latex = "0"
        for bc in problem.boundary_conditions:
            if bc.type == "dirichlet" and bc.value.strip() != "0":
                f_latex = bc.value
                break
        f_expr = parse_scalar_latex(f_latex, problem.parameters).subs(
            {sp.Symbol("x"): x, sp.Symbol("a"): a, sp.Symbol("b"): b}
        )

        steps: list[Step] = []

        steps.append(self._step_statement(f_latex))
        steps += self._steps_classification()
        steps.append(self._step_method_choice())
        steps += self._steps_separation(x, y)
        steps += self._steps_three_cases(a)
        steps += self._steps_Y_ode(a, b)
        steps.append(self._step_superposition(a))

        # Fourier coefficients to match u(x, b) = f(x).
        An_expr = self._steps_apply_top_bc(steps, f_expr, f_latex, a, b, x)

        solution_expr = self._build_solution_expression(An_expr, x, y, a, b)
        steps.append(self._step_final(solution_expr))

        steps += self._steps_verification(solution_expr, f_expr, x, y, a, b)
        steps.append(self._step_visualization())
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # ===========================================================================

    def _step_statement(self, f_latex: str) -> Step:
        latex = equation_chain(
            [
                r"&\nabla^2 u = u_{xx} + u_{yy} = 0,"
                r"\quad 0 < x < a,\ 0 < y < b,",
                r"&u(0, y) = u(a, y) = 0,",
                r"&u(x, 0) = 0,",
                rf"&u(x, b) = {f_latex}.",
            ]
        )
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (Laplace en rectángulo)",
            md=T.T_statement_laplace_rect(),
            latex=latex,
            level="basic",
        )

    def _steps_classification(self) -> list[Step]:
        # u_xx + u_yy = 0: A = 1, C = 1, B = 0 → Δ = -4 < 0 → elliptic.
        s = step(
            kind="classification",
            title="Paso 1 — Clasificación (elíptica)",
            md=T.T_classification_intro(),
            latex=equation_chain(
                [
                    r"A &= 1,\quad B = 0,\quad C = 1,",
                    r"\Delta &= B^2 - 4AC = -4 < 0,",
                    r"&\Rightarrow \text{EDP elíptica}.",
                ]
            ),
            level="basic",
            observations=[obs.get("laplace_max_principle")],
        )
        return [s]

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método: separación de variables",
            md=(
                "El dominio es **rectangular** y las condiciones de "
                "Dirichlet son **homogéneas en tres lados** (sólo "
                "$u(x, b) = f(x)$ es no nula). Esto encaja con "
                "separación de variables: la dirección $x$, con BCs "
                "homogéneas en ambos extremos, dará el problema de "
                "Sturm-Liouville oscilatorio. La dirección $y$ heredará "
                "una EDO con autovalores ya conocidos y se ajustará a la "
                "frontera no homogénea.\n\n"
                "**Alternativas descartadas.** Una función de Green daría "
                "la solución directamente, pero requiere integrar contra "
                "el núcleo de Poisson — más costoso de explicar para un "
                "primer encuentro. La transformada de Fourier no aplica "
                "directamente en un dominio acotado."
            ),
            level="basic",
        )

    def _steps_separation(self, x: sp.Symbol, y: sp.Symbol) -> list[Step]:
        X = sp.Function("X")
        Y = sp.Function("Y")
        ansatz = X(x) * Y(y)
        u_xx = sp.diff(ansatz, x, 2)
        u_yy = sp.diff(ansatz, y, 2)

        s_ansatz = step(
            kind="development",
            title="Paso 3.1 — Ansatz separable",
            md=T.T_sov_ansatz(),
            latex=r"u(x, y) = X(x)\, Y(y).",
            level="basic",
            observations=[obs.get("sov_why_separable")],
        )
        s_subs = step(
            kind="development",
            title="Paso 3.2 — Sustituimos en $\\nabla^2 u = 0$",
            md="Calculamos las dos derivadas segundas y sumamos:",
            latex=equation_chain(
                [
                    rf"u_{{xx}} &= {sp.latex(u_xx)},",
                    rf"u_{{yy}} &= {sp.latex(u_yy)},",
                    r"X''(x)\, Y(y) + X(x)\, Y''(y) &= 0.",
                ]
            ),
            level="basic",
        )
        s_divide = step(
            kind="development",
            title="Paso 3.3 — Dividimos por $X(x)\\, Y(y)$",
            md=(
                "Para separar las dependencias en $x$ y en $y$, llevamos "
                "cada lado a su propia variable:"
            ),
            latex=r"\frac{X''(x)}{X(x)} = -\frac{Y''(y)}{Y(y)}.",
            level="basic",
        )
        s_constant = step(
            kind="development",
            title="Paso 3.4 — Constante de separación",
            md=T.T_laplace_signs(),
            latex=equation_chain(
                [
                    r"\frac{X''(x)}{X(x)} = -\frac{Y''(y)}{Y(y)} &= -\lambda,",
                    r"X'' + \lambda X &= 0 \quad \text{(oscilatoria)},",
                    r"Y'' - \lambda Y &= 0 \quad \text{(hiperbólica)}.",
                ]
            ),
            level="basic",
            observations=[obs.get("laplace_sign_swap")],
        )
        return [s_ansatz, s_subs, s_divide, s_constant]

    def _steps_three_cases(self, a: sp.Symbol) -> list[Step]:
        s_intro = step(
            kind="development",
            title="Paso 3.5 — Tres casos en $\\lambda$ para la EDO en $X$",
            md=T.T_sov_three_cases_intro(),
            level="basic",
            observations=[obs.get("sov_why_three_cases")],
        )
        s_pos_only = step(
            kind="development",
            title="Sólo $\\lambda > 0$ sobrevive a $X(0) = X(a) = 0$",
            md=(
                "El análisis es **idéntico** al de la ecuación del calor "
                "1D: $\\lambda \\le 0$ obliga a $X \\equiv 0$. El caso "
                "$\\lambda > 0$ produce el problema de Sturm-Liouville "
                "estándar."
            ),
            latex=equation_chain(
                [
                    r"X(x) &= A\cos(\mu x) + B\sin(\mu x),\quad \mu = \sqrt{\lambda},",
                    r"X(0) = 0 &\Rightarrow A = 0,",
                    r"X(a) = 0 &\Rightarrow \sin(\mu a) = 0 \Rightarrow \mu a = n\pi,",
                    r"\boxed{\;\lambda_n = (n\pi/a)^2,\quad X_n(x) = \sin(n\pi x/a).\;}",
                ]
            ),
            level="basic",
            observations=[obs.get("sturm_liouville_theorem")],
        )
        return [s_intro, s_pos_only]

    def _steps_Y_ode(self, a: sp.Symbol, b: sp.Symbol) -> list[Step]:
        s_solve = step(
            kind="development",
            title="Paso 3.6 — Resolución de la EDO en $Y$",
            md=T.T_laplace_Y_ode(),
            latex=equation_chain(
                [
                    r"Y_n'' - \lambda_n Y_n &= 0,\quad \lambda_n = (n\pi/a)^2,",
                    r"&\text{característica: } r^2 = \lambda_n,",
                    r"&r = \pm n\pi/a,",
                    r"Y_n(y) &= C_n \sinh(n\pi y/a) + D_n \cosh(n\pi y/a),",
                    r"Y_n(0) = 0 &\Rightarrow D_n = 0,",
                    r"Y_n(y) &= C_n \sinh(n\pi y/a).",
                ]
            ),
            level="basic",
        )
        return [s_solve]

    def _step_superposition(self, a: sp.Symbol) -> Step:
        return step(
            kind="development",
            title="Paso 3.7 — Superposición",
            md=(
                "La solución general es la combinación lineal de todos "
                "los productos $X_n(x) Y_n(y)$:"
            ),
            latex=(
                r"u(x, y) = \sum_{n=1}^{\infty} A_n\, "
                r"\sin\!\bigl(\tfrac{n\pi x}{a}\bigr)\, "
                r"\sinh\!\bigl(\tfrac{n\pi y}{a}\bigr)."
            ),
            level="basic",
        )

    def _steps_apply_top_bc(
        self,
        steps: list[Step],
        f_expr: sp.Basic,
        f_latex: str,
        a: sp.Symbol,
        b: sp.Symbol,
        x: sp.Symbol,
    ) -> sp.Basic:
        n = sp.Symbol("n", integer=True, positive=True)
        steps.append(
            step(
                kind="initial",  # acting as "data condition" here
                title="Paso 5 — Aplicación de la condición $u(x, b) = f(x)$",
                md=(
                    "Evaluando la serie en $y = b$:\n\n"
                    "$$f(x) = \\sum_{n=1}^{\\infty} A_n\\, "
                    "\\sinh\\!\\bigl(\\tfrac{n\\pi b}{a}\\bigr)\\, "
                    "\\sin\\!\\bigl(\\tfrac{n\\pi x}{a}\\bigr).$$\n\n"
                    "Reconocemos el desarrollo de Fourier en senos de "
                    "$f$ sobre $[0, a]$. Despejando $A_n$ con la "
                    "**ortogonalidad** de los senos:"
                ),
                latex=(
                    r"A_n = \frac{2}{a\, \sinh(n\pi b/a)} "
                    r"\int_0^a f(x)\, \sin\!\bigl(\tfrac{n\pi x}{a}\bigr)\, dx."
                ),
                level="basic",
                observations=[obs.get("fourier_orthogonality")],
            )
        )

        steps.append(
            step(
                kind="initial",
                title=f"Paso 5.1 — Sustituimos $f(x) = {f_latex}$",
                md="Procedemos con la integral:",
                latex=(
                    rf"A_n = \frac{{2}}{{a\, \sinh(n\pi b/a)}} "
                    rf"\int_0^a {sp.latex(f_expr)}\, "
                    r"\sin\!\bigl(\tfrac{n\pi x}{a}\bigr)\, dx."
                ),
                level="basic",
            )
        )

        integral = sp.integrate(f_expr * sp.sin(n * sp.pi * x / a), (x, 0, a))
        An = sp.simplify(
            sp.Rational(2) / (a * sp.sinh(n * sp.pi * b / a)) * integral
        )
        An = sp.simplify(An.subs(sp.cos(sp.pi * n), (-1) ** n))

        steps.append(
            step(
                kind="initial",
                title="Resultado de la integral",
                md="Integrando simbólicamente:",
                latex=rf"A_n = {sp.latex(An)}.",
                sympy_expr=An,
                level="basic",
            )
        )
        return An

    def _build_solution_expression(
        self,
        An: sp.Basic,
        x: sp.Symbol,
        y: sp.Symbol,
        a: sp.Symbol,
        b: sp.Symbol,
    ) -> sp.Basic:
        n = sp.Symbol("n", integer=True, positive=True)
        term = An * sp.sin(n * sp.pi * x / a) * sp.sinh(n * sp.pi * y / a)
        return sp.Sum(term, (n, 1, sp.oo))

    def _step_final(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Solución",
            md=(
                "Sustituyendo los coeficientes en la superposición, la "
                "solución es la siguiente serie:"
            ),
            latex=rf"\boxed{{\; u(x, y) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        f_expr: sp.Basic,
        x: sp.Symbol,
        y: sp.Symbol,
        a: sp.Symbol,
        b: sp.Symbol,
    ) -> list[Step]:
        term = solution_expr.function if isinstance(solution_expr, sp.Sum) else solution_expr
        u_xx = sp.diff(term, x, 2)
        u_yy = sp.diff(term, y, 2)
        residual = sp.simplify(u_xx + u_yy)
        pde_ok = bool(residual == 0)

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=T.T_verification_intro(),
            level="basic",
        )
        s_pde = step(
            kind="verification",
            title="Verificación: $\\nabla^2 u = 0$",
            md=(
                "Calculamos las dos derivadas segundas. El factor "
                "$\\sin(n\\pi x/a)$ contribuye con $-(n\\pi/a)^2$ por "
                "$u_{xx}$, y el factor $\\sinh(n\\pi y/a)$ contribuye con "
                "$+(n\\pi/a)^2$ por $u_{yy}$. **Se cancelan exactamente.**"
                if pde_ok
                else "**Atención:** el residuo no se anuló."
            ),
            latex=rf"u_{{xx}} + u_{{yy}} = {sp.latex(residual)}.",
            level="intermediate",
        )

        # Boundary checks (term-by-term, since the series is by construction).
        bc_left = sp.simplify(term.subs(x, 0))
        bc_right = sp.simplify(term.subs(x, a))
        bc_bottom = sp.simplify(term.subs(y, 0))
        s_bc = step(
            kind="verification",
            title="Verificación: tres lados homogéneos",
            md=(
                "El factor $\\sin(n\\pi x/a)$ se anula en $x = 0$ y "
                "$x = a$; el factor $\\sinh(n\\pi y/a)$ se anula en "
                "$y = 0$. Las tres condiciones homogéneas se cumplen "
                "término a término."
            ),
            latex=(
                r"\begin{aligned}"
                rf"u_n(0, y) &= {sp.latex(bc_left)},\\"
                rf"u_n(a, y) &= {sp.latex(bc_right)},\\"
                rf"u_n(x, 0) &= {sp.latex(bc_bottom)}."
                r"\end{aligned}"
            ),
            level="intermediate",
        )

        s_bc_top = step(
            kind="verification",
            title="Verificación: $u(x, b) = f(x)$",
            md=(
                "Por construcción de los $A_n$ como coeficientes de "
                "Fourier de $f$, la serie evaluada en $y = b$ reproduce "
                "$f(x)$."
            ),
            latex=(
                r"u(x, b) = \sum_{n=1}^{\infty} A_n\, "
                r"\sinh(n\pi b/a)\, \sin(n\pi x/a) "
                rf"\overset{{!}}{{=}} {sp.latex(f_expr)}."
            ),
            level="intermediate",
        )
        return [s_intro, s_pde, s_bc, s_bc_top]

    def _step_visualization(self) -> Step:
        return step(
            kind="visualization",
            title="Paso 8 — Visualización",
            md=(
                "El panel adjunto muestra $u(x, y)$ como superficie. "
                "Observa cómo el dato de frontera del lado caliente "
                "$y = b$ se **decae exponencialmente** al bajar hacia "
                "$y = 0$: los modos altos (con $n$ grande) decaen más "
                "rápido al alejarse de la frontera porque "
                "$\\sinh(n\\pi y/a) / \\sinh(n\\pi b/a) \\to 0$ "
                "rápidamente. Es el suavizado característico de las "
                "EDPs elípticas."
            ),
            level="basic",
        )

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_laplace_physical_interpretation(),
            level="basic",
            observations=[obs.get("laplace_max_principle")],
        )
