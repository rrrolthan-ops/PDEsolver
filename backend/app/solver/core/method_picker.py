"""Pick a solution method given a `PDEProblem`.

For Phase 1 the picker only knows about heat-equation-shaped problems
on a bounded interval with homogeneous Dirichlet conditions, which it
sends to `SeparationOfVariablesHeat1D`. As more methods land, register
them here with explicit eligibility predicates rather than letting the
picker grow into a soup of `if`s.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.schemas import PDEProblem


@dataclass
class MethodChoice:
    method_slug: str
    rationale_md: str
    alternatives_md: str  # methods considered and discarded


def _looks_like_heat_1d(p: PDEProblem) -> bool:
    """True if the problem matches the canonical heat-on-an-interval setup.

    We accept either `equation_kind == "heat"` (set by the user / upstream
    parser) or the literal form ``u_t = alpha^2 u_{xx}`` in the LaTeX.
    """
    if p.equation_kind == "heat":
        return _has_1d_interval_domain(p) and _all_dirichlet_zero(p)
    latex = p.equation_latex.replace(" ", "").lower()
    heat_shapes = ("u_t=alpha^2*u_{xx}", "u_t=alpha^2u_{xx}", "u_t=a^2u_{xx}")
    if any(shape in latex for shape in heat_shapes):
        return _has_1d_interval_domain(p) and _all_dirichlet_zero(p)
    return False


def _has_1d_interval_domain(p: PDEProblem) -> bool:
    return p.domain.x is not None and p.domain.y is None and p.domain.z is None


def _all_dirichlet_zero(p: PDEProblem) -> bool:
    if not p.boundary_conditions:
        return False
    return all(
        bc.type == "dirichlet" and bc.value.strip() == "0" for bc in p.boundary_conditions
    )


# Registry of (predicate, slug, rationale-builder).
_REGISTRY: list[tuple[Callable[[PDEProblem], bool], str, Callable[[PDEProblem], MethodChoice]]] = []


def register(predicate: Callable[[PDEProblem], bool], slug: str):
    """Decorator to register a method-choice builder."""

    def deco(fn: Callable[[PDEProblem], MethodChoice]):
        _REGISTRY.append((predicate, slug, fn))
        return fn

    return deco


@register(_looks_like_heat_1d, "separation_of_variables")
def _heat_1d_sov(p: PDEProblem) -> MethodChoice:
    return MethodChoice(
        method_slug="separation_of_variables",
        rationale_md=(
            "Elegimos **separación de variables** porque concurren tres "
            "condiciones que la hacen no sólo aplicable, sino la opción "
            "natural:\n\n"
            "1. La EDP es **lineal y homogénea** (no aparece término "
            "independiente). Si encontramos soluciones particulares en "
            "forma de producto, su superposición sigue siendo solución.\n"
            "2. El dominio espacial es un **intervalo finito** "
            "$[0, L]$, geométricamente simple, sin acoplar coordenadas.\n"
            "3. Las **condiciones de contorno son homogéneas** "
            "($u(0, t) = u(L, t) = 0$). Esto es lo que permite que el "
            "factor espacial $X(x)$ herede directamente las condiciones "
            "y dé lugar a un problema de Sturm-Liouville con "
            "autovalores discretos."
        ),
        alternatives_md=(
            "**Métodos descartados y por qué:**\n\n"
            "- *D'Alembert*: aplica a la ecuación de onda, no al calor.\n"
            "- *Transformada de Fourier*: requiere dominio espacial "
            "infinito ($x \\in \\mathbb{R}$). En nuestro intervalo "
            "$[0, L]$ usaríamos la transformada finita, que es "
            "equivalente a la serie que vamos a obtener.\n"
            "- *Transformada de Laplace en $t$*: es viable, pero la "
            "inversión nos llevaría a la misma serie. Es preferible "
            "separar variables, que muestra explícitamente los modos "
            "normales y su interpretación física.\n"
            "- *Funciones de Green*: útiles cuando la EDP es no "
            "homogénea ($u_t - \\alpha^2 u_{xx} = f(x, t)$). Aquí $f = 0$, "
            "así que no aporta."
        ),
    )


def pick_method(problem: PDEProblem) -> MethodChoice:
    """Return the first matching method, or raise if none applies."""
    for predicate, _slug, builder in _REGISTRY:
        if predicate(problem):
            return builder(problem)
    raise NotImplementedError(
        "Ningún método del repertorio actual cubre este problema. "
        "Fase 1 sólo implementa la ecuación del calor 1D con condiciones "
        "de Dirichlet homogéneas en un intervalo finito."
    )
