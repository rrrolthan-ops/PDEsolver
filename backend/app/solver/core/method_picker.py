"""Pick a solution method given a `PDEProblem`.

Registry pattern: each `(predicate, slug, builder)` tuple says "if the
problem matches this predicate, this is the slug to dispatch to and
here's how to build the rationale step". Predicates are evaluated in
**registration order**, so register more specific methods first.

The rationale is returned as a `MethodChoice` and rendered into Paso 2
of the solution. Each method module also references its own
`MethodChoice` from within `solve`, which keeps the "why this method"
text in one place rather than scattered across method picker + method.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.schemas import PDEProblem


@dataclass
class MethodChoice:
    method_slug: str
    rationale_md: str
    alternatives_md: str


# ---------------------------------------------------------------------------
# Eligibility predicates
# ---------------------------------------------------------------------------


def _has_1d_interval_domain(p: PDEProblem) -> bool:
    return p.domain.x is not None and p.domain.y is None and p.domain.z is None


def _is_unbounded_x(p: PDEProblem) -> bool:
    if p.domain.x is None:
        return False
    lo, hi = p.domain.x
    return lo.strip().lower() in {"-infty", "-inf", "-oo"} and hi.strip().lower() in {
        "infty",
        "inf",
        "oo",
    }


def _all_dirichlet_zero(p: PDEProblem) -> bool:
    if not p.boundary_conditions:
        return False
    return all(
        bc.type == "dirichlet" and bc.value.strip() == "0"
        for bc in p.boundary_conditions
    )


def _looks_like_heat_1d(p: PDEProblem) -> bool:
    if p.equation_kind == "heat":
        return (
            _has_1d_interval_domain(p)
            and not _is_unbounded_x(p)
            and _all_dirichlet_zero(p)
        )
    latex = p.equation_latex.replace(" ", "").lower()
    heat_shapes = ("u_t=alpha^2*u_{xx}", "u_t=alpha^2u_{xx}", "u_t=a^2u_{xx}")
    return (
        any(s in latex for s in heat_shapes)
        and _has_1d_interval_domain(p)
        and not _is_unbounded_x(p)
        and _all_dirichlet_zero(p)
    )


def _looks_like_heat_1d_unbounded(p: PDEProblem) -> bool:
    """Heat equation on the real line — Fourier transform / Gaussian kernel."""
    if p.equation_kind == "heat":
        return _is_unbounded_x(p)
    latex = p.equation_latex.replace(" ", "").lower()
    heat_shapes = ("u_t=alpha^2*u_{xx}", "u_t=alpha^2u_{xx}", "u_t=a^2u_{xx}")
    return any(s in latex for s in heat_shapes) and _is_unbounded_x(p)


def _is_semi_infinite_x_nonneg(p: PDEProblem) -> bool:
    """x ∈ [0, ∞): lower bound is zero, upper bound is +∞."""
    if p.domain.x is None:
        return False
    lo, hi = (s.strip().lower() for s in p.domain.x)
    return lo == "0" and hi in {"infty", "inf", "oo"}


def _has_dirichlet_at_x0(p: PDEProblem) -> bool:
    for bc in p.boundary_conditions:
        where = bc.where.replace(" ", "").lower()
        if bc.type == "dirichlet" and where in {"x=0", "0"}:
            return True
    return False


def _looks_like_heat_halfline(p: PDEProblem) -> bool:
    """Heat on x ∈ [0, ∞) with prescribed temperature at the wall — Laplace in t."""
    if p.equation_kind == "heat":
        return (
            _is_semi_infinite_x_nonneg(p)
            and p.domain.y is None
            and _has_dirichlet_at_x0(p)
        )
    latex = p.equation_latex.replace(" ", "").lower()
    heat_shapes = ("u_t=alpha^2*u_{xx}", "u_t=alpha^2u_{xx}", "u_t=a^2u_{xx}")
    return (
        any(s in latex for s in heat_shapes)
        and _is_semi_infinite_x_nonneg(p)
        and p.domain.y is None
        and _has_dirichlet_at_x0(p)
    )


def _looks_like_wave_1d_bounded(p: PDEProblem) -> bool:
    if p.equation_kind == "wave":
        return _has_1d_interval_domain(p) and not _is_unbounded_x(p) and _all_dirichlet_zero(p)
    latex = p.equation_latex.replace(" ", "").lower()
    wave_shapes = ("u_{tt}=c^2*u_{xx}", "u_{tt}=c^2u_{xx}", "u_tt=c^2u_xx")
    return (
        any(s in latex for s in wave_shapes)
        and _has_1d_interval_domain(p)
        and not _is_unbounded_x(p)
        and _all_dirichlet_zero(p)
    )


def _looks_like_wave_1d_unbounded(p: PDEProblem) -> bool:
    if p.equation_kind == "wave":
        return _is_unbounded_x(p)
    latex = p.equation_latex.replace(" ", "").lower()
    wave_shapes = ("u_{tt}=c^2*u_{xx}", "u_{tt}=c^2u_{xx}", "u_tt=c^2u_xx")
    return any(s in latex for s in wave_shapes) and _is_unbounded_x(p)


def _looks_like_laplace_rect(p: PDEProblem) -> bool:
    """Cartesian rectangle: Laplace, 2D, geometry not disk."""
    if p.geometry == "disk":
        return False
    if p.equation_kind == "laplace":
        # Heuristic: rectangle has both x and y bounded by parameters
        # like "a" and "b" (not "R", not implicit polar).
        return (
            p.domain.x is not None
            and p.domain.y is not None
            and p.domain.t is None
            and (p.geometry in (None, "rectangle"))
        )
    latex = p.equation_latex.replace(" ", "").lower()
    laplace_shapes = (
        "u_{xx}+u_{yy}=0",
        "u_xx+u_yy=0",
        "\\nabla^2u=0",
        "nabla^2u=0",
    )
    return (
        any(s in latex for s in laplace_shapes)
        and p.domain.x is not None
        and p.domain.y is not None
        and p.domain.t is None
        and (p.geometry in (None, "rectangle"))
    )


def _looks_like_laplace_disk(p: PDEProblem) -> bool:
    """Laplace on a disk: geometry hint set, or BC location uses r=R."""
    if p.geometry == "disk":
        return p.equation_kind in ("laplace", "general")
    # Fallback: a BC `where = "r=R"` is a strong signal of polar geometry.
    if p.equation_kind == "laplace":
        for bc in p.boundary_conditions:
            if bc.where.replace(" ", "").lower().startswith("r="):
                return True
    return False


def _looks_like_poisson_1d(p: PDEProblem) -> bool:
    """1D Poisson with a non-zero source on a bounded interval."""
    if p.equation_kind == "poisson" and _has_1d_interval_domain(p):
        return True
    # Heuristic from the source_term field alone.
    if p.source_term and p.source_term.strip() not in {"", "0"} and _has_1d_interval_domain(p):
        latex = p.equation_latex.replace(" ", "").lower()
        if "u_{xx}" in latex or "u''" in latex:
            return True
    return False


def _looks_like_helmholtz_rect(p: PDEProblem) -> bool:
    if p.equation_kind == "helmholtz":
        return p.domain.x is not None and p.domain.y is not None and p.domain.t is None
    latex = p.equation_latex.replace(" ", "").lower()
    helmholtz_shapes = (
        "\\nabla^2u+k^2u=",
        "nabla^2u+k^2u=",
        "u_{xx}+u_{yy}+k^2u=",
    )
    return (
        any(s in latex for s in helmholtz_shapes)
        and p.domain.x is not None
        and p.domain.y is not None
    )


def _looks_like_telegraph(p: PDEProblem) -> bool:
    if p.equation_kind == "telegraph":
        return _has_1d_interval_domain(p) and _all_dirichlet_zero(p)
    latex = p.equation_latex.replace(" ", "").lower()
    # Detect any of u_t with alpha (and not heat's pure u_t = alpha² u_xx).
    has_utt = "u_{tt}" in latex or "u_tt" in latex
    has_ut = "u_t" in latex
    has_alpha = "alpha" in latex
    return (
        has_utt
        and has_ut
        and has_alpha
        and _has_1d_interval_domain(p)
        and _all_dirichlet_zero(p)
    )


def _looks_like_schrodinger_well(p: PDEProblem) -> bool:
    """Schrödinger in a 1D infinite well: bounded interval + Dirichlet 0."""
    if p.equation_kind == "schrodinger":
        return (
            _has_1d_interval_domain(p)
            and not _is_unbounded_x(p)
            and _all_dirichlet_zero(p)
        )
    latex = p.equation_latex.replace(" ", "").lower()
    # `i*hbar*u_t = -hbar^2/(2*m)*u_xx` or variants.
    has_hbar = "hbar" in latex
    has_i_u_t = "i*hbar*u_t" in latex or "i hbar u_t" in latex or "ihbar*u_t" in latex
    return (
        has_hbar
        and has_i_u_t
        and _has_1d_interval_domain(p)
        and not _is_unbounded_x(p)
        and _all_dirichlet_zero(p)
    )


def _looks_like_schrodinger_oscillator(p: PDEProblem) -> bool:
    """Quantum harmonic oscillator: Schrödinger on the real line with V = ½mω²x²."""
    latex_raw = p.equation_latex.replace(" ", "").lower()
    has_omega_squared_x = "omega^2*x^2" in latex_raw or "omega^2x^2" in latex_raw
    if p.equation_kind == "schrodinger":
        # The oscillator is *specifically* the case with a quadratic
        # potential. Free Schrödinger on the line (no potential) routes
        # to `_looks_like_schrodinger_free` instead — so we now require
        # the explicit ω²x² signature in latex (or a `parameters` entry
        # for `omega`) to claim this slot.
        if not has_omega_squared_x and "omega" not in p.parameters:
            return False
        if _is_unbounded_x(p):
            return True
        # Bounded domain *plus* an explicit quadratic potential in
        # the latex — also oscillator (a confined harmonic trap).
        return has_omega_squared_x
    # Fallback: equation_kind not set, but latex carries the signature.
    has_hbar = "hbar" in latex_raw
    return has_hbar and has_omega_squared_x and _is_unbounded_x(p)


def _looks_like_schrodinger_free(p: PDEProblem) -> bool:
    """Free particle: Schrödinger on the real line with V = 0."""
    latex_raw = p.equation_latex.replace(" ", "").lower()
    has_omega_squared_x = "omega^2*x^2" in latex_raw or "omega^2x^2" in latex_raw
    # A potential of any other shape (V(x)*u, V*u, etc.) excludes us;
    # we only handle the pure-kinetic-energy case here.
    has_potential_term = "v(x)" in latex_raw or "+v*" in latex_raw
    if has_omega_squared_x or has_potential_term:
        return False
    if p.equation_kind == "schrodinger":
        return _is_unbounded_x(p)
    has_hbar = "hbar" in latex_raw
    has_i_u_t = (
        "i*hbar*u_t" in latex_raw
        or "ihbar*u_t" in latex_raw
        or "i\\hbaru_t" in latex_raw
        or "i*hbar\\psi_t" in latex_raw
    )
    return has_hbar and has_i_u_t and _is_unbounded_x(p)


def _looks_like_characteristics_transport(p: PDEProblem) -> bool:
    """First-order transport u_t + c u_x = 0 on the line."""
    if p.equation_kind == "general":
        latex = p.equation_latex.replace(" ", "").lower()
        if ("u_t+c*u_x=0" in latex or "u_t+cu_x=0" in latex) and _is_unbounded_x(p):
            return True
    # No dedicated equation_kind; rely on latex shape.
    latex = p.equation_latex.replace(" ", "").lower()
    transport_shapes = ("u_t+c*u_x=0", "u_t+cu_x=0", "u_t+c\\cdotu_x=0")
    return any(s in latex for s in transport_shapes) and _is_unbounded_x(p)


def _looks_like_biharmonic_beam(p: PDEProblem) -> bool:
    """1D biharmonic / beam: EI u'''' = q on bounded interval."""
    if p.equation_kind == "biharmonic" and _has_1d_interval_domain(p):
        return True
    latex = p.equation_latex.replace(" ", "").lower()
    # Match u'''' (any spacing).
    has_4thder = (
        "u''''" in latex
        or "u^{(4)}" in latex
        or "u_{xxxx}" in latex
        or "\\nabla^4u" in latex
    )
    return has_4thder and _has_1d_interval_domain(p)


