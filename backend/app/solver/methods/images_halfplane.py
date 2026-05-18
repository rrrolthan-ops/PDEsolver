"""Method of images for Laplace in the upper half-plane.

Problem covered
---------------
    Δu = 0           in y > 0
    u(x, 0) = f(x)
    u → 0 at infinity

Result: u(x, y) = (y/π) ∫_{-∞}^∞ f(x') / ((x - x')² + y²) dx'.

This method file does two things didactically:

1. Constructs the Green function explicitly by placing a mirror image,
   shows that boundary value vanishes, and derives the Poisson kernel
   by taking the normal derivative.
2. Substitutes a given f and (where SymPy can) closes the integral
   into elementary functions. For sample data we usually keep the
   integral form for clarity.
"""

from __future__ import annotations

import sympy as sp

from app.parser.latex_to_sympy import parse_scalar_latex
from app.schemas import PDEProblem, Step
from app.solver.core.step_builder import equation_chain, step
from app.solver.pedagogy import observations as obs
from app.solver.pedagogy import templates as T

from .base import Method, SolutionArtifacts


class ImagesHalfPlane(Method):
    """Laplace in the upper half-plane via the method of images."""

    slug = "images_halfplane"

    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        x = sp.Symbol("x", real=True)
        y = sp.Symbol("y", positive=True)
        xp = sp.Symbol("xprime", real=True)

        # Extract f(x) from the y=0 BC.
        f_latex = "0"
        for bc in problem.boundary_conditions:
            if bc.where.replace(" ", "").lower().startswith("y=0"):
                f_latex = bc.value
                break
        f_expr = parse_scalar_latex(f_latex, problem.parameters).subs(sp.Symbol("x"), x)
        f_of_xp = f_expr.subs(x, xp)

        steps: list[Step] = []
        steps.append(self._step_statement(f_latex))
        steps.append(self._step_classification())
        steps.append(self._step_method_motivation())
        steps += self._steps_green_construction()
        steps.append(self._step_poisson_kernel())
        solution_expr, integral_form = self._build_solution(f_of_xp, x, y, xp)
        steps += self._steps_apply(f_latex, integral_form, solution_expr)
        steps.append(self._step_final(solution_expr, integral_form))
        steps += self._steps_verification(solution_expr, f_expr, x, y)
        steps.append(self._step_physical())

        return steps, SolutionArtifacts(
            solution_expr=solution_expr,
            solution_latex=sp.latex(solution_expr),
        )

    # ---------------------------------------------------------------------

    def _step_statement(self, f_latex: str) -> Step:
        return step(
            kind="statement",
            title="Paso 0 — Planteamiento (Laplace en semiplano)",
            md=T.T_statement_images_halfplane(),
            latex=equation_chain(
                [
                    r"&\Delta u = u_{xx} + u_{yy} = 0,\quad y > 0,",
                    rf"&u(x, 0) = {f_latex},",
                    r"&u \to 0 \text{ cuando } x^2 + y^2 \to \infty.",
                ]
            ),
            level="basic",
        )

    def _step_classification(self) -> Step:
        return step(
            kind="classification",
            title="Paso 1 — Clasificación: elíptica en dominio no acotado",
            md=(
                "Laplace es elíptica. El semiplano es un dominio no "
                "acotado, así que perdemos parte de la maquinaria "
                "habitual (los espectros pasan a ser continuos, las "
                "expansiones se convierten en transformadas de Fourier). "
                "El método de imágenes evita esto reduciendo el problema "
                "al cálculo directo de una función de Green."
            ),
            level="basic",
            observations=[obs.get("laplace_max_principle")],
        )

    def _step_method_motivation(self) -> Step:
        return step(
            kind="method_choice",
            title="Paso 2 — Método de las imágenes",
            md=T.T_images_method_motivation(),
            level="basic",
            observations=[obs.get("images_mirror_trick")],
        )

    def _steps_green_construction(self) -> list[Step]:
        s = step(
            kind="development",
            title="Paso 3 — Construcción de la función de Green",
            md=T.T_images_green_construction(),
            level="basic",
        )
        return [s]

    def _step_poisson_kernel(self) -> Step:
        return step(
            kind="development",
            title="Paso 3.1 — Derivada normal de $G$ → núcleo de Poisson",
            md=T.T_images_poisson_kernel(),
            level="intermediate",
        )

    def _build_solution(
        self,
        f_of_xp: sp.Basic,
        x: sp.Symbol,
        y: sp.Symbol,
        xp: sp.Symbol,
    ) -> tuple[sp.Basic, sp.Basic]:
        """Return (solution, integral form).

        We **deliberately do not try to close the integral**. For most
        non-trivial `f`, SymPy's `integrate` over `(-∞, ∞)` can hang
        searching for residue-style answers it never finds. The
        integral form is the canonical pedagogical answer for the
        method of images, so we keep it as-is.

        Two special cases are recognized cheaply:
        - `f ≡ 0` → solution is `0`.
        - `f ≡ const` → solution is the constant (the Poisson kernel
          integrates to 1, so the constant passes through).
        """
        integrand = (y / sp.pi) * f_of_xp / ((x - xp) ** 2 + y**2)
        integral_form = sp.Integral(integrand, (xp, -sp.oo, sp.oo))

        # Cheap closed forms: f is a constant (xp does not appear in it).
        if xp not in f_of_xp.free_symbols:
            # The factor depending on xp integrates to π/y, and we have
            # (y/π) outside, so the constant survives.
            return sp.simplify(f_of_xp), integral_form

        return integral_form, integral_form

    def _steps_apply(
        self,
        f_latex: str,
        integral_form: sp.Basic,
        solution_expr: sp.Basic,
    ) -> list[Step]:
        s_setup = step(
            kind="initial",
            title=f"Paso 5 — Aplicación a $f(x) = {f_latex}$",
            md=(
                "Sustituimos $f$ en la fórmula de Poisson. Si SymPy "
                "puede cerrar la integral, lo hace; si no, dejamos la "
                "forma integral (sigue siendo una respuesta perfectamente "
                "válida — la convolución con el núcleo de Poisson)."
            ),
            latex=rf"u(x, y) = {sp.latex(integral_form)}.",
            level="basic",
        )
        s_result = step(
            kind="initial",
            title="Resultado",
            md="Tras integrar (o dejarlo planteado):",
            latex=rf"u(x, y) = {sp.latex(solution_expr)}.",
            sympy_expr=solution_expr,
            level="basic",
        )
        return [s_setup, s_result]

    def _step_final(self, solution_expr: sp.Basic, integral_form: sp.Basic) -> Step:
        # Show both forms when they differ.
        if str(solution_expr) == str(integral_form):
            body = rf"\boxed{{\; u(x, y) = {sp.latex(solution_expr)} \;}}"
        else:
            body = (
                r"\begin{aligned}"
                rf"u(x, y) &= {sp.latex(integral_form)}\\[6pt]"
                rf"&= {sp.latex(solution_expr)}."
                r"\end{aligned}"
            )
        return step(
            kind="final",
            title="Paso 6 — Solución",
            md=T.T_images_solution_formula(),
            latex=body,
            sympy_expr=solution_expr,
            level="basic",
        )

    def _steps_verification(
        self,
        solution_expr: sp.Basic,
        f_expr: sp.Basic,
        x: sp.Symbol,
        y: sp.Symbol,
    ) -> list[Step]:
        # Heuristic verification: when the closed-form exists and is
        # differentiable in SymPy, check Δu = 0.
        try:
            laplacian = sp.simplify(
                sp.diff(solution_expr, x, 2) + sp.diff(solution_expr, y, 2)
            )
            pde_ok = bool(laplacian == 0)
        except Exception:
            laplacian = sp.Symbol("?")
            pde_ok = False

        s_intro = step(
            kind="verification",
            title="Paso 7 — Verificación",
            md=(
                "Si SymPy logró cerrar la integral, comprobamos "
                "$\\Delta u = 0$ directamente. Si no, apelamos al hecho "
                "**estructural** de que el núcleo de Poisson es armónico "
                "en $y > 0$ y la integral de Poisson preserva la "
                "armonicidad: la solución es armónica por construcción."
            ),
            level="basic",
        )
        if pde_ok:
            s_check = step(
                kind="verification",
                title="$\\Delta u = 0$ comprobado simbólicamente",
                md="La suma $u_{xx} + u_{yy}$ se simplifica a cero.",
                latex=rf"\Delta u = {sp.latex(laplacian)}.",
                level="intermediate",
            )
        else:
            s_check = step(
                kind="verification",
                title="Armonicidad por construcción",
                md=(
                    "SymPy no cerró la integral en forma elemental, "
                    "pero la armonicidad sale del hecho de que "
                    "$P(x-x', y)$ es armónico en $(x, y)$ y la integral "
                    "preserva armonicidad."
                ),
                level="intermediate",
            )
        return [s_intro, s_check]

    def _step_physical(self) -> Step:
        return step(
            kind="interpretation",
            title="Paso 9 — Interpretación física",
            md=T.T_images_physical_interpretation(),
            level="basic",
            observations=[obs.get("images_general_geometry")],
        )
