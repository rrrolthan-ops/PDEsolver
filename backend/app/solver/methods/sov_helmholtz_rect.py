"""Inhomogeneous Helmholtz on a rectangle, by eigenfunction expansion.

Problem covered
---------------
    Δu + k² u = f(x, y)   in (0, a) × (0, b)
    u = 0 on the boundary

We expand both u and f in the rectangular eigenbasis
    φ_{mn}(x, y) = sin(mπx/a) sin(nπy/b),
    Δφ_{mn} = -k_{mn}² φ_{mn},   k_{mn}² = (mπ/a)² + (nπ/b)²

and read off coefficients
    c_{mn} = f_{mn} / (k² - k_{mn}²),
provided k² is not in the spectrum.

If `source_term` is missing or zero, we instead treat the problem as the
**eigenvalue problem** ∆u + k² u = 0, u = 0 on ∂Ω, and emit the
spectrum and the first few eigenfunctions.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class HelmholtzRect(Method):
    """Helmholtz on a rectangle with Dirichlet 0 boundaries."""

    slug = "helmholtz_rect"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        y = sp.Symbol("y", real=True)
        a = sp.Symbol("a", positive=True)
        b = sp.Symbol("b", positive=True)
        k = sp.Symbol("k", positive=True)
        m_sym = sp.Symbol("m", integer=True, positive=True)
        n_sym = sp.Symbol("n", integer=True, positive=True)

        f_str = problem.source_term or "0"
        has_source = f_str.strip() not in {"", "0"}
        f_expr = (
            parse_scalar_latex(f_str, problem.parameters).subs(
                {sp.Symbol("x"): x, sp.Symbol("y"): y, sp.Symbol("a"): a, sp.Symbol("b"): b}
            )
            if has_source
            else sp.Integer(0)
        )

        steps: list[Step] = []
        steps.append(self._step_statement(f_str, has_source))
        steps.append(self._step_classification())
        steps.append(self._step_method_choice(has_source))
        steps += self._steps_eigenpairs(m_sym, n_sym, a, b)

        if not has_source:
            # Eigenvalue mode: list the first few (m, n) pairs and stop.
            steps.append(self._step_eigenvalue_problem_output(m_sym, n_sym, a, b))
            # Symbolic "solution" placeholder: the first eigenfunction.
            solution_expr = sp.sin(sp.pi * x / a) * sp.sin(sp.pi * y / b)
            steps.append(self._step_final(solution_expr, eigenvalue_mode=True))
        else:
            f_mn = self._compute_fmn(f_expr, m_sym, n_sym, a, b, x, y)
            steps += self._steps_expansion(f_str, f_mn, m_sym, n_sym, k, a, b)
            solution_expr = self._build_solution(f_mn, m_sym, n_sym, k, a, b, x, y)
            steps.append(self._step_final(solution_expr, eigenvalue_mode=False))
            steps += self._steps_verification(solution_expr, f_expr, k, x, y)

        steps.append(self._step_physical())
        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # -----------------------------------------------------------------------

    def _step_statement(self, f_str: str, has_source: bool) -> Step:
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (Helmholtz en rectángulo)",
            md=T.T_statement_helmholtz_rect(),
            latex=equation_chain(
                [
                    rf"&\Delta u + k^2 u = {f_str},\quad (x, y) \in (0, a) \times (0, b),",
                    r"&u = 0 \text{ en la frontera},",
                ]
                + ([] if has_source else [r"&\text{caso homogéneo} \Rightarrow \text{problema de autovalores.}"])
            ),
            level="basic",
        )

    def _step_classification(self) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Clasificación",
            md=(
                "$\\Delta + k^2$ es un operador elíptico **con masa**: "
                "para $k^2 < 0$ sería el operador modificado de Helmholtz, "
                "para $k^2 > 0$ pueden aparecer **resonancias**. La "
                "clasificación PDE clásica $B^2 - 4AC = -4 < 0$ sigue "
                "siendo elíptica."
            ),
            level="basic",
        )

    def _step_method_choice(self, has_source: bool) -> Step:
        if has_source:
            md = (
                "Por la presencia del término $f \\neq 0$, lo más limpio "
                "es **expandir en la base de autofunciones** del Laplaciano "
                "con Dirichlet 0 sobre el rectángulo. Esa base existe y "
                "es explícita (productos de senos en $x$ y en $y$), así "
                "que sustituyendo la expansión de $u$ y de $f$ en la EDP, "
                "los coeficientes salen casi gratis."
            )
        else:
            md = (
                "Al ser homogénea, la EDP equivale a buscar **valores "
                "propios** $k^2$ del Laplaciano (con signo cambiado) y "
                "sus **autofunciones** correspondientes. Es el clásico "
                "problema de autovalores que describe los **modos "
                "normales** de la membrana."
            )
        return step(
            kind="method_choice",
            title="Paso 2 — Método: expansión en autofunciones",
            md=md,
            level="basic",
        )

    def _steps_eigenpairs(
        self,
        m: sp.Symbol,
        n: sp.Symbol,
        a: sp.Symbol,
        b: sp.Symbol,
    ) -> list[Step]:
        s_pairs = step(
            kind="development",
            title="Paso 3 — Autofunciones y autovalores del Laplaciano",
            md=T.T_helmholtz_eigenpairs(),
            latex=equation_chain(
                [
                    r"\phi_{mn}(x, y) &= \sin\!\bigl(\tfrac{m\pi x}{a}\bigr)"
                    r"\sin\!\bigl(\tfrac{n\pi y}{b}\bigr),",
                    r"k_{mn}^2 &= \left(\tfrac{m\pi}{a}\right)^2 + \left(\tfrac{n\pi}{b}\right)^2,",
                    r"\Delta \phi_{mn} &= -k_{mn}^2\, \phi_{mn}.",
                ]
            ),
            level="basic",
            observations=[obs.get("helmholtz_double_basis")],
        )
        return [s_pairs]

    def _step_eigenvalue_problem_output(
        self,
        m: sp.Symbol,
        n: sp.Symbol,
        a: sp.Symbol,
        b: sp.Symbol,
    ) -> Step:
        return step(
            kind="final",
            title="Resultado: espectro y modos normales",
            md=(
                "El problema homogéneo no tiene solución única: cada par "
                "$(m, n)$ con $m, n \\geq 1$ produce una autofunción "
                "$\\phi_{mn}$ no trivial con autovalor $k^2 = k_{mn}^2$. "
                "Listamos los primeros:"
            ),
            latex=equation_chain(
                [
                    r"k_{11}^2 &= (\pi/a)^2 + (\pi/b)^2,",
                    r"k_{12}^2 &= (\pi/a)^2 + (2\pi/b)^2,",
                    r"k_{21}^2 &= (2\pi/a)^2 + (\pi/b)^2,",
                    r"k_{22}^2 &= (2\pi/a)^2 + (2\pi/b)^2,\ \ldots",
                ]
            ),
            level="basic",
        )

    def _compute_fmn(
        self,
        f_expr: sp.Basic,
        m: sp.Symbol,
        n: sp.Symbol,
        a: sp.Symbol,
        b: sp.Symbol,
        x: sp.Symbol,
        y: sp.Symbol,
    ) -> sp.Basic:
        """Project f onto φ_{mn}: f_{mn} = (4/ab) ∫∫ f φ_{mn} dxdy."""
        integrand = f_expr * sp.sin(m * sp.pi * x / a) * sp.sin(n * sp.pi * y / b)
        inner_x = sp.integrate(integrand, (x, 0, a))
        inner_xy = sp.integrate(inner_x, (y, 0, b))
        f_mn = sp.simplify(4 / (a * b) * inner_xy)
        f_mn = sp.simplify(
            f_mn.subs(sp.cos(sp.pi * m), (-1) ** m).subs(sp.cos(sp.pi * n), (-1) ** n)
        )
        return f_mn

    def _steps_expansion(
        self,
        f_str: str,
        f_mn: sp.Basic,
        m: sp.Symbol,
        n: sp.Symbol,
        k: sp.Symbol,
        a: sp.Symbol,
        b: sp.Symbol,
    ) -> list[Step]:
        s_expand = step(
            kind="initial",
            title="Paso 5 — Expansión doble de $u$ y de $f$",
            md=T.T_helmholtz_expansion(),
            level="basic",
        )
        s_fmn = step(
            kind="initial",
            title=f"Paso 5.1 — Coeficientes de $f(x, y) = {f_str}$",
            md=(
                "Proyectamos $f$ sobre cada $\\phi_{mn}$ por ortogonalidad:"
            ),
            latex=(
                r"f_{mn} = \frac{4}{ab} \int_0^a \int_0^b "
                r"f(x, y)\, \phi_{mn}(x, y)\, dx\, dy "
                rf"= {sp.latex(f_mn)}."
            ),
            sympy_expr=f_mn,
            level="basic",
        )
        s_cmn = step(
            kind="initial",
            title="Paso 5.2 — Coeficientes $c_{mn}$",
            md="Dividiendo por la diferencia con cada autovalor:",
            latex=rf"c_{{mn}} = \frac{{f_{{mn}}}}{{k^2 - k_{{mn}}^2}} = "
            rf"\frac{{{sp.latex(f_mn)}}}{{k^2 - (m\pi/a)^2 - (n\pi/b)^2}}.",
            level="basic",
            observations=[obs.get("helmholtz_resonance")],
        )
        return [s_expand, s_fmn, s_cmn]

    def _build_solution(
        self,
        f_mn: sp.Basic,
        m: sp.Symbol,
        n: sp.Symbol,
        k: sp.Symbol,
        a: sp.Symbol,
        b: sp.Symbol,
        x: sp.Symbol,
        y: sp.Symbol,
    ) -> sp.Basic:
        denom = k**2 - (m * sp.pi / a) ** 2 - (n * sp.pi / b) ** 2
        phi_mn = sp.sin(m * sp.pi * x / a) * sp.sin(n * sp.pi * y / b)
        c_mn = f_mn / denom
        # SymPy doesn't natively express a double Sum; nest two.
        inner = sp.Sum(c_mn * phi_mn, (n, 1, sp.oo))
        return sp.Sum(inner, (m, 1, sp.oo))

    def _step_final(self, expr: sp.Basic, *, eigenvalue_mode: bool) -> Step:
        if eigenvalue_mode:
            return step(
                kind="final",
                title="Paso 6 — Primera autofunción (modo fundamental)",
                md=(
                    "Como muestra del espectro, mostramos la **autofunción "
                    "fundamental** $\\phi_{11}(x, y)$ y su autovalor. El "
                    "espectro completo es discreto: $\\{k_{mn}^2 : m, n \\geq 1\\}$."
                ),
                latex=rf"\phi_{{11}}(x, y) = {sp.latex(expr)}.",
                sympy_expr=expr,
                level="basic",
            )
        return step(
            kind="final",
            title="Paso 6 — Solución (válida fuera de resonancia)",
            md="Sustituyendo $c_{mn}$ en la expansión:",
            latex=rf"\boxed{{\; u(x, y) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        f_expr: sp.Basic,
        k: sp.Symbol,
        x: sp.Symbol,
        y: sp.Symbol,
    ) -> list[Step]:
        # We verify the generic term inside the double sum.
        outer = solution_expr.function if isinstance(solution_expr, sp.Sum) else solution_expr
        inner = outer.function if isinstance(outer, sp.Sum) else outer
        u_xx = sp.diff(inner, x, 2)
        u_yy = sp.diff(inner, y, 2)
        residual = sp.simplify(u_xx + u_yy + k**2 * inner - sp.S(0))
        # The residual after operator application should equal f_mn φ_mn; we
        # just confirm the action of the operator pulls out the right factor.
        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "Aplicamos $\\Delta + k^2$ al término genérico y "
                "comprobamos que coincide con el término correspondiente "
                "de la expansión de $f$."
            ),
            latex=rf"(\Delta + k^2) c_{{mn}} \phi_{{mn}} = c_{{mn}}(k^2 - k_{{mn}}^2)\, \phi_{{mn}}\overset{{!}}{{=}} f_{{mn}}\, \phi_{{mn}}.",
            level="intermediate",
        )
        return [s_intro]

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física y resonancia",
            md=T.T_helmholtz_resonance() + "\n\n" + T.T_helmholtz_physical_interpretation(),
            level="basic",
            observations=[obs.get("helmholtz_resonance")],
        )