def _looks_like_wave_disk(p: PDEProblem) -> bool:
    """Wave on a disk: geometry hint == disk, equation_kind == wave."""
    if p.geometry != "disk":
        return False
    if p.equation_kind == "wave":
        return True
    latex = p.equation_latex.replace(" ", "").lower()
    return "u_{tt}" in latex or "u_tt" in latex


def _looks_like_heat_disk(p: PDEProblem) -> bool:
    """Heat on a disk: geometry hint == disk, equation_kind == heat."""
    if p.geometry != "disk":
        return False
    if p.equation_kind == "heat":
        return True
    latex = p.equation_latex.replace(" ", "").lower()
    # u_t with alpha², not u_tt
    return ("u_t=" in latex or "u_t-" in latex) and "u_{tt}" not in latex


def _looks_like_laplace_ball(p: PDEProblem) -> bool:
    """Laplace in a 3D ball: geometry hint == sphere."""
    if p.geometry != "sphere":
        return False
    if p.equation_kind == "laplace":
        return True
    latex = p.equation_latex.replace(" ", "").lower()
    return "nabla^2u" in latex or "\\nabla^2u" in latex or "\\delta" in latex


def _looks_like_second_order_general(p: PDEProblem) -> bool:
    """Catch-all for any linear 2nd-order PDE in two variables.

    Fires only as the last resort (registered at the end of the
    registry). Detects the presence of any 2nd-order derivative
    notation in the LaTeX.
    """
    latex = p.equation_latex.replace(" ", "").lower()
    second_order_markers = (
        "u_{xx}", "u_xx", "u_{yy}", "u_yy", "u_{tt}", "u_tt",
        "u_{xy}", "u_xy", "u_{xt}", "u_xt", "u_{yt}", "u_yt",
        "u_{yx}", "u_yx", "u_{tx}", "u_tx",
        "\\partial^2", "partial^2", "u_{xxxx}",
    )
    return any(m in latex for m in second_order_markers)


