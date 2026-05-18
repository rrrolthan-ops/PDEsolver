"""Simply supported Euler-Bernoulli beam: EI u'''' = q(x).

Problem covered
---------------
    EI u''''(x) = q(x)     on 0 < x < L
    u(0) = u(L) = 0        (simply supported, no deflection)
    u''(0) = u''(L) = 0    (no bending moment)

Method
------
Sine-series expansion: phi_n(x) = sin(n pi x/L) satisfies all four BCs
by construction. Project q onto sines, then A_n = q_n / (EI (n pi/L)^4).
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class BiharmonicBeam(Method):
    """Simply supported beam under distributed load."""

    slug = "biharmonic_beam"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        L = sp.Symbol("L", positive=True)
        EI = sp.Symbol("EI", positive=True)
        n = sp.Symbol("n", integer=True, positive=True)

        # Source term q(x).
        q_str = problem.source_term or "1"
        q_expr = parse_scalar_latex(q_str, problem.parameters).subs(
            {sp.Symbol("x"): x, sp.Symbol("L"): L}
        )

        steps: list[Step] = []
        steps.append(self._step_statement(q_str))
        steps.append(self._step_classification())
        steps.append(self._step_method_choice())
        steps += self._steps_expansion()
        A_n = self._compute_coefficients(steps, q_expr, q_str, x, L, n, EI)
        solution_expr = self._build_solution(A_n, x, L, n)
        steps.append(self._step_final(solution_expr))
        steps += self._steps_verification(solution_expr, q_expr, EI, x, L)
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # ---------------------------------------------------------------------

    def _step_statement(self, q_str: str) -> Step:
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (viga simplemente apoyada)",
            md=T.T_statement_biharmonic_beam(),
            latex=equation_chain(
                [
                    rf"&EI\, u''''(x) = {q_str},\quad 0 < x < L,",
                    r"&u(0) = u(L) = 0,\quad u''(0) = u''(L) = 0.",
                ]
            ),
            level="basic",
            observations=[obs.get("biharmonic_four_bcs")],
        )

    def _step_classification(self) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — EDO lineal de cuarto orden",
            md=(
                "$EI\\, u'''' = q$ es una EDO **lineal con coeficientes "
                "constantes** de orden 4. La parte homogénea $u'''' = 0$ "
                "tiene cuatro soluciones independientes $1, x, x^2, x^3$. "
                "Las cuatro BCs eliminan estas, dejando una solución "
                "particular única."
            ),
            level="basic",
        )

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método: expansión en serie de senos",
            md=T.T_biharmonic_method_choice(),
            level="basic",
        )

    def _steps_expansion(self) -> list[Step]:
        s = step(
            kind="development",
            title="Paso 3 — Sustitución término a término",
            md=T.T_biharmonic_expansion(),
            latex=equation_chain(
                [
                    r"u(x) &= \sum_{n=1}^{\infty} A_n \sin\!\bigl(\tfrac{n\pi x}{L}\bigr),",
                    r"u''''(x) &= \sum_{n=1}^{\infty} A_n \left(\tfrac{n\pi}{L}\right)^4 "
                    r"\sin\!\bigl(\tfrac{n\pi x}{L}\bigr),",
                    r"q(x) &= \sum_{n=1}^{\infty} q_n \sin\!\bigl(\tfrac{n\pi x}{L}\bigr),",
                    r"EI\, (n\pi/L)^4 A_n &= q_n.",
                ]
            ),
            level="basic",
        )
        return [s]

    def _compute_coefficients(
        self,
        steps: list[Step],
        q_expr: sp.Basic,
        q_str: str,
        x: sp.Symbol,
        L: sp.Symbol,
        n: sp.Symbol,
        EI: sp.Symbol,
    ) -> sp.Basic:
        q_n = sp.simplify(
            sp.Rational(2) / L * sp.integrate(q_expr * sp.sin(n * sp.pi * x / L), (x, 0, L))
        )
        q_n = sp.simplify(q_n.subs(sp.cos(sp.pi * n), (-1) ** n))
        A_n = sp.simplify(q_n / (EI * (n * sp.pi / L) ** 4))

        steps.append(
            step(
                kind="initial",
                title=f"Paso 5 — Cálculo de los coeficientes para $q(x) = {q_str}$",
                md=(
                    "Proyectamos $q$ sobre $\\sin(n\\pi x/L)$ usando "
                    "ortogonalidad estándar:"
                ),
                latex=equation_chain(
                    [
                        r"q_n &= \frac{2}{L} \int_0^L q(x)\, "
                        r"\sin\!\bigl(\tfrac{n\pi x}{L}\bigr) dx "
                        rf"= {sp.latex(q_n)},",
                        rf"A_n &= \frac{{q_n}}{{EI\, (n\pi/L)^4}} = {sp.latex(A_n)}.",
                    ]
                ),
                sympy_expr=A_n,
                level="basic",
                observations=[obs.get("fourier_orthogonality")],
            )
        )
        return A_n

    def _build_solution(
        self,
        A_n: sp.Basic,
        x: sp.Symbol,
        L: sp.Symbol,
        n: sp.Symbol,
    ) -> sp.Basic:
        return sp.Sum(A_n * sp.sin(n * sp.pi * x / L), (n, 1, sp.oo))

    def _step_final(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Deflexión de la viga",
            md="Sustituyendo $A_n$ en la serie:",
            latex=rf"\boxed{{\; u(x) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        q_expr: sp.Basic,
        EI: sp.Symbol,
        x: sp.Symbol,
        L: sp.Symbol,
    ) -> list[Step]:
        term = solution_expr.function if isinstance(solution_expr, sp.Sum) else solution_expr
        u_4 = sp.diff(term, x, 4)
        bc0 = sp.simplify(term.subs(x, 0))
        bcL = sp.simplify(term.subs(x, L))
        bc_pp0 = sp.simplify(sp.diff(term, x, 2).subs(x, 0))
        bc_ppL = sp.simplify(sp.diff(term, x, 2).subs(x, L))

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "Comprobamos que $EI u''''$ produce $q$ término-a-término "
                "y que las cuatro BCs se satisfacen por construcción."
            ),
            level="basic",
        )
        s_pde = step(
            kind="verification",
            title="Verificación de la EDP (término genérico)",
            md=(
                "$d^4/dx^4 \\sin(n\\pi x/L) = (n\\pi/L)^4 \\sin(n\\pi x/L)$, "
                "y el factor $A_n \\cdot EI (n\\pi/L)^4$ coincide con "
                "$q_n$ por construcción."
            ),
            latex=rf"EI\, u_n''''(x) = {sp.latex(sp.simplify(EI * u_4))}.",
            level="intermediate",
        )
        s_bc = step(
            kind="verification",
            title="Verificación de las cuatro BCs",
            md=(
                "$\\sin(n\\pi x/L)$ y $-(n\\pi/L)^2 \\sin(n\\pi x/L)$ "
                "se anulan en $x = 0$ y $x = L$ para todo $n$ entero."
            ),
            latex=equation_chain(
                [
                    rf"u_n(0) &= {sp.latex(bc0)},\quad u_n(L) = {sp.latex(bcL)},",
                    rf"u_n''(0) &= {sp.latex(bc_pp0)},\quad u_n''(L) = {sp.latex(bc_ppL)}.",
                ]
            ),
            level="intermediate",
        )
        return [s_intro, s_pde, s_bc]

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_biharmonic_physical_interpretation(),
            level="basic",
            observations=[obs.get("biharmonic_n4_decay")],
        )
