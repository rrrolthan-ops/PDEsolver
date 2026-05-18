"""Green's-function solver for the 1D Poisson problem.

Problem covered
---------------
    -u''(x) = f(x)   in 0 < x < L
    u(0) = u(L) = 0

Strategy
--------
Construct the Green function G(x, ξ) of the operator -d²/dx² with
homogeneous Dirichlet BCs on [0, L], then assemble

    u(x) = ∫₀ᴸ G(x, ξ) f(ξ) dξ.

G has the "tent" shape:
    G(x, ξ) = x(L - ξ)/L   for x ≤ ξ
    G(x, ξ) = ξ(L - x)/L   for x ≥ ξ

We compute the integral symbolically by splitting at ξ = x.

Pedagogical thrust
------------------
Green's functions are *the* technique of "respond to a delta source and
integrate against the data". This is the cleanest 1D example: G is
piecewise linear, every property has a physical interpretation
(reciprocity, tent shape, derivative jump = -1).
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class GreensFunction1D(Method):
    """1D Poisson via Green's function on [0, L] with Dirichlet 0."""

    slug = "greens_function_1d"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        xi = sp.Symbol("xi", real=True, positive=True)
        L = sp.Symbol("L", positive=True)

        # Source f(x); the user passes it via `source_term` (preferred) or
        # we infer it from the equation. We default to "x*(L-x)" as a
        # textbook example if nothing is given.
        f_str = problem.source_term or "x*(L-x)"
        f_x = parse_scalar_latex(f_str, problem.parameters).subs(
            {sp.Symbol("x"): x, sp.Symbol("L"): L}
        )
        f_xi = f_x.subs(x, xi)

        steps: list[Step] = []
        steps.append(self._step_statement(f_str))
        steps.append(self._step_classification())
        steps.append(self._step_method_choice())
        steps += self._steps_green_construction(L)
        steps.append(self._step_green_formula())
        u_expr = self._integral_solution(f_xi, x, xi, L)
        steps += self._steps_apply_to_source(f_str, f_xi, x, xi, L, u_expr)
        steps.append(self._step_final(u_expr))
        steps += self._steps_verification(u_expr, f_x, x, L)
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=u_expr,
            solution_latex=sp.latex(u_expr),
        )

    # -----------------------------------------------------------------------

    def _step_statement(self, f_str: str) -> Step:
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (Poisson 1D)",
            md=T.T_statement_poisson_1d(),
            latex=equation_chain(
                [
                    rf"&-u''(x) = {f_str},\quad 0 < x < L,",
                    r"&u(0) = u(L) = 0.",
                ]
            ),
            level="basic",
        )

    def _step_classification(self) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Naturaleza del problema",
            md=(
                "Es un **problema con valores en la frontera** (BVP) "
                "para una EDO lineal de segundo orden con término "
                "independiente. La parte homogénea $-u'' = 0$ tiene "
                "soluciones lineales $u = Ax + B$; en el espacio "
                "compatible con las BCs sólo está $u \\equiv 0$. Eso "
                "garantiza **unicidad**: el operador es inyectivo."
            ),
            level="basic",
        )

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método: función de Green",
            md=T.T_greens_function_motivation(),
            level="basic",
            observations=[obs.get("green_delta_intuition")],
        )

    def _steps_green_construction(self, L: sp.Symbol) -> list[Step]:
        s_props = step(
            kind="development",
            title="Paso 3.1 — Propiedades que define $G$",
            md=T.T_greens_function_defining_properties(),
            level="basic",
        )
        s_construct = step(
            kind="development",
            title="Paso 3.2 — Construcción explícita de $G$",
            md=T.T_greens_function_construction(),
            latex=equation_chain(
                [
                    r"0 \leq x < \xi:\ G &= Ax,",
                    r"\xi < x \leq L:\ G &= C(x - L),",
                    r"\text{continuidad:}\ A\xi &= C(\xi - L),",
                    r"\text{salto:}\ C - A &= -1,",
                    r"\Rightarrow A &= \tfrac{L - \xi}{L},\ C = -\tfrac{\xi}{L}.",
                ]
            ),
            level="basic",
        )
        return [s_props, s_construct]

    def _step_green_formula(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.3 — Forma final de $G(x, \\xi)$",
            md=T.T_greens_function_final(),
            level="basic",
            observations=[obs.get("green_reciprocity")],
        )

    def _integral_solution(
        self,
        f_xi: sp.Basic,
        x: sp.Symbol,
        xi: sp.Symbol,
        L: sp.Symbol,
    ) -> sp.Basic:
        """u(x) = ∫₀ᴸ G(x, ξ) f(ξ) dξ split at ξ = x."""
        # For 0 ≤ ξ ≤ x:  G = ξ(L - x)/L   (the "x ≥ ξ" branch)
        # For x ≤ ξ ≤ L:  G = x(L - ξ)/L   (the "x ≤ ξ" branch)
        G_left = xi * (L - x) / L
        G_right = x * (L - xi) / L
        left = sp.integrate(G_left * f_xi, (xi, 0, x))
        right = sp.integrate(G_right * f_xi, (xi, x, L))
        u = sp.simplify(sp.expand(left + right))
        return u

    def _steps_apply_to_source(
        self,
        f_str: str,
        f_xi: sp.Basic,
        x: sp.Symbol,
        xi: sp.Symbol,
        L: sp.Symbol,
        u_expr: sp.Basic,
    ) -> list[Step]:
        s_setup = step(
            kind="initial",
            title=f"Paso 5 — Aplicación a $f(x) = {f_str}$",
            md=(
                "Calculamos $u(x) = \\int_0^L G(x, \\xi) f(\\xi)\\, d\\xi$ "
                "partiendo la integral en $\\xi = x$ para usar la "
                "rama correcta de $G$ en cada lado:"
            ),
            latex=(
                r"u(x) = \int_0^x \frac{\xi(L - x)}{L}\, f(\xi)\, d\xi "
                r"+ \int_x^L \frac{x(L - \xi)}{L}\, f(\xi)\, d\xi."
            ),
            level="basic",
        )
        s_result = step(
            kind="initial",
            title="Resultado de las integrales",
            md=(
                "Cada integral es polinómica en $\\xi$ (asumiendo $f$ "
                "polinómica) y se hace directamente. Sumando ambas y "
                "simplificando:"
            ),
            latex=rf"u(x) = {sp.latex(u_expr)}.",
            sympy_expr=u_expr,
            level="basic",
        )
        return [s_setup, s_result]

    def _step_final(self, u_expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Solución",
            md="La solución del problema es:",
            latex=rf"\boxed{{\; u(x) = {sp.latex(u_expr)} \;}}",
            sympy_expr=u_expr,
            level="basic",
        )

    def _steps_verification(
        self,
        u_expr: sp.Basic,
        f_x: sp.Basic,
        x: sp.Symbol,
        L: sp.Symbol,
    ) -> list[Step]:
        u_pp = sp.simplify(sp.diff(u_expr, x, 2))
        residual = sp.simplify(-u_pp - f_x)
        pde_ok = bool(residual == 0)

        u_at_0 = sp.simplify(u_expr.subs(x, 0))
        u_at_L = sp.simplify(u_expr.subs(x, L))
        bcs_ok = bool(u_at_0 == 0) and bool(u_at_L == 0)

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "Comprobamos: que $-u'' = f$ se cumple (debe ser **idéntica** "
                "en $x$, no sólo casi-puntualmente, porque $u$ es $C^2$ aquí), "
                "y que $u(0) = u(L) = 0$."
            ),
            level="basic",
        )
        s_pde = step(
            kind="verification",
            title="Verificación: $-u'' - f$",
            md=(
                "Derivamos dos veces $u$ y restamos $f$."
                if pde_ok
                else "**Atención:** el residuo no se anuló."
            ),
            latex=rf"-u''(x) - f(x) = {sp.latex(residual)}.",
            level="intermediate",
        )
        s_bc = step(
            kind="verification",
            title="Verificación: condiciones de contorno",
            md=("Evaluamos $u$ en los extremos." if bcs_ok else "**Atención:** BCs no nulas."),
            latex=equation_chain(
                [
                    rf"u(0) &= {sp.latex(u_at_0)},",
                    rf"u(L) &= {sp.latex(u_at_L)}.",
                ]
            ),
            level="intermediate",
        )
        return [s_intro, s_pde, s_bc]

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_poisson_1d_physical_interpretation(),
            level="basic",
            observations=[obs.get("green_reciprocity")],
        )
