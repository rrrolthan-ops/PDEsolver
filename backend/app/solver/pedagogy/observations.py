"""Curated didactic observations.

These are the "Observación didáctica" boxes that appear in the margin
of certain steps. Each one is calibrated to a specific algebraic
situation in which students typically stumble. They're indexed by a
slug so methods can attach them by reference.
"""

from __future__ import annotations

from app.schemas.solution import DidacticObservation


_REGISTRY: dict[str, DidacticObservation] = {
    "sov_why_separable": DidacticObservation(
        kind="intuition",
        text_md=(
            "**¿Por qué tiene sentido suponer una solución producto?** "
            "Porque la EDP es lineal: si $u_1$ y $u_2$ son soluciones, "
            "$a u_1 + b u_2$ también lo es. Si encontramos *muchas* "
            "soluciones-producto, sus combinaciones generan un espacio "
            "vectorial enorme. El teorema de Sturm-Liouville garantiza "
            "que ese espacio es lo bastante grande para representar "
            "cualquier condición inicial razonable."
        ),
    ),
    "sov_sign_convention": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**Atención al signo de la constante de separación.** "
            "Algunos libros usan $+\\lambda$, otros $-\\lambda$. El "
            "*resultado* es el mismo, pero los signos intermedios "
            "cambian. Aquí elegimos $-\\lambda$ para que los "
            "autovalores físicamente relevantes salgan positivos: "
            "$\\lambda_n = (n\\pi/L)^2 > 0$."
        ),
    ),
    "sov_why_three_cases": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**No saltes esto.** Antes de saber qué signo tiene "
            "$\\lambda$, hay que examinar los tres casos posibles. "
            "Sólo después de descartar $\\lambda \\le 0$ podemos "
            "afirmar que los autovalores son positivos. Saltarse este "
            "análisis es la causa #1 de soluciones perdidas en "
            "exámenes."
        ),
    ),
    "sturm_liouville_theorem": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Teorema (Sturm-Liouville regular).** Para el problema "
            "$-X'' = \\lambda X$, $X(0) = X(L) = 0$, existen "
            "infinitos autovalores reales "
            "$0 < \\lambda_1 < \\lambda_2 < \\cdots \\to \\infty$ con "
            "autofunciones $X_n(x) = \\sin(n\\pi x/L)$ que forman una "
            "base ortogonal de $L^2([0, L])$. En particular, *toda* "
            "función $f \\in L^2([0, L])$ admite un desarrollo "
            "convergente en serie de senos."
        ),
    ),
    "fourier_orthogonality": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Ortogonalidad de los senos.** "
            "$\\int_0^L \\sin(n\\pi x/L)\\sin(m\\pi x/L)\\, dx = (L/2)\\,\\delta_{nm}$. "
            "Esta identidad es lo único que necesitamos para extraer "
            "$B_n$. Se demuestra con la identidad producto-a-suma "
            "$2\\sin a \\sin b = \\cos(a-b) - \\cos(a+b)$ e integrando."
        ),
    ),
    "modes_decay_rate": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Las altas frecuencias mueren primero.** "
            "El modo $n$ decae como "
            "$e^{-\\alpha^2 (n\\pi/L)^2 t}$. La constante de tiempo "
            "$\\tau_n \\propto 1/n^2$ disminuye rápidamente con $n$. "
            "Por eso un perfil inicial \"con picos\" se redondea casi "
            "instantáneamente, mientras la forma general tarda mucho "
            "más en desaparecer."
        ),
    ),
}


def get(slug: str) -> DidacticObservation:
    """Retrieve an observation by slug."""
    return _REGISTRY[slug]


def maybe(slugs: list[str]) -> list[DidacticObservation]:
    """Convenience: build a list of observations from a list of slugs."""
    return [_REGISTRY[s] for s in slugs if s in _REGISTRY]
