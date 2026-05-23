"""Generic linear 2nd-order PDE classifier and canonical-form reducer.

This is the **fallback** method: it activates when no specific solver
in the repertoire matches. Given any linear 2nd-order PDE in two
variables (x, y) or (x, t):

    A u_{ξ1 ξ1} + B u_{ξ1 ξ2} + C u_{ξ2 ξ2} + (lower order) = 0,

we:

1. Read A, B, C off the equation by SymPy coefficient extraction.
2. Compute the discriminant Δ = B² − 4AC.
3. Classify the equation (hyperbolic / parabolic / elliptic).
4. Solve the characteristic equation A m² − B m + C = 0.
5. Build the change of variables ξ, η aligned to the characteristics
   and report the canonical form.
6. If the equation is hyperbolic with **constant coefficients** and
   no lower-order terms, give the explicit general solution
   u = F(ξ) + G(η). Otherwise honestly report that no closed-form
   solution is available without boundary/initial conditions.

Why this lives in the repertoire
--------------------------------
The original spec explicitly listed "general 2nd-order" alongside the
specific equations. The pedagogical value is enormous even without a
closed form: students learn that *every* linear 2nd-order PDE falls
into exactly one of three families, each with characteristic
physical behaviour. This method makes that lesson reachable for
arbitrary inputs.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_pde_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class GeneralSecondOrder(Method):
    """Fallback classifier + canonical-form reducer for any 2nd-order PDE."""

    slug = "general_second_order"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        parsed = parse_pde_latex(problem.equation_latex, problem.parameters)
        u = parsed.u
        # Independent variables: (x, y) for stationary, (x, t) for evolution.
        if parsed.time_var is not None and len(parsed.spatial_vars) >= 1:
            xi1 = parsed.spatial_vars[0]
            xi2 = parsed.time_var
            xi1_name, xi2_name = "x", "t"
        else:
            # Stationary: (x, y) — possibly (x, z) but we relabel to (x, y).
            xi1 = parsed.spatial_vars[0]
            xi2 = (
                parsed.spatial_vars[1]
                if len(parsed.spatial_vars) >= 2
                else sp.Symbol("y", real=True)
            )
            xi1_name, xi2_name = str(xi1), str(xi2)

        u_of = u(xi1, xi2)
        expr = parsed.expr

        # Extract coefficients A, B, C of u_{xi1 xi1}, u_{xi1 xi2}, u_{xi2 xi2}.
        A = sp.simplify(expr.coeff(sp.Derivative(u_of, xi1, 2)))
        B = sp.simplify(expr.coeff(sp.Derivative(u_of, xi1, xi2)))
        C = sp.simplify(expr.coeff(sp.Derivative(u_of, xi2, 2)))

        discriminant = sp.simplify(B**2 - 4 * A * C)
        family = self._classify(discriminant)

        steps: list[Step] = []

        # ===== PASO 0 — Statement ============================================
        steps.append(self._step_statement(problem.equation_latex, xi1_name, xi2_name))

        # ===== PASO 1 — Identify coefficients ===============================
        steps.append(
            self._step_identify_coeffs(A, B, C, xi1_name, xi2_name)
        )

        # ===== PASO 2 — Method choice ========================================
        steps.append(self._step_method_choice())

        # ===== PASO 3 — Discriminant + classification =======================
        steps.append(
            self._step_discriminant(A, B, C, discriminant, family)
        )

        # ===== PASO 4 — Characteristics =====================================
        roots, root_kind = self._characteristic_roots(A, B, C, discriminant)
        steps.append(
            self._step_characteristics(
                A, B, discriminant, roots, root_kind, xi1_name, xi2_name
            )
        )

        # ===== PASO 5 — Canonical change of variables ========================
        steps.append(
            self._step_canonical_change(family, roots, xi1_name, xi2_name)
        )

        # ===== PASO 6 — Final formula (or honest dropout) ===================
        solution_expr, gave_closed_form = self._final_formula(
            family, A, B, C, roots, expr, u_of, xi1, xi2
        )
        steps.append(
            self._step_final(
                family, gave_closed_form, solution_expr, xi1_name, xi2_name
            )
        )

        # ===== PASO 7 — Verification (only if closed form available) =========
        if gave_closed_form:
            steps.append(self._step_verification(xi1_name, xi2_name))

        # ===== PASO 8 — Visualization (skipped — no concrete u) ==============
        # We skip this for the generic case.

        # ===== PASO 9 — Physical interpretation ==============================
        steps.append(self._step_physical())

        artifact_expr = solution_expr if gave_closed_form else u_of
        return steps, SolutionArtifacts(
            solution_expr=artifact_expr,
            solution_latex=sp.latex(artifact_expr),
        )

    # ===========================================================================
    # Classification
    # ===========================================================================

    @staticmethod
    def _classify(discriminant: sp.Basic) -> str:
        """Return one of 'hyperbolic', 'parabolic', 'elliptic', 'undetermined'."""
        try:
            is_pos = discriminant.is_positive
            is_neg = discriminant.is_negative
            is_zero = discriminant.is_zero
        except Exception:
            is_pos = is_neg = is_zero = None
        if is_zero:
            return "parabolic"
        if is_pos:
            return "hyperbolic"
        if is_neg:
            return "elliptic"
        # Numeric test for symbolic ambiguity.
        try:
            sample = float(discriminant.subs({s: 1 for s in discriminant.free_symbols}))
            if sample > 1e-12:
                return "hyperbolic"
            if sample < -1e-12:
                return "elliptic"
            return "parabolic"
        except Exception:
            return "undetermined"

    @staticmethod
    def _characteristic_roots(
        A: sp.Basic, B: sp.Basic, C: sp.Basic, discriminant: sp.Basic
    ) -> tuple[tuple[sp.Basic, ...], str]:
        """Solve A m² − B m + C = 0; return the roots and a label.

        We use the standard form A m² − B m + C = 0 (sign of B negated
        comes from the characteristic equation A (dxi2)² − B dxi1 dxi2 +
        C (dxi1)² = 0 dividing by dxi1²).
        """
        m = sp.Symbol("m")
        roots = sp.solve(A * m**2 - B * m + C, m)
        if len(roots) == 2 and roots[0] != roots[1]:
            return tuple(sp.simplify(r) for r in roots), "two_real_or_complex"
        if len(roots) >= 1:
            return (sp.simplify(roots[0]),), "double"
        return (), "none"

    # ===========================================================================
    # Steps
    # ===========================================================================

    def _step_statement(self, latex: str, xi1_name: str, xi2_name: str) -> Step:
        return step(
            kind="statement",
            title=f"Paso 0 — Planteamiento (EDP de 2°-orden en $({xi1_name}, {xi2_name})$)",
            md=T.T_statement_general_2nd_order(),
            latex=rf"\text{{EDP:}} \quad {latex}.",
            level="basic",
        )

    def _step_identify_coeffs(
        self,
        A: sp.Basic,
        B: sp.Basic,
        C: sp.Basic,
        xi1_name: str,
        xi2_name: str,
    ) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Identificación de coeficientes principales",
            md=(
                f"Leemos los coeficientes de los términos de **segundo "
                f"orden puros** y del **cruzado** comparando con la "
                f"forma estándar "
                f"$A u_{{{xi1_name}{xi1_name}}} + B u_{{{xi1_name}{xi2_name}}} "
                f"+ C u_{{{xi2_name}{xi2_name}}} + \\ldots = 0$:"
            ),
            latex=equation_chain(
                [
                    rf"A &= {sp.latex(A)},",
                    rf"B &= {sp.latex(B)},",
                    rf"C &= {sp.latex(C)}.",
                ]
            ),
            level="basic",
        )

    def _step_method_choice(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Estrategia: clasificar y reducir a forma canónica",
            md=T.T_general_method_choice(),
            level="basic",
            observations=[obs.get("classification_is_invariant")],
        )

    def _step_discriminant(
        self,
        A: sp.Basic,
        B: sp.Basic,
        C: sp.Basic,
        discriminant: sp.Basic,
        family: str,
    ) -> Step:
        family_label = {
            "hyperbolic": r"\Delta > 0 \Rightarrow \text{hiperbólica}",
            "parabolic": r"\Delta = 0 \Rightarrow \text{parabólica}",
            "elliptic": r"\Delta < 0 \Rightarrow \text{elíptica}",
            "undetermined": r"\Delta \text{ depende de los parámetros — clasificación abierta}",
        }[family]
        return step(
            kind="classification",
            title="Paso 3 — Discriminante y clasificación",
            md=(
                "Computamos $\\Delta = B^2 - 4AC$. Esta cantidad es "
                "**la** invariante que clasifica la EDP en una de las "
                "tres familias:"
            ),
            latex=equation_chain(
                [
                    rf"\Delta &= B^2 - 4AC "
                    rf"= ({sp.latex(B)})^2 - 4 ({sp.latex(A)}) ({sp.latex(C)})",
                    rf"&= {sp.latex(discriminant)},",
                    family_label + ".",
                ]
            ),
            level="basic",
            observations=[obs.get("three_families_three_physics")],
        )

    def _step_characteristics(
        self,
        A: sp.Basic,
        B: sp.Basic,
        discriminant: sp.Basic,
        roots: tuple[sp.Basic, ...],
        root_kind: str,
        xi1_name: str,
        xi2_name: str,
    ) -> Step:
        lines = [
            r"A\, m^2 - B\, m + C &= 0,",
            rf"m &= \frac{{B \pm \sqrt{{\Delta}}}}{{2A}}"
            rf" = \frac{{{sp.latex(B)} \pm \sqrt{{{sp.latex(discriminant)}}}}}"
            rf"{{2({sp.latex(A)})}}.",
        ]
        if root_kind == "two_real_or_complex" and len(roots) == 2:
            lines.append(
                rf"\Rightarrow\ m_1 = {sp.latex(roots[0])},\quad "
                rf"m_2 = {sp.latex(roots[1])}."
            )
        elif root_kind == "double" and len(roots) == 1:
            lines.append(
                rf"\Rightarrow\ m_1 = m_2 = {sp.latex(roots[0])} "
                rf"\quad (\text{{raíz doble}})."
            )
        return step(
            kind="development",
            title="Paso 4 — Ecuación característica",
            md=T.T_general_characteristics(),
            latex=equation_chain(lines),
            level="intermediate",
            observations=[obs.get("characteristics_lose_uniqueness")],
        )

    def _step_canonical_change(
        self,
        family: str,
        roots: tuple[sp.Basic, ...],
        xi1_name: str,
        xi2_name: str,
    ) -> Step:
        if family == "hyperbolic" and len(roots) == 2:
            m1, m2 = roots
            lines = [
                rf"\xi &= {xi2_name} - ({sp.latex(m1)})\, {xi1_name},",
                rf"\eta &= {xi2_name} - ({sp.latex(m2)})\, {xi1_name},",
                r"\text{forma canónica:}\quad u_{\xi \eta} + "
                r"(\text{orden inferior}) = 0.",
            ]
        elif family == "parabolic" and len(roots) >= 1:
            m = roots[0]
            lines = [
                rf"\xi &= {xi2_name} - ({sp.latex(m)})\, {xi1_name} "
                rf"\quad (\text{{característica única}}),",
                rf"\eta &= {xi1_name} \quad (\text{{variable transversal}}),",
                r"\text{forma canónica:}\quad u_{\eta\eta} + "
                r"(\text{orden inferior}) = 0.",
            ]
        elif family == "elliptic" and len(roots) == 2:
            m1 = roots[0]
            re_m, im_m = sp.re(m1), sp.im(m1)
            lines = [
                rf"m_{{1,2}} &= {sp.latex(re_m)} \pm i\, ({sp.latex(sp.Abs(im_m))}),",
                rf"\sigma &= {xi2_name} - ({sp.latex(re_m)})\, {xi1_name},",
                rf"\tau &= ({sp.latex(sp.Abs(im_m))})\, {xi1_name},",
                r"\text{forma canónica:}\quad u_{\sigma\sigma} + "
                r"u_{\tau\tau} + (\text{orden inferior}) = 0.",
            ]
        else:
            lines = [
                r"\text{Sin clasificación cerrada — los coeficientes "
                r"dependen de parámetros sin signo determinado.}"
            ]
        return step(
            kind="development",
            title="Paso 5 — Cambio canónico de variables",
            md=T.T_general_canonical_form(),
            latex=equation_chain(lines),
            level="intermediate",
        )

    # ===========================================================================
    # Final formula
    # ===========================================================================

    def _final_formula(
        self,
        family: str,
        A: sp.Basic,
        B: sp.Basic,
        C: sp.Basic,
        roots: tuple[sp.Basic, ...],
        expr: sp.Basic,
        u_of: sp.Basic,
        xi1: sp.Symbol,
        xi2: sp.Symbol,
    ) -> tuple[sp.Basic, bool]:
        """Return (solution_expr, closed_form_available).

        Closed form is available only for hyperbolic + constant
        coefficients + no lower-order terms (the equation is exactly
        A u_{ξ1ξ1} + B u_{ξ1ξ2} + C u_{ξ2ξ2} = 0).
        """
        if family != "hyperbolic" or len(roots) != 2:
            return u_of, False

        # Constant-coefficient check: A, B, C must have no x/t/y free symbols
        # other than the equation parameters (which we treat as constants).
        coords = {xi1, xi2}
        for coeff in (A, B, C):
            if coords & coeff.free_symbols:
                return u_of, False

        # No lower-order terms check: the equation must be exactly the
        # 2nd-order part. Build the 2nd-order-only expression and compare.
        u = u_of.func
        second_order_part = (
            A * sp.Derivative(u(xi1, xi2), xi1, 2)
            + B * sp.Derivative(u(xi1, xi2), xi1, xi2)
            + C * sp.Derivative(u(xi1, xi2), xi2, 2)
        )
        residual = sp.simplify(expr - second_order_part)
        if residual != 0:
            return u_of, False

        m1, m2 = roots
        xi = xi2 - m1 * xi1
        eta = xi2 - m2 * xi1
        F = sp.Function("F")
        G = sp.Function("G")
        u_expr = F(xi) + G(eta)
        return u_expr, True

    def _step_final(
        self,
        family: str,
        gave_closed_form: bool,
        solution_expr: sp.Basic,
        xi1_name: str,
        xi2_name: str,
    ) -> Step:
        if gave_closed_form:
            md = T.T_general_hyperbolic_closed_form()
            latex = rf"\boxed{{\; u({xi1_name}, {xi2_name}) = {sp.latex(solution_expr)} \;}}"
            return step(
                kind="final",
                title="Paso 6 — Solución general (D'Alembert generalizado)",
                md=md,
                latex=latex,
                sympy_expr=solution_expr,
                level="basic",
            )
        # Honest dropout case.
        return step(
            kind="final",
            title="Paso 6 — Forma canónica entregada (sin solución cerrada general)",
            md=T.T_general_no_closed_form(),
            latex=(
                rf"u({xi1_name}, {xi2_name}) "
                r"= \text{solución dependiente de BCs/ICs aún no especificadas}."
            ),
            level="basic",
        )

    # ===========================================================================
    # Verification (only when closed form exists)
    # ===========================================================================

    def _step_verification(
        self,
        xi1_name: str,
        xi2_name: str,
    ) -> Step:
        # The verification is *algebraic* — by the chain rule on
        # u = F(ξ) + G(η) with ξ = ξ2 − m1 ξ1, η = ξ2 − m2 ξ1:
        #   A u_{ξ1ξ1} + B u_{ξ1ξ2} + C u_{ξ2ξ2}
        #     = (A m1² − B m1 + C) F''(ξ) + (A m2² − B m2 + C) G''(η)
        # which vanishes identically because m1, m2 are roots of the
        # characteristic polynomial A m² − B m + C. We render this
        # chain of equalities in LaTeX; no SymPy computation needed.
        return step(
            kind="verification",
            title=r"Paso 7 — Verificación de la solución u = F(\xi) + G(\eta)",
            md=(
                "Aplicando regla de la cadena a $u = F(\\xi) + G(\\eta)$ "
                "con $\\xi = \\xi_2 - m_1 \\xi_1$, $\\eta = \\xi_2 - "
                "m_2 \\xi_1$:"
            ),
            latex=equation_chain(
                [
                    rf"u_{{{xi1_name}}} &= -m_1\, F'(\xi) - m_2\, G'(\eta),",
                    rf"u_{{{xi1_name}{xi1_name}}} &= "
                    rf"m_1^2\, F''(\xi) + m_2^2\, G''(\eta),",
                    rf"u_{{{xi1_name}{xi2_name}}} &= "
                    rf"-m_1\, F''(\xi) - m_2\, G''(\eta),",
                    rf"u_{{{xi2_name}{xi2_name}}} &= F''(\xi) + G''(\eta),",
                    r"A u_{xx} + B u_{xy} + C u_{yy} "
                    r"&= (A m_1^2 - B m_1 + C) F'' "
                    r"+ (A m_2^2 - B m_2 + C) G''",
                    r"&= 0 + 0 = 0 \quad "
                    r"(\text{por ser } m_1, m_2 \text{ raíces de } "
                    r"A m^2 - B m + C = 0). \qquad \blacksquare",
                ]
            ),
            level="intermediate",
        )

    # ===========================================================================
    # Physical interpretation
    # ===========================================================================

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física de la clasificación",
            md=T.T_general_physical_interpretation(),
            level="basic",
            observations=[obs.get("three_families_three_physics")],
        )
