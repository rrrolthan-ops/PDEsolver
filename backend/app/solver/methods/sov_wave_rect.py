"""Wave equation on a rectangle — separation of variables.

Problem covered
---------------
    u_tt = c² (u_xx + u_yy)   on [0, a] × [0, b], t > 0
    u = 0  on the four sides
    u(x, y, 0)   = f(x, y)
    u_t(x, y, 0) = g(x, y)

Solution
--------
Modal expansion:

    u(x, y, t) = Σ_{m,n ≥ 1} (A_{mn} cos(ω_{mn} t) + B_{mn} sin(ω_{mn} t))
                              · sin(mπx/a) sin(nπy/b)

with ω_{mn} = c π √(m²/a² + n²/b²) and double-Fourier coefficients

    A_{mn} = (4/(ab)) ∫∫ f · sin · sin dx dy
    B_{mn} = (4/(ab ω_{mn})) ∫∫ g · sin · sin dx dy.

Pedagogical contrast
--------------------
- 1D string (sov_wave_1d): harmonic spectrum ω_n = c n π/L.
- 2D rectangular drum (this method): non-harmonic in general,
  *degenerate* in the square case (m ↔ n swap gives same ω).
- 2D circular drum (sov_wave_disk): non-harmonic spectrum tied to
  zeros of J_0.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class WaveRect2D(Method):
    """Rectangular drum via 2D separation of variables."""

    slug = "sov_wave_rect"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        y = sp.Symbol("y", real=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        m = sp.Symbol("m", integer=True, positive=True)
        n = sp.Symbol("n", integer=True, positive=True)
        a = sp.Symbol("a", positive=True)
        b = sp.Symbol("b", positive=True)
        c = sp.Symbol("c", positive=True)
        xi = sp.Symbol("xi", real=True)
        eta = sp.Symbol("eta", real=True)

        # ---------- Parse f(x, y) and g(x, y) -------------------------------
        f_latex = "0"
        g_latex = "0"
        for ic in problem.initial_conditions:
            if ic.order == 0:
                f_latex = ic.value
            elif ic.order == 1:
                g_latex = ic.value
        f_expr = self._parse_2d(f_latex, problem.parameters, x, y)
        g_expr = self._parse_2d(g_latex, problem.parameters, x, y)

        steps: list[Step] = []

        # ===== PASO 0 — Statement =============================================
        steps.append(self._step_statement(f_latex, g_latex))

        # ===== PASO 1 — Classification ========================================
        steps.append(self._step_classification(c))

        # ===== PASO 2 — Method choice =========================================
        steps.append(self._step_method_choice())

        # ===== PASO 3 — Separation =============================================
        steps.append(self._step_separation(c))

        # ===== PASO 4 — Eigenmodes and frequencies ===========================
        steps.append(self._step_eigenmodes(m, n, a, b, c))

        # ===== PASO 5 — Apply initial conditions =============================
        steps.append(self._step_apply_initial(m, n, a, b, c, xi, eta))

        # ===== PASO 6 — Final formula =========================================
        solution_expr = self._build_solution_expression(
            f_expr, g_expr, m, n, a, b, c, x, y, t, xi, eta
        )
        steps.append(self._step_final_formula(solution_expr))

        # ===== PASO 7 — Verification ==========================================
        steps += self._steps_verification(
            solution_expr, m, n, a, b, c, x, y, t
        )

        # ===== PASO 8 — Visualization =========================================
        steps.append(self._step_visualization())

        # ===== PASO 9 — Physical interpretation ==============================
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # ===========================================================================
    # Helpers
    # ===========================================================================

    @staticmethod
    def _parse_2d(
        latex: str,
        parameters: dict[str, str],
        x: sp.Symbol,
        y: sp.Symbol,
    ) -> sp.Basic:
        expr = parse_scalar_latex(latex, parameters)
        return expr.subs(sp.Symbol("x"), x).subs(sp.Symbol("y"), y)

    # ===========================================================================
    # Steps
    # ===========================================================================

    def _step_statement(self, f_latex: str, g_latex: str) -> Step:
        latex = equation_chain(
            [
                r"&\text{EDP:} \quad u_{tt} = c^2\, (u_{xx} + u_{yy}), "
                r"\quad (x, y) \in [0, a] \times [0, b],\ t > 0,",
                r"&\text{BCs (cuatro lados):}\quad "
                r"u(0, y, t) = u(a, y, t) = u(x, 0, t) = u(x, b, t) = 0,",
                rf"&\text{{posición inicial:}}\quad u(x, y, 0) = {f_latex},",
                rf"&\text{{velocidad inicial:}}\quad u_t(x, y, 0) = {g_latex}.",
            ]
        )
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (tambor rectangular)",
            md=T.T_statement_wave_rect_2d(),
            latex=latex,
            level="basic",
        )

    def _step_classification(self, c: sp.Symbol) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Clasificación (hiperbólica 2D)",
            md=(
                "EDP de segundo orden en tres variables $(x, y, t)$, "
                "hiperbólica respecto al tiempo: el coeficiente de "
                "$u_{tt}$ tiene signo opuesto a los del Laplaciano "
                "espacial. Misma naturaleza que la cuerda 1D y el "
                "tambor circular — sólo cambia la geometría."
            ),
            latex=(
                r"u_{tt} - c^2 (u_{xx} + u_{yy}) = 0 "
                r"\quad \Rightarrow \quad \text{hiperbólica 2+1.}"
            ),
            level="basic",
        )

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método: separación de variables triple",
            md=T.T_wave_rect_method_choice(),
            latex=(
                r"u(x, y, t) = X(x)\, Y(y)\, T(t) "
                r"\Rightarrow \frac{T''}{c^2 T} "
                r"= \frac{X''}{X} + \frac{Y''}{Y} = -\mu."
            ),
            level="basic",
        )

    def _step_separation(self, c: sp.Symbol) -> Step:
        return step(
            kind="development",
            title="Paso 3 — Separación + tres EDOs",
            md=(
                "Las tres EDOs resultantes (con $\\mu = \\lambda + \\nu$):"
            ),
            latex=equation_chain(
                [
                    r"X'' + \lambda X = 0,&\quad X(0) = X(a) = 0,",
                    r"Y'' + \nu Y = 0,&\quad Y(0) = Y(b) = 0,",
                    r"T'' + c^2 \mu\, T = 0,&\quad \mu = \lambda + \nu.",
                ]
            ),
            level="intermediate",
        )

    def _step_eigenmodes(
        self,
        m: sp.Symbol,
        n: sp.Symbol,
        a: sp.Symbol,
        b: sp.Symbol,
        c: sp.Symbol,
    ) -> Step:
        return step(
            kind="boundary",
            title="Paso 4 — Autovalores y autofunciones",
            md=T.T_wave_rect_eigenmodes(),
            latex=equation_chain(
                [
                    rf"\lambda_m &= ({sp.latex(m * sp.pi / a)})^2,\quad "
                    rf"X_m(x) = \sin\!\left(\frac{{m\pi x}}{{a}}\right),",
                    rf"\nu_n &= ({sp.latex(n * sp.pi / b)})^2,\quad "
                    rf"Y_n(y) = \sin\!\left(\frac{{n\pi y}}{{b}}\right),",
                    r"\omega_{mn} &= c\sqrt{\lambda_m + \nu_n} "
                    r"= c\pi\sqrt{\frac{m^2}{a^2} + \frac{n^2}{b^2}}.",
                ]
            ),
            level="intermediate",
            observations=[obs.get("rectangular_drum_degeneracy")],
        )

    def _step_apply_initial(
        self,
        m: sp.Symbol,
        n: sp.Symbol,
        a: sp.Symbol,
        b: sp.Symbol,
        c: sp.Symbol,
        xi: sp.Symbol,
        eta: sp.Symbol,
    ) -> Step:
        omega_mn = c * sp.sqrt((m * sp.pi / a) ** 2 + (n * sp.pi / b) ** 2)
        return step(
            kind="initial",
            title="Paso 5 — Coeficientes de la doble serie de Fourier",
            md=(
                "Posición inicial $u(\\cdot, \\cdot, 0) = f$ fija "
                "$A_{mn}$; velocidad inicial $u_t(\\cdot, \\cdot, 0) = g$ "
                "fija $B_{mn}$. La **ortogonalidad doble** "
                "$\\int_0^a \\sin\\sin = (a/2)\\delta_{mm'}$ por Fubini "
                "extrae cada coeficiente por integración término-a-término."
            ),
            latex=equation_chain(
                [
                    r"A_{mn} &= \frac{4}{ab} "
                    r"\int_0^a\!\!\int_0^b f(\xi, \eta)\, "
                    r"\sin\!\left(\frac{m\pi\xi}{a}\right) "
                    r"\sin\!\left(\frac{n\pi\eta}{b}\right)\, d\xi\, d\eta,",
                    r"B_{mn} &= \frac{4}{ab\, \omega_{mn}} "
                    r"\int_0^a\!\!\int_0^b g(\xi, \eta)\, "
                    r"\sin\!\left(\frac{m\pi\xi}{a}\right) "
                    r"\sin\!\left(\frac{n\pi\eta}{b}\right)\, d\xi\, d\eta,",
                    rf"\omega_{{mn}} &= {sp.latex(omega_mn)}.",
                ]
            ),
            level="intermediate",
        )

    def _build_solution_expression(
        self,
        f_expr: sp.Basic,
        g_expr: sp.Basic,
        m: sp.Symbol,
        n: sp.Symbol,
        a: sp.Symbol,
        b: sp.Symbol,
        c: sp.Symbol,
        x: sp.Symbol,
        y: sp.Symbol,
        t: sp.Symbol,
        xi: sp.Symbol,
        eta: sp.Symbol,
    ) -> sp.Basic:
        omega_mn = c * sp.sqrt((m * sp.pi / a) ** 2 + (n * sp.pi / b) ** 2)
        sin_x = sp.sin(m * sp.pi * x / a)
        sin_y = sp.sin(n * sp.pi * y / b)
        sin_xi = sp.sin(m * sp.pi * xi / a)
        sin_eta = sp.sin(n * sp.pi * eta / b)

        # A_{mn}: try to evaluate the double integral; fall back to unevaluated.
        f_at_xy = f_expr.subs({x: xi, y: eta})
        g_at_xy = g_expr.subs({x: xi, y: eta})

        A_integral = sp.Integral(
            f_at_xy * sin_xi * sin_eta, (xi, 0, a), (eta, 0, b)
        )
        B_integral = sp.Integral(
            g_at_xy * sin_xi * sin_eta, (xi, 0, a), (eta, 0, b)
        )

        A_mn = sp.Rational(4, 1) / (a * b) * A_integral
        B_mn = sp.Rational(4, 1) / (a * b * omega_mn) * B_integral

        # Attempt symbolic evaluation when f or g is a single product mode.
        try:
            A_val = sp.simplify(A_integral.doit())
            if not A_val.has(sp.Integral) and not A_val.has(sp.Piecewise):
                A_mn = sp.Rational(4, 1) / (a * b) * A_val
        except Exception:
            pass
        try:
            B_val = sp.simplify(B_integral.doit())
            if not B_val.has(sp.Integral) and not B_val.has(sp.Piecewise):
                B_mn = sp.Rational(4, 1) / (a * b * omega_mn) * B_val
        except Exception:
            pass

        term = (
            A_mn * sp.cos(omega_mn * t) + B_mn * sp.sin(omega_mn * t)
        ) * sin_x * sin_y

        return sp.Sum(sp.Sum(term, (n, 1, sp.oo)), (m, 1, sp.oo))

    def _step_final_formula(self, expr: sp.Basic) -> Step:
        return step(
            kind="final",
            title="Paso 6 — Solución general (serie doble de modos normales)",
            md=T.T_wave_rect_solution(),
            latex=rf"\boxed{{\; u(x, y, t) = {sp.latex(expr)} \;}}",
            sympy_expr=expr,
            level="basic",
        )

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        m: sp.Symbol,
        n: sp.Symbol,
        a: sp.Symbol,
        b: sp.Symbol,
        c: sp.Symbol,
        x: sp.Symbol,
        y: sp.Symbol,
        t: sp.Symbol,
    ) -> list[Step]:
        # Inspect the *generic term* inside the double Sum.
        outer = (
            solution_expr.function if isinstance(solution_expr, sp.Sum) else solution_expr
        )
        inner = outer.function if isinstance(outer, sp.Sum) else outer
        u_tt = sp.diff(inner, t, 2)
        lap = sp.diff(inner, x, 2) + sp.diff(inner, y, 2)
        residual = sp.simplify(u_tt - c**2 * lap)
        pde_ok = bool(residual == 0)

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "Verificamos en el **término genérico** del doble Sum. "
                "Cada modo es un producto $\\phi_{mn}(x, y) T_{mn}(t)$ "
                "con $\\phi_{mn} = \\sin(m\\pi x/a)\\sin(n\\pi y/b)$ "
                "una autofunción del Laplaciano "
                "($-\\Delta \\phi_{mn} = \\mu_{mn} \\phi_{mn}$), y "
                "$T_{mn}$ una combinación de $\\cos(\\omega_{mn} t)$ y "
                "$\\sin(\\omega_{mn} t)$ con frecuencia $\\omega_{mn} = "
                "c\\sqrt{\\mu_{mn}}$. La EDP se satisface término a "
                "término:"
            ),
            level="basic",
        )
        s_pde = step(
            kind="verification",
            title=r"Verificación de la EDP: u_{tt} = c^2 \Delta u",
            md=(
                "Diferenciando el término genérico:"
                if pde_ok
                else "**Atención:** el residuo no se simplificó a cero."
            ),
            latex=equation_chain(
                [
                    rf"u_{{tt}} &= {sp.latex(sp.simplify(u_tt))},",
                    rf"c^2 (u_{{xx}} + u_{{yy}}) &= {sp.latex(sp.simplify(c**2 * lap))},",
                    rf"u_{{tt}} - c^2 \Delta u &= {sp.latex(residual)}.",
                ]
            ),
            level="intermediate",
        )
        s_bcs = step(
            kind="verification",
            title="Verificación de las BCs",
            md=(
                "Las cuatro condiciones $u = 0$ en los lados se "
                "cumplen automáticamente porque "
                "$\\sin(m\\pi \\cdot 0/a) = \\sin(m\\pi \\cdot a/a) = 0$ "
                "(análogamente en $y$). La base sin-sin **está "
                "construida para anular en los cuatro lados**."
            ),
            latex=(
                r"\sin(m\pi \cdot 0 / a) = \sin(m\pi) = 0,\quad "
                r"\sin(n\pi \cdot 0 / b) = \sin(n\pi) = 0."
            ),
            level="intermediate",
        )
        return [s_intro, s_pde, s_bcs]

    def _step_visualization(self) -> Step:
        return step(
            kind="visualization",
            title="Paso 8 — Visualización (instantánea $t = 0$)",
            md=(
                "El gráfico muestra el perfil inicial $u(x, y, 0) = "
                "f(x, y)$ sobre el rectángulo. Cada modo $(m, n)$ "
                "vibra independientemente con su frecuencia $\\omega_{mn}$. "
                "Para visualizar la **dinámica**, prueba a sustituir "
                "$t$ por valores entre $0$ y $2\\pi/\\omega_{11}$ (un "
                "período del modo fundamental): la superficie oscila "
                "verticalmente con patrones nodales fijos."
            ),
            level="basic",
        )

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física (espectros de tambores)",
            md=T.T_wave_rect_physical_interpretation(),
            level="basic",
            observations=[
                obs.get("rectangular_drum_degeneracy"),
                obs.get("kac_hear_shape_of_drum"),
            ],
        )
