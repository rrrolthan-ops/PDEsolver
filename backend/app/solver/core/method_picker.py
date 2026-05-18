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
        return _has_1d_interval_domain(p) and _all_dirichlet_zero(p)
    latex = p.equation_latex.replace(" ", "").lower()
    heat_shapes = ("u_t=alpha^2*u_{xx}", "u_t=alpha^2u_{xx}", "u_t=a^2u_{xx}")
    return (
        any(s in latex for s in heat_shapes)
        and _has_1d_interval_domain(p)
        and _all_dirichlet_zero(p)
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
    if p.equation_kind == "laplace":
        return p.domain.x is not None and p.domain.y is not None and p.domain.t is None
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
    )


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


# ---------------------------------------------------------------------------
# Registry — order matters: most specific first
# ---------------------------------------------------------------------------

_REGISTRY: list[tuple[Callable[[PDEProblem], bool], Callable[[PDEProblem | None], MethodChoice]]] = [
    (_looks_like_heat_1d, _choice_heat_1d_sov),
    (_looks_like_wave_1d_unbounded, _choice_dalembert),
    (_looks_like_wave_1d_bounded, _choice_wave_1d_sov),
    (_looks_like_laplace_rect, _choice_laplace_rect),
]


def pick_method(problem: PDEProblem) -> MethodChoice:
    """Return the first matching method, or raise if none applies."""
    for predicate, builder in _REGISTRY:
        if predicate(problem):
            return builder(problem)
    raise NotImplementedError(
        "Ningún método del repertorio actual cubre este problema. "
        "Repertorio implementado (Fase 1 + Fase 2-A): calor 1D, onda 1D "
        "(separación y D'Alembert), Laplace en rectángulo. "
        "Más métodos llegan en Fase 2-B (Poisson/Green, disco, Helmholtz)."
    )


# ---------------------------------------------------------------------------
# Backward-compat alias used by `methods/separation_of_variables.py`.
# Older code imports `_heat_1d_sov` to fetch the choice text without
# instantiating a problem; keep the alias.
# ---------------------------------------------------------------------------

_heat_1d_sov = _choice_heat_1d_sov
