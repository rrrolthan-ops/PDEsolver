"""Inviscid Burgers' equation u_t + u u_x = 0 by characteristics.

Problem covered
---------------
    u_t + u u_x = 0       x ∈ ℝ,   t > 0
    u(x, 0) = u_0(x)

Approach
--------
Characteristics: along the curve x(t) = x_0 + u_0(x_0) t, u stays
constant equal to u_0(x_0). The solution is implicit:

    u(x, t) = u_0(x_0)  with  x = x_0 + u_0(x_0) t.

Breaking time
-------------
The Jacobian ∂x/∂x_0 = 1 + u_0'(x_0) t vanishes first at
    t_b = -1 / min(u_0'(x_0)).
For non-decreasing data, t_b = ∞ (smooth forever). Otherwise t_b is
finite and a shock forms.

Why this method belongs in the curriculum
-----------------------------------------
Burgers is the canonical "first non-linear PDE": it teaches that
smooth initial data can spontaneously develop discontinuities (shocks),
that classical solutions fail, and that weak solutions + selection
principles (Rankine-Hugoniot, vanishing viscosity, entropy) are
necessary. It's the gateway from linear theory to non-linear hyperbolic
analysis.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class BurgersInviscid(Method):
    """Method of characteristics for inviscid Burgers' equation."""

    slug = "burgers_inviscid"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        t = sp.Symbol("t", real=True, nonnegative=True)
        x0 = sp.Symbol("x_0", real=True)

        # ---------- Parse u_0(x) ---------------------------------------------
        u0_latex = "0"
        for ic in problem.initial_conditions:
            if ic.order == 0:
                u0_latex = ic.value
                break
        u0_expr_x = parse_scalar_latex(u0_latex, problem.parameters).subs(
            sp.Symbol("x"), x
        )
        u0_of_x0 = u0_expr_x.subs(x, x0)

        steps: list[Step] = []

        # ===== PASO 0 — Statement =============================================
        steps.append(self._step_statement(u0_latex))

        # ===== PASO 1 — Classification ========================================
        steps.append(self._step_classification())

        # ===== PASO 2 — Method choice =========================================
        steps.append(self._step_method_choice())

        # ===== PASO 3 — Characteristics ======================================
        steps.append(self._step_characteristics(u0_of_x0, x0, t))

        # ===== PASO 5 — Apply initial condition (built-in via x_0 ↔ u_0(x_0)).
        steps.append(self._step_apply_initial(u0_latex))

        # ===== PASO 6 — Final implicit formula ===============================
        steps.append(self._step_implicit_formula(u0_of_x0, x, x0, t))

        # ===== PASO 6.5 — Breaking time + shock analysis =====================
        breaking_time, breaking_x0, monotonicity = self._compute_breaking(
            u0_expr_x, x
        )
        steps.append(
            self._step_breaking_time(
                u0_expr_x, x, breaking_time, breaking_x0, monotonicity
            )
        )

        # ===== PASO 6.75 — Rankine-Hugoniot (when shock occurs) ==============
        if monotonicity == "decreasing_somewhere":
            steps.append(self._step_rankine_hugoniot())

        # ===== PASO 7 — Verification =========================================
        steps.append(self._step_verification(u0_of_x0, x0, t))

        # ===== PASO 8 — Visualization =========================================
        steps.append(self._step_visualization(monotonicity, breaking_time))

        # ===== PASO 9 — Physical interpretation ==============================
        steps.append(self._step_physical())

        # Artifact: the implicit relation u_0(x_0) with the
        # characteristic-coordinate relation. We pack it as a sympy
        # equation u - u_0(x - u·t) = 0 (the "fix-point" form).
        try:
            implicit = u0_expr_x.subs(x, x - sp.Symbol("u") * t)
            artifact = sp.Symbol("u") - implicit
        except Exception:
            artifact = u0_of_x0

        return steps, SolutionArtifacts(
            solution_expr=artifact,
            solution_latex=sp.latex(artifact),
        )

    # ===========================================================================
    # PASO 0
    # ===========================================================================

    def _step_statement(self, u0_latex: str) -> Step:
        latex = equation_chain(
            [
                r"&\text{EDP:} \quad u_t + u\, u_x = 0, "
                r"\quad x \in \mathbb{R},\quad t > 0,",
                rf"&\text{{condición inicial:}} \quad u(x, 0) = {u0_latex}.",
            ]
        )
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (Burgers no viscosa)",
            md=T.T_statement_burgers(),
            latex=latex,
            level="basic",
        )

    # ===========================================================================
    # PASO 1
    # ===========================================================================

    def _step_classification(self) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Clasificación (cuasi-lineal hiperbólica)",
            md=(
                "Es una EDP de **primer orden** (sólo $u_t$ y $u_x$), "
                "y **cuasi-lineal**: los coeficientes dependen de $u$ "
                "pero no de $u_x$. Estas EDPs son **hiperbólicas** "
                "(propagación a lo largo de características) pero, a "
                "diferencia de las lineales, las características no "
                "son rectas paralelas — la pendiente depende de la "
                "solución misma."
            ),
            latex=(
                r"u_t + a(u)\, u_x = 0,\quad a(u) = u "
                r"\quad \Rightarrow \quad "
                r"\text{cuasi-lineal hiperbólica.}"
            ),
            level="basic",
        )

    # ===========================================================================
    # PASO 2
    # ===========================================================================

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método: características generalizadas",
            md=T.T_burgers_method_choice(),
            latex=(
                r"\frac{dx}{dt} = u(x, t),\quad "
                r"\frac{du}{dt} = 0 \text{ a lo largo de la característica.}"
            ),
            level="basic",
            observations=[obs.get("burgers_self_steepening")],
        )

    # ===========================================================================
    # PASO 3
    # ===========================================================================

    def _step_characteristics(
        self, u0_of_x0: sp.Basic, x0: sp.Symbol, t: sp.Symbol
    ) -> Step:
        return step(
            kind="development",
            title="Paso 3 — Ecuaciones de las características",
            md=T.T_burgers_characteristics(),
            latex=equation_chain(
                [
                    r"\text{característica que parte de } x_0:",
                    rf"x(t; x_0) &= x_0 + u_0(x_0)\, t = x_0 + ({sp.latex(u0_of_x0)})\, t,",
                    rf"u\bigl(x(t; x_0), t\bigr) &= u_0(x_0) = {sp.latex(u0_of_x0)}.",
                ]
            ),
            level="intermediate",
        )

    # ===========================================================================
    # PASO 5
    # ===========================================================================

    def _step_apply_initial(self, u0_latex: str) -> Step:
        return step(
            kind="initial",
            title="Paso 5 — La condición inicial entra como datos sobre el eje $t = 0$",
            md=(
                "Cada característica está **etiquetada por su punto de "
                "partida** $x_0$ en el eje $t = 0$, y porta consigo el "
                "valor $u_0(x_0)$. No hay coeficientes adicionales que "
                "ajustar: la condición inicial **es** la parametrización."
            ),
            latex=rf"u_0(x) = {u0_latex}, \quad u(x_0, 0) = u_0(x_0).",
            level="basic",
        )

    # ===========================================================================
    # PASO 6 — Implicit formula
    # ===========================================================================

    def _step_implicit_formula(
        self,
        u0_of_x0: sp.Basic,
        x: sp.Symbol,
        x0: sp.Symbol,
        t: sp.Symbol,
    ) -> Step:
        # Display the implicit fix-point equation u = u_0(x - u t).
        u_sym = sp.Symbol("u")
        implicit_box = sp.Eq(
            u_sym,
            u0_of_x0.subs(x0, x - u_sym * t),
        )
        return step(
            kind="final",
            title="Paso 6 — Solución implícita",
            md=(
                "Despejando $x_0$ de $x = x_0 + u_0(x_0) t$ y "
                "reemplazándolo en $u = u_0(x_0)$, obtenemos la "
                "**ecuación de punto fijo**:"
            ),
            latex=rf"\boxed{{\; {sp.latex(implicit_box)} \;}}",
            sympy_expr=implicit_box.lhs - implicit_box.rhs,
            level="intermediate",
        )

    # ===========================================================================
    # Breaking time analysis
    # ===========================================================================

    def _compute_breaking(
        self, u0_expr: sp.Basic, x: sp.Symbol
    ) -> tuple[sp.Basic | None, sp.Basic | None, str]:
        """Find t_b = -1/min(u_0'(x)).

        Returns (t_b, x_at_min, monotonicity_label) where the label is one
        of "non_decreasing", "decreasing_somewhere", or "undetermined".
        """
        u0_prime = sp.diff(u0_expr, x)
        try:
            # Try to find global min via critical points.
            critical = sp.solve(sp.diff(u0_prime, x), x)
            candidates = list(critical) + []
            values = []
            for c in candidates:
                try:
                    v = sp.simplify(u0_prime.subs(x, c))
                    if v.is_real is not False:
                        values.append((v, c))
                except Exception:
                    continue
            if not values:
                # Try a few sample points: limits and 0.
                for c in (sp.Integer(0), sp.oo, -sp.oo):
                    try:
                        v = sp.limit(u0_prime, x, c)
                        if v.is_real is not False and v.is_finite:
                            values.append((v, c))
                    except Exception:
                        continue
            if not values:
                return None, None, "undetermined"
            v_min, x_at_min = min(values, key=lambda p: float(p[0]))
            if v_min >= 0:
                return sp.oo, x_at_min, "non_decreasing"
            t_b = sp.simplify(-1 / v_min)
            return t_b, x_at_min, "decreasing_somewhere"
        except Exception:
            return None, None, "undetermined"

    def _step_breaking_time(
        self,
        u0_expr: sp.Basic,
        x: sp.Symbol,
        breaking_time: sp.Basic | None,
        breaking_x0: sp.Basic | None,
        monotonicity: str,
    ) -> Step:
        u0_prime = sp.diff(u0_expr, x)
        if monotonicity == "non_decreasing":
            md = (
                "El dato inicial es **no decreciente** "
                "($u_0'(x) \\ge 0$ en todas partes), así que las "
                "características divergen y no se cruzan nunca. La "
                "solución clásica existe para **todo** $t > 0$ — no "
                "hay choque."
            )
            latex_body = [
                rf"u_0'(x) &= {sp.latex(u0_prime)} \ge 0,",
                r"\Rightarrow\ t_b = +\infty.",
            ]
        elif monotonicity == "decreasing_somewhere":
            md = (
                "El dato inicial **decrece** en algún punto. La "
                "característica con $u_0'$ más negativa es la primera "
                "en alcanzar a su vecina por delante: ahí se forma el "
                "primer choque, en tiempo $t = t_b$."
            )
            latex_body = [
                rf"u_0'(x) &= {sp.latex(u0_prime)},",
                rf"\min_x u_0'(x) &= {sp.latex(sp.simplify(u0_prime.subs(x, breaking_x0)))} "
                rf"\text{{ en }} x = {sp.latex(breaking_x0)},",
                rf"\boxed{{\; t_b = -\dfrac{{1}}{{\min u_0'}} "
                rf"= {sp.latex(breaking_time)}. \;}}",
            ]
        else:
            md = (
                "Para este dato inicial, el análisis simbólico del "
                "mínimo de $u_0'$ no es concluyente; el tiempo de "
                "ruptura debe estudiarse caso por caso."
            )
            latex_body = [
                rf"u_0'(x) &= {sp.latex(u0_prime)},",
                r"\text{análisis caso por caso.}",
            ]
        return step(
            kind="development",
            title="Paso 6.5 — Tiempo de ruptura $t_b$",
            md=T.T_burgers_breaking_time() + "\n\n" + md,
            latex=equation_chain(latex_body),
            level="intermediate",
        )

    # ===========================================================================
    # Rankine-Hugoniot
    # ===========================================================================

    def _step_rankine_hugoniot(self) -> Step:
        return step(
            kind="development",
            title="Paso 6.75 — Condición de Rankine-Hugoniot",
            md=T.T_burgers_shock_rankine_hugoniot(),
            latex=(
                r"\frac{ds}{dt} = \frac{u_L + u_R}{2}"
                r"\quad (\text{velocidad del choque}); \qquad "
                r"\text{en general:}\ "
                r"\frac{ds}{dt} = \frac{f(u_L) - f(u_R)}{u_L - u_R}, "
                r"\ f(u) = \tfrac{1}{2}u^2."
            ),
            level="intermediate",
            observations=[
                obs.get("rankine_hugoniot_geometric"),
                obs.get("burgers_vanishing_viscosity"),
            ],
        )

    # ===========================================================================
    # Verification
    # ===========================================================================

    def _step_verification(
        self, u0_of_x0: sp.Basic, x0: sp.Symbol, t: sp.Symbol
    ) -> Step:
        # Verify: along x(t;x_0) = x_0 + u_0(x_0) t, du/dt = u_t + u u_x = 0.
        # Since u(x(t;x_0), t) = u_0(x_0) is constant in t along the
        # characteristic, the total derivative vanishes — this IS the
        # original PDE (chain rule):
        #   du/dt = u_t + (dx/dt) u_x = u_t + u(x,t) u_x = 0.
        # So the implicit solution satisfies Burgers identically.
        return step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "**Estructura del argumento.** Por construcción, $u$ "
                "es **constante** a lo largo de cada característica: "
                "$u(x(t; x_0), t) = u_0(x_0)$ no depende de $t$. "
                "Derivando esta identidad con la regla de la cadena, "
                "**recuperamos exactamente la EDP**:"
            ),
            latex=equation_chain(
                [
                    r"\frac{d}{dt}\bigl[ u(x(t; x_0), t) \bigr] &= 0 "
                    r"\quad (\text{constante por construcción}),",
                    r"\frac{d}{dt}\bigl[ u(x(t; x_0), t) \bigr] "
                    r"&= u_t\bigl(x(t; x_0), t\bigr) "
                    r"+ \frac{dx}{dt}\, u_x\bigl(x(t; x_0), t\bigr)",
                    r"&= u_t + u(x, t)\, u_x \quad "
                    r"\bigl(\text{porque } dx/dt = u_0(x_0) = u\bigr),",
                    r"\Rightarrow\quad u_t + u\, u_x &= 0 "
                    r"\quad \blacksquare.",
                ]
            ),
            level="intermediate",
        )

    # ===========================================================================
    # Visualization
    # ===========================================================================

    def _step_visualization(
        self, monotonicity: str, breaking_time: sp.Basic | None
    ) -> Step:
        if monotonicity == "non_decreasing":
            extra = (
                "Como el dato inicial es no decreciente, no aparece "
                "choque y la solución es suave para todo tiempo. La "
                "**rarefacción** (\"abanico\" de características "
                "divergentes) es la imagen característica."
            )
        elif monotonicity == "decreasing_somewhere" and breaking_time and breaking_time != sp.oo:
            extra = (
                f"En el plano $(x, t)$, las características "
                f"convergen y se cruzan en torno a $t \\approx "
                f"{sp.latex(breaking_time)}$ — ahí se forma el primer "
                f"choque. Más allá de ese tiempo la representación "
                f"implícita deja de ser una función bien definida."
            )
        else:
            extra = (
                "La evolución hasta antes del choque (si existe) se "
                "muestra a continuación. Las líneas rectas son las "
                "características; donde se cruzan, hay choque."
            )
        return step(
            kind="visualization",
            title="Paso 8 — Visualización (haz de características)",
            md=(
                "Cada línea recta del gráfico es una característica "
                "$x = x_0 + u_0(x_0) t$. La pendiente codifica la "
                "velocidad de transporte local, que iguala a $u$. "
                + extra
            ),
            level="basic",
        )

    # ===========================================================================
    # Physical
    # ===========================================================================

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_burgers_physical_interpretation(),
            level="basic",
            observations=[
                obs.get("burgers_self_steepening"),
                obs.get("burgers_vanishing_viscosity"),
            ],
        )