def _looks_like_images_halfplane(p: PDEProblem) -> bool:
    """Laplace on a half-plane: geometry hint or domain shape gives it away."""
    if p.geometry == "halfplane":
        return p.equation_kind in ("laplace", "general")
    # Otherwise: y in [0, infty], x in (-infty, infty), equation is Laplace.
    if p.domain.x is None or p.domain.y is None:
        return False
    y_bounds = [s.strip().lower() for s in p.domain.y]
    x_bounds = [s.strip().lower() for s in p.domain.x]
    y_is_halfline = y_bounds[0] == "0" and y_bounds[1] in {"infty", "inf", "oo"}
    x_is_line = x_bounds[0] in {"-infty", "-inf", "-oo"} and x_bounds[1] in {"infty", "inf", "oo"}
    if not (y_is_halfline and x_is_line):
        return False
    if p.equation_kind == "laplace":
        return True
    latex = p.equation_latex.replace(" ", "").lower()
    return "u_{xx}+u_{yy}=0" in latex or "u_xx+u_yy=0" in latex


# ---------------------------------------------------------------------------
# Choice builders — return a fresh `MethodChoice` per dispatch
# ---------------------------------------------------------------------------


def _choice_heat_1d_sov(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="separation_of_variables",
        rationale_md=(
            "Elegimos **separación de variables** porque concurren tres "
            "condiciones que la hacen no sólo aplicable, sino la opción "
            "natural:\n\n"
            "1. La EDP es **lineal y homogénea**.\n"
            "2. El dominio espacial es un **intervalo finito** $[0, L]$.\n"
            "3. Las **condiciones de contorno son homogéneas** "
            "($u(0, t) = u(L, t) = 0$), lo que produce un problema de "
            "Sturm-Liouville con autovalores discretos."
        ),
        alternatives_md=(
            "**Métodos descartados y por qué:**\n\n"
            "- *D'Alembert*: aplica a la ecuación de onda, no al calor.\n"
            "- *Transformada de Fourier*: requiere dominio espacial infinito.\n"
            "- *Transformada de Laplace en $t$*: viable, pero inversa "
            "lleva a la misma serie. Separación muestra los modos normales.\n"
            "- *Funciones de Green*: útiles cuando la EDP es no homogénea."
        ),
    )


