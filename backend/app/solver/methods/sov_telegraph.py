"""Telegraph equation on a bounded interval, by separation of variables.

Problem covered
---------------
    u_tt + 2 α u_t + β u = c² u_xx       in 0 < x < L,  t > 0
    u(0, t) = u(L, t) = 0
    u(x, 0) = f(x)
    u_t(x, 0) = g(x)

Method
------
SOV gives the usual spatial Sturm-Liouville problem (same as heat/wave),
producing λ_n = (nπ/L)² and X_n(x) = sin(nπx/L). The temporal ODE is
the new ingredient:

    T_n'' + 2 α T_n' + (β + c² λ_n) T_n = 0

— a damped harmonic oscillator with three regimes per mode depending on
the sign of Δ_n = α² − β − c² λ_n. We split the analysis explicitly.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class TelegraphSOV(Method):
    """Telegraph equation on [0, L] with Dirichlet 0, SOV."""

    slug = "telegraph_sov"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        L = sp.Symbol("L", positive=True)
        alpha = sp.Symbol("alpha", positive=True)
        beta = sp.Symbol("beta", nonnegative=True)
        c = sp.Symbol("c", positive=True)
        n = sp.Symbol("n", integer=True, positive=True)

        # Parse f and g (two ICs).
        f_latex = "0"
        g_latex = "0"
        for ic in problem.initial_conditions:
            if ic.order == 0:
                f_latex = ic.value
            elif ic.order == 1:
                g_latex = ic.value
        f_expr = parse_scalar_latex(f_latex, problem.parameters).subs(
            {sp.Symbol("x"): x, sp.Symbol("L"): L}
        )
        g_expr = parse_scalar_latex(g_latex, problem.parameters).subs(
            {sp.Symbol("x"): x, sp.Symbol("L"): L}
        )

        steps: list[Step] = []
        steps.append(self._step_statement(f_latex, g_latex))
        steps.append(self._step_classification())
        steps.append(self._step_method_choice())
        steps += self._steps_separation(alpha, beta, c)
        steps.append(self._step_spatial())
        steps.append(self._step_temporal_ode(alpha, beta, c))
        steps.append(self._step_three_regimes())
        steps.append(self._step_superposition_formal())

        An, Bn = self._compute_coefficients(f_expr, g_expr, n, L, x, alpha, beta, c)
        steps += self._steps_apply_ics(f_latex, g_latex, An, Bn)

        solution_expr = self._build_solution(
            An, Bn, n, x, t, L, alpha, beta, c
        )
        steps.append(self._step_final(solution_expr))
        steps += self._steps_verification(solution_expr, alpha, beta, c, x, t)
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # -----------------------------------------------------------------------

    def _step_statement(self, f_latex: str, g_latex: str) -> Step:
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (ecuación del telégrafo)",
            md=T.T_statement_telegraph(),
            latex=equation_chain(
                [
                    r"&u_{tt} + 2\alpha u_t + \beta u = c^2 u_{xx},\quad 0 < x < L,\ t > 0,",
                    r"&u(0, t) = u(L, t) = 0,",
                    rf"&u(x, 0) = {f_latex},\quad u_t(x, 0) = {g_latex}.",
                ]
            ),
            level="basic",
            observations=[obs.get("wave_needs_two_ics")],
        )

    def _step_classification(self) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Clasificación",
            md=(
                "El término de mayor orden es $u_{tt} - c^2 u_{xx}$, "
                "idéntico al de la ecuación de onda. La parte de orden "
                "inferior ($2\\alpha u_t + \\beta u$) **no cambia** el "
                "carácter PDE: sigue siendo **hiperbólica**. Lo que sí "
                "cambia es la dinámica: ahora hay disipación y una "
                "fuerza restauradora extra."
            ),
            level="basic",
        )

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método: separación de variables",
            md=(
                "Mismas tres condiciones que en heat/wave: lineal, "
                "intervalo finito, BCs homogéneas. La separación produce "
                "el problema espacial estándar; la novedad está en la "
                "**EDO temporal** que ahora tiene un coeficiente de "
                "fricción y una masa efectiva."
            ),
            level="basic",
        )

    def _steps_separation(
        self, alpha: sp.Symbol, beta: sp.Symbol, c: sp.Symbol
    ) -> list[Step]:
        s_ansatz = step(
            kind="development",
            title="Paso 3.1 — Ansatz $u = X(x) T(t)$",
            md=T.T_sov_ansatz(),
            latex=r"u(x, t) = X(x)\, T(t).",
            level="basic",
            observations=[obs.get("sov_why_separable")],
        )
        s_substitute = step(
            kind="development",
            title="Paso 3.2 — Sustituimos y separamos",
            md=(
                "Dividiendo por $c^2 X T$, todos los términos en $t$ "
                "quedan a un lado y todos los términos en $x$ al otro:"
            ),
            latex=equation_chain(
                [
                    r"X T'' + 2\alpha X T' + \beta X T &= c^2 X'' T,",
                    r"\frac{T'' + 2\alpha T' + \beta T}{c^2 T} &= \frac{X''}{X} = -\lambda,",
                    r"\Rightarrow X'' + \lambda X &= 0,",
                    r"\Rightarrow T'' + 2\alpha T' + (\beta + c^2 \lambda) T &= 0.",
                ]
            ),
            level="basic",
        )
        return [s_ansatz, s_substitute]

    def _step_spatial(self) -> Step:
        return step(
            kind="boundary",
            title="Paso 4 — Problema espacial (idéntico al del calor)",
            md=(
                "El problema de Sturm-Liouville en $X$ es el mismo de "
                "siempre. Tres casos en $\\lambda$, sólo el positivo "
                "sobrevive, y obtenemos $\\lambda_n = (n\\pi/L)^2$, "
                "$X_n(x) = \\sin(n\\pi x/L)$."
            ),
            observations=[obs.get("sturm_liouville_theorem")],
            level="basic",
        )

    def _step_temporal_ode(
        self, alpha: sp.Symbol, beta: sp.Symbol, c: sp.Symbol
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3.6 — EDO temporal: oscilador amortiguado",
            md=T.T_telegraph_temporal_ode(),
            level="basic",
        )

    def _step_three_regimes(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.7 — Los tres regímenes (sobre/crítico/subamortiguado)",
            md=T.T_telegraph_three_regimes(),
            level="basic",
            observations=[obs.get("telegraph_three_regimes"), obs.get("telegraph_heaviside")],
        )

    def _step_superposition_formal(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.8 — Superposición (forma general)",
            md=(
                "Independientemente del régimen, escribimos la solución "
                "como combinación lineal de las dos soluciones "
                "independientes de la EDO temporal, multiplicadas por "
                "la autofunción espacial:"
            ),
            latex=(
                r"u(x, t) = \sum_{n=1}^{\infty} "
                r"e^{-\alpha t}\bigl[A_n \psi_n^{(1)}(t) + B_n \psi_n^{(2)}(t)\bigr]\, "
                r"\sin\!\bigl(\tfrac{n\pi x}{L}\bigr),"
            ),
            level="intermediate",
        )

    def _compute_coefficients(
        self,
        f_expr: sp.Basic,
        g_expr: sp.Basic,
        n: sp.Symbol,
        L: sp.Symbol,
        x: sp.Symbol,
        alpha: sp.Symbol,
        beta: sp.Symbol,
        c: sp.Symbol,
    ) -> tuple[sp.Basic, sp.Basic]:
        # We use the unified subdamped representation
        # T_n(t) = e^{-α t} [A_n cos(ω_n t) + B_n sin(ω_n t)] where
        # ω_n² = β + c²(nπ/L)² − α². This expression is valid as the
        # principal SymPy branch; for the overdamped case ω_n becomes
        # imaginary and the cos/sin turn into cosh/sinh.
        omega_n_sq = beta + c**2 * (n * sp.pi / L) ** 2 - alpha**2
        omega_n = sp.sqrt(omega_n_sq)

        # At t = 0: u = A_n sin(nπx/L) → A_n is the Fourier-sine coef of f.
        An = sp.simplify(
            sp.Rational(2) / L * sp.integrate(f_expr * sp.sin(n * sp.pi * x / L), (x, 0, L))
        )
        An = sp.simplify(An.subs(sp.cos(sp.pi * n), (-1) ** n))

        # u_t(x, 0) = Σ (-α A_n + ω_n B_n) sin(...) = g(x).
        # → -α A_n + ω_n B_n = (2/L) ∫g sin(...) dx = call it ĝ_n.
        # → B_n = (ĝ_n + α A_n) / ω_n.
        g_n = sp.simplify(
            sp.Rational(2) / L * sp.integrate(g_expr * sp.sin(n * sp.pi * x / L), (x, 0, L))
        )
        g_n = sp.simplify(g_n.subs(sp.cos(sp.pi * n), (-1) ** n))
        Bn = sp.simplify((g_n + alpha * An) / omega_n)
        return An, Bn

    def _steps_apply_ics(
        self,
        f_latex: str,
        g_latex: str,
        An: sp.Basic,
        Bn: sp.Basic,
    ) -> list[Step]:
        s_setup = step(
            kind="initial",
            title="Paso 5 — Aplicación de las dos condiciones iniciales",
            md=(
                "Usaremos la representación unificada "
                "$T_n(t) = e^{-\\alpha t}[A_n \\cos(\\omega_n t) + "
                "B_n \\sin(\\omega_n t)]$ con "
                "$\\omega_n^2 = \\beta + c^2(n\\pi/L)^2 - \\alpha^2$. "
                "Cuando $\\omega_n^2 < 0$ (régimen sobreamortiguado), "
                "$\\omega_n$ es imaginario y las funciones trigonométricas "
                "se convierten formalmente en hiperbólicas — el álgebra "
                "es la misma."
            ),
            latex=equation_chain(
                [
                    r"u(x, 0) &= \sum A_n \sin(n\pi x/L) = f(x),",
                    r"u_t(x, 0) &= \sum (-\alpha A_n + \omega_n B_n) \sin(n\pi x/L) = g(x).",
                ]
            ),
            level="basic",
        )
        s_An = step(
            kind="initial",
            title=f"Paso 5.1 — Coeficientes $A_n$ a partir de $f(x) = {f_latex}$",
            md="Es la serie de Fourier en senos de $f$:",
            latex=rf"A_n = {sp.latex(An)}.",
            sympy_expr=An,
            level="basic",
        )
        s_Bn = step(
            kind="initial",
            title=f"Paso 5.2 — Coeficientes $B_n$ a partir de $g(x) = {g_latex}$",
            md=(
                "Despejamos $B_n$ del coeficiente de Fourier de $g$, "
                "compensando por el factor $-\\alpha$ que arrastra el "
                "$e^{-\\alpha t}$ al derivar:"
            ),
            latex=rf"B_n = {sp.latex(Bn)}.",
            sympy_expr=Bn,
            level="basic",
        )
        return [s_setup, s_An, s_Bn]

    def _build_solution(
        self,
        An: sp.Basic,
        Bn: sp.Basic,
        n: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
        L: sp.Symbol,
        alpha: sp.Symbol,
        beta: sp.Symbol,
        c: sp.Symbol,
    ) -> sp.Basic:
        omega_n = sp.sqrt(beta + c**2 * (n * sp.pi / L) ** 2 - alpha**2)
        temporal = sp.exp(-alpha * t) * (
            An * sp.cos(omega_n * t) + Bn * sp.sin(omega_n * t)
        )
        spatial = sp.sin(n * sp.pi * x / L)
        return sp.Sum(temporal * spatial, (n, 1, sp.oo))

    def _step_final(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Solución",
            md="Sustituyendo en la superposición, la solución es:",
            latex=rf"\boxed{{\; u(x, t) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        alpha: sp.Symbol,
        beta: sp.Symbol,
        c: sp.Symbol,
        x: sp.Symbol,
        t: sp.Symbol,
    ) -> list[Step]:
        term = solution_expr.function if isinstance(solution_expr, sp.Sum) else solution_expr
        u_t = sp.diff(term, t)
        u_tt = sp.diff(term, t, 2)
        u_xx = sp.diff(term, x, 2)
        residual = sp.simplify(u_tt + 2 * alpha * u_t + beta * term - c**2 * u_xx)
        pde_ok = bool(residual == 0)

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "Sustituimos el término genérico en la EDP completa "
                "$u_{tt} + 2\\alpha u_t + \\beta u - c^2 u_{xx}$. Cada "
                "pieza debe contribuir con su parte correspondiente para "
                "cancelarse."
            ),
            level="basic",
        )
        s_pde = step(
            kind="verification",
            title="Residuo de la EDP",
            md=(
                "El cálculo es algebraicamente largo pero mecánico. "
                "SymPy simplifica todos los términos y verifica:"
                if pde_ok
                else "**Atención:** residuo no nulo, revisar."
            ),
            latex=rf"u_{{tt}} + 2\alpha u_t + \beta u - c^2 u_{{xx}} = {sp.latex(residual)}.",
            level="intermediate",
        )
        return [s_intro, s_pde]

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_telegraph_physical_interpretation(),
            level="basic",
            observations=[obs.get("telegraph_heaviside")],
        )