def _choice_wave_1d_sov(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="sov_wave_1d",
        rationale_md=(
            "Igual que en el calor 1D, las tres condiciones de aplicabilidad "
            "se dan: linealidad y homogeneidad, intervalo finito, BCs "
            "homogéneas. Separación de variables produce la **descomposición "
            "modal** (modos normales) de la cuerda."
        ),
        alternatives_md=(
            "**Alternativa pedagógica:** la **fórmula de D'Alembert** "
            "resuelve el mismo problema en la línea infinita y, con "
            "extensiones periódicas impares, en el intervalo $[0, L]$. "
            "La equivalencia entre ambas vistas es uno de los hechos "
            "más instructivos del estudio de ondas."
        ),
    )


def _choice_general_second_order(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="general_second_order",
        rationale_md=(
            "Tu EDP es de **segundo orden lineal en dos variables**, "
            "pero no encaja con ninguno de los métodos específicos del "
            "repertorio (probablemente porque los coeficientes, la "
            "geometría o las BCs son no estándar). En lugar de "
            "dejarte sin respuesta, aplicamos el **flujo general**: "
            "clasificación por discriminante, ecuación característica "
            "y reducción a forma canónica.\n\n"
            "Este flujo siempre funciona y enseña la **estructura "
            "intrínseca** de la EDP (elíptica/parabólica/hiperbólica), "
            "que es la información cualitativa más importante."
        ),
        alternatives_md=(
            "Si tu EDP encaja en una geometría y BCs estándar, "
            "consulta el repertorio específico (separación de "
            "variables sobre rectángulo/disco/bola/segmento, "
            "D'Alembert, Green, imágenes, Bessel, Legendre, etc.). "
            "El flujo general que aplicamos aquí es una **caja de "
            "herramientas universal** pero a costa de no producir "
            "siempre una fórmula explícita."
        ),
    )


def _choice_laplace_heat_halfline(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="laplace_heat_halfline",
        rationale_md=(
            "El dominio espacial es **semi-infinito** $x \\in [0, \\infty)$, "
            "con una condición de **Dirichlet en la pared** $x = 0$ y "
            "decaimiento al infinito. Como el dato no homogéneo vive en "
            "el tiempo (la temperatura del extremo), y la condición "
            "inicial es nula en $x$, la **transformada de Laplace en "
            "$t$** es la herramienta natural: incorpora la CI "
            "automáticamente ($\\mathcal{L}[u_t] = sU - u(x,0)$) y "
            "convierte la EDP en una EDO lineal de segundo orden en "
            "$x$, que se invierte usando el par $\\mathcal{L}^{-1}[s^{-1} "
            "e^{-a\\sqrt{s}}] = \\operatorname{erfc}(a/(2\\sqrt{t}))$."
        ),
        alternatives_md=(
            "**Otras vías equivalentes.**\n\n"
            "- **Método de imágenes:** extender la barra a la recta entera "
            "con un dato impar — funciona si el dato fuera homogéneo en "
            "$x = 0$, pero con $u(0, t) = h \\ne 0$ habría que restar la "
            "constante primero. Menos directo.\n"
            "- **Variable de similaridad** $\\eta = x/(2\\alpha\\sqrt{t})$: "
            "transforma la EDP directamente en una EDO en $\\eta$. Es la "
            "ruta más rápida si reconoces de antemano la autosimilaridad, "
            "y produce **la misma fórmula**. Pedagógicamente Laplace "
            "tiene la ventaja de no requerir esa intuición previa."
        ),
    )


def _choice_fourier_heat_line(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="fourier_heat_line",
        rationale_md=(
            "El dominio espacial es la **recta entera** $\\mathbb{R}$, "
            "sin condiciones de contorno. Sin BCs no hay un problema de "
            "Sturm-Liouville que produzca autovalores discretos, así que "
            "**separación de variables clásica no aplica**. La herramienta "
            "natural es la **transformada de Fourier en $x$**, que "
            "diagonaliza $\\partial_x$ y reduce la EDP a una EDO desacoplada "
            "para cada modo $k$. La inversión devuelve la solución como "
            "convolución del dato inicial con el **núcleo de Gauss**."
        ),
        alternatives_md=(
            "*Funciones de Green* daría exactamente la misma fórmula "
            "(el núcleo $G$ es la función de Green del calor en la línea, "
            "con condición inicial $G(x, 0) = \\delta(x)$). *Transformada "
            "de Laplace en $t$* es otra ruta clásica, especialmente útil "
            "si hay fuentes dependientes del tiempo. *Separación de "
            "variables* no aplica directamente (dominio no acotado)."
        ),
    )


def _choice_dalembert(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="dalembert_wave_1d",
        rationale_md=(
            "El dominio espacial es la **recta entera** $\\mathbb{R}$, "
            "así que no hay condiciones de contorno: el problema es de "
            "Cauchy puro. En este caso la **fórmula de D'Alembert** "
            "resuelve el problema en forma cerrada explotando la "
            "factorización del operador de onda y un cambio a "
            "**coordenadas características** $\\xi = x - ct$, $\\eta = x + ct$."
        ),
        alternatives_md=(
            "*Transformada de Fourier en $x$* daría la misma fórmula tras "
            "invertir la transformada. *Separación de variables* no "
            "aplica directamente en dominio infinito (no hay BCs que "
            "generen un problema de Sturm-Liouville)."
        ),
    )


def _choice_laplace_rect(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="sov_laplace_rect",
        rationale_md=(
            "El dominio es **rectangular** y las condiciones son de "
            "Dirichlet, con **tres lados homogéneos**. Separación de "
            "variables en $x$ produce un Sturm-Liouville estándar; "
            "la dirección $y$ hereda autovalores y se ajusta a la "
            "frontera no homogénea."
        ),
        alternatives_md=(
            "Otras opciones: **función de Green** (núcleo de Poisson en "
            "el rectángulo), **transformada conforme** (mapea el "
            "rectángulo al semiplano), o **diferencias finitas** "
            "(numérico). Para un primer encuentro pedagógico, "
            "separación es la opción canónica."
        ),
    )


def _choice_laplace_disk(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="sov_laplace_disk",
        rationale_md=(
            "El dominio es un **disco**, así que la separación natural "
            "es en **coordenadas polares**. La dirección angular hereda "
            "una condición de **periodicidad** (no de Dirichlet); la "
            "dirección radial se reduce a una EDO de Euler."
        ),
        alternatives_md=(
            "**Otras vías:** transformada conforme (mapea el disco al "
            "semiplano superior, simplifica algunos cálculos), o usar "
            "directamente la **fórmula integral de Poisson** "
            "(equivalente a sumar la serie). La separación es la ruta "
            "pedagógica clásica."
        ),
    )


def _choice_greens_1d(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="greens_function_1d",
        rationale_md=(
            "La EDP tiene **término fuente** $f$ no nulo, así que SOV "
            "homogénea no aplica directamente. El método de la **función "
            "de Green** resuelve el problema construyendo el núcleo "
            "$G(x, \\xi)$ y luego integrando contra $f$. Es la "
            "estrategia más limpia para Poisson 1D."
        ),
        alternatives_md=(
            "**Eigenfunction expansion** (proyectar $f$ sobre los modos "
            "y dividir por los autovalores) da exactamente el mismo "
            "resultado en forma de serie. La función de Green tiene "
            "la ventaja pedagógica de mostrar la **forma puntual** de "
            "la respuesta del operador."
        ),
    )


def _choice_helmholtz_rect(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="helmholtz_rect",
        rationale_md=(
            "El Laplaciano con Dirichlet 0 sobre un rectángulo tiene "
            "una **base ortogonal explícita** de autofunciones. "
            "Expandir tanto $u$ como $f$ en esa base convierte la EDP "
            "en una identidad término-a-término entre coeficientes, "
            "que se invierte trivialmente."
        ),
        alternatives_md=(
            "**Función de Green** del operador $\\Delta + k^2$ daría "
            "la misma respuesta como una integral. La expansión modal "
            "tiene la virtud de hacer explícita la estructura de "
            "**resonancias** que es esencial para entender el problema."
        ),
    )


def _choice_telegraph(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="telegraph_sov",
        rationale_md=(
            "La EDP es **lineal y homogénea**, el dominio espacial es "
            "un intervalo finito con BCs homogéneas: separación de "
            "variables aplica. La novedad respecto a wave/heat es la "
            "**EDO temporal de segundo orden con disipación**, cuyo "
            "análisis introduce los tres regímenes de un oscilador "
            "amortiguado."
        ),
        alternatives_md=(
            "**Transformada de Fourier en $x$** (no aplica en dominio "
            "acotado), o **transformada de Laplace en $t$** (viable, "
            "pero la inversión devuelve la misma serie con menos "
            "intuición pedagógica)."
        ),
    )


def _choice_schrodinger_well(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="schrodinger_well",
        rationale_md=(
            "La EDP es lineal con BCs homogéneas en un intervalo "
            "finito (las paredes infinitas del pozo). **Separación de "
            "variables** produce el problema espacial de Sturm-Liouville "
            "estándar y una EDO temporal de primer orden con coeficiente "
            "imaginario, que da rotación de fase $e^{-i E t / \\hbar}$. "
            "Los autovalores son los **niveles de energía cuantizados**."
        ),
        alternatives_md=(
            "Para potenciales más generales $V(x)$ usaríamos "
            "**perturbación**, **WKB**, o métodos numéricos. Aquí "
            "$V = 0$ dentro de la caja, así que la solución es elemental."
        ),
    )


def _choice_schrodinger_free(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="schrodinger_free",
        rationale_md=(
            "Schrödinger sin potencial ($V \\equiv 0$) en la **recta "
            "entera**. Como no hay BCs, no hay autovalores discretos: "
            "el espectro del Hamiltoniano libre es **continuo**. La "
            "**transformada de Fourier** diagonaliza $\\partial_x^2$ y "
            "convierte la EDP en una EDO modal con coeficiente "
            "imaginario, $\\partial_t \\hat\\psi = -i\\omega(k)\\hat\\psi$ "
            "con relación de dispersión $\\omega(k) = \\hbar k^2/(2m)$. "
            "La inversa devuelve $\\psi$ como convolución con el "
            "**propagador libre** de Feynman."
        ),
        alternatives_md=(
            "**Métodos descartados:** *Separación de variables* — no "
            "aplica (dominio no acotado, sin BCs que cuanticen). "
            "*Operadores de escalera* — son específicos del oscilador "
            "armónico. *Funciones de Green* — daría exactamente el "
            "mismo propagador, ya que $K$ es la función de Green del "
            "operador $i\\hbar\\partial_t + \\tfrac{\\hbar^2}{2m}\\partial_x^2$ "
            "con condición inicial $K(x, 0) = \\delta(x)$. **Integral "
            "de camino de Feynman** — recupera $K$ como suma sobre "
            "trayectorias clásicas con peso $e^{iS/\\hbar}$; ruta "
            "pedagógica más profunda pero menos elemental."
        ),
    )


def _choice_schrodinger_oscillator(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="schrodinger_oscillator",
        rationale_md=(
            "EDP de Schrödinger en la recta con potencial cuadrático "
            "$V(x) = \\tfrac{1}{2} m \\omega^2 x^2$. Separación de "
            "variables nos lleva a la **ecuación de Hermite-Weber**, "
            "cuya cuantización por terminación de serie produce los "
            "niveles equiespaciados $E_n = \\hbar\\omega(n + 1/2)$ y "
            "las autofunciones gaussianas multiplicadas por **polinomios "
            "de Hermite**."
        ),
        alternatives_md=(
            "**Operadores de escalera** ($\\hat a, \\hat a^\\dagger$) son "
            "la otra forma estándar de obtener el espectro y las "
            "autofunciones, sin pasar por la EDO. **Funciones de Green** "
            "(propagador del oscilador, fórmula de Mehler) dan la "
            "solución como integral en $\\psi_0$. Aquí elegimos la "
            "ruta vía Hermite porque es la más pedagógica para un "
            "primer encuentro."
        ),
    )


def _choice_characteristics(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="characteristics_transport_1d",
        rationale_md=(
            "La EDP es de **primer orden hiperbólica**. El método de "
            "las **características** es el camino canónico: parametrizar "
            "las curvas $dx/dt = c$ a lo largo de las cuales la solución "
            "se transporta sin cambios."
        ),
        alternatives_md=(
            "**Transformada de Fourier** también funciona (la solución "
            "es $\\hat u(k, t) = e^{-ick t}\\hat u_0(k)$), pero "
            "geométricamente las características son más intuitivas y "
            "se generalizan a EDPs no lineales (donde Fourier no aplica)."
        ),
    )


def _choice_biharmonic_beam(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="biharmonic_beam",
        rationale_md=(
            "Para una viga simplemente apoyada, las **cuatro condiciones "
            "de contorno** se satisfacen automáticamente por la base "
            "$\\sin(n\\pi x/L)$. Expandimos $u$ y $q$ en serie de senos "
            "y leemos los coeficientes término a término."
        ),
        alternatives_md=(
            "Para condiciones distintas (empotrado, libre) la base "
            "$\\sin$ deja de servir y hay que usar **autofunciones de "
            "Sturm-Liouville de cuarto orden** (funciones de Krylov). "
            "Para una sola carga concentrada, **función de Green** es "
            "más directa que la serie."
        ),
    )


def _choice_wave_disk(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="sov_wave_disk",
        rationale_md=(
            "La geometría es **circular** y la EDP es de onda con "
            "condición de Dirichlet en el borde. Separación de "
            "variables en polares produce la **ecuación de Bessel** "
            "en la coordenada radial y autovalores $\\lambda_n = "
            "(\\mu_n/R)^2$, donde $\\mu_n$ es el $n$-ésimo cero "
            "positivo de $J_0$. Es la generalización natural de la "
            "cuerda vibrante 1D a 2D con geometría circular."
        ),
        alternatives_md=(
            "La **transformada de Hankel** (análoga radial de Fourier) "
            "es la herramienta cuando el dominio es no acotado "
            "($r \\in [0, \\infty)$). Aquí, dominio acotado: SOV "
            "Bessel-Fourier es la opción canónica."
        ),
    )


def _choice_heat_disk(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="sov_heat_disk",
        rationale_md=(
            "Igual que el caso de la onda en disco, pero con un "
            "operador temporal de **primer orden**. Cada modo Bessel "
            "decae exponencialmente como $e^{-\\alpha^2 (\\mu_n/R)^2 t}$, "
            "con el modo fundamental $J_0(\\mu_1 r/R)$ dominando a "
            "tiempos largos."
        ),
        alternatives_md=(
            "**Función de Green** del calor en disco también funciona, "
            "pero la fórmula explícita ya involucra series de Bessel — "
            "no se gana simplicidad."
        ),
    )


def _choice_laplace_ball(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="sov_laplace_ball",
        rationale_md=(
            "Geometría **esférica** y EDP de Laplace. Separación de "
            "variables en esféricas con simetría axial produce **EDOs "
            "de Legendre y Euler**. Los autovalores son enteros "
            "$\\ell = 0, 1, 2, \\dots$ forzados por la regularidad en "
            "los polos, y las autofunciones angulares son los "
            "**polinomios de Legendre** $P_\\ell(\\cos\\theta)$."
        ),
        alternatives_md=(
            "**Función de Green del Laplaciano en bola** (fórmula de "
            "Poisson esférica) daría la misma solución como una "
            "integral. La serie multipolar es más útil para entender "
            "el **comportamiento por orden** del campo (monopolo, "
            "dipolo, cuadrupolo, …)."
        ),
    )


def _choice_images_halfplane(_p: PDEProblem | None = None) -> MethodChoice:
    return MethodChoice(
        method_slug="images_halfplane",
        rationale_md=(
            "El **semiplano** tiene simetría especular respecto al "
            "muro $y = 0$. El método de **imágenes** explota esa "
            "simetría: reflejando la fuente con signo opuesto, la "
            "función de Green del plano entero produce automáticamente "
            "$G = 0$ en el muro."
        ),
        alternatives_md=(
            "**Transformada de Fourier en $x$** da la misma fórmula "
            "de Poisson tras invertir; **transformada conforme** "
            "(p. ej. $z \\mapsto i(1 + z)/(1 - z)$) mapea el semiplano "
            "al disco unidad y reduce el problema al de Laplace en disco."
        ),
    )


# ---------------------------------------------------------------------------
# Registry — order matters: most specific first
# ---------------------------------------------------------------------------

_REGISTRY: list[tuple[Callable[[PDEProblem], bool], Callable[[PDEProblem | None], MethodChoice]]] = [
    # Most specific first.
    # Schrödinger: three cases on disjoint signatures.
    #   - free: unbounded x, no ω²x² potential.
    #   - oscillator: ω²x² potential present (either bounded or unbounded x).
    #   - well: bounded interval with Dirichlet 0 BCs.
    # `free` is registered first because its predicate explicitly
    # excludes the oscillator signature, so it never poaches.
    (_looks_like_schrodinger_free, _choice_schrodinger_free),
    (_looks_like_schrodinger_oscillator, _choice_schrodinger_oscillator),
    (_looks_like_schrodinger_well, _choice_schrodinger_well),
    (_looks_like_biharmonic_beam, _choice_biharmonic_beam),
    (_looks_like_characteristics_transport, _choice_characteristics),
    (_looks_like_poisson_1d, _choice_greens_1d),
    (_looks_like_telegraph, _choice_telegraph),
    # Geometry-specific (must precede the more general Heat/Wave 1D predicates).
    (_looks_like_wave_disk, _choice_wave_disk),
    (_looks_like_heat_disk, _choice_heat_disk),
    (_looks_like_laplace_ball, _choice_laplace_ball),
    (_looks_like_heat_halfline, _choice_laplace_heat_halfline),
    (_looks_like_heat_1d_unbounded, _choice_fourier_heat_line),
    (_looks_like_heat_1d, _choice_heat_1d_sov),
    (_looks_like_wave_1d_unbounded, _choice_dalembert),
    (_looks_like_wave_1d_bounded, _choice_wave_1d_sov),
    (_looks_like_images_halfplane, _choice_images_halfplane),
    (_looks_like_laplace_disk, _choice_laplace_disk),
    (_looks_like_laplace_rect, _choice_laplace_rect),
    (_looks_like_helmholtz_rect, _choice_helmholtz_rect),
    # Last-resort fallback: any 2nd-order PDE classifier + canonical form.
    # MUST be last in the registry so specific methods always win.
    (_looks_like_second_order_general, _choice_general_second_order),
]


def pick_method(problem: PDEProblem) -> MethodChoice:
    """Return the first matching method, or raise if none applies."""
    for predicate, builder in _REGISTRY:
        if predicate(problem):
            return builder(problem)
    raise NotImplementedError(
        "Ningún método del repertorio actual cubre este problema. "
        "El catch-all de 2°-orden general debería haber capturado "
        "cualquier EDP lineal de segundo orden. Revisa el LaTeX: "
        "puede que no contenga un marcador de segunda derivada "
        "reconocible (u_{xx}, u_{yy}, u_{tt}, u_{xy}, ...). "
        "Repertorio específico: calor 1D (SOV acotado, Fourier en la "
        "línea, Laplace en el semieje) y en disco, onda 1D (SOV y "
        "D'Alembert) y en disco (tambor), Laplace en rectángulo, "
        "disco, bola y semiplano, Poisson 1D (Green), Helmholtz en "
        "rectángulo, telégrafo, Schrödinger libre, en pozo infinito y "
        "oscilador armónico, transporte 1D por características, "
        "biarmónica/viga 1D."
    )


# ---------------------------------------------------------------------------
# Backward-compat alias used by `methods/separation_of_variables.py`.
# Older code imports `_heat_1d_sov` to fetch the choice text without
# instantiating a problem; keep the alias.
# ---------------------------------------------------------------------------

_heat_1d_sov = _choice_heat_1d_sov
