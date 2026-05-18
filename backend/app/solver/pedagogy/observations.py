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
    # ---- Wave equation -----------------------------------------------------
    "wave_needs_two_ics": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**El problema de Cauchy de orden 2 necesita 2 condiciones "
            "iniciales.** La ecuación de onda es $u_{tt} = c^2 u_{xx}$: el "
            "operador temporal es de segundo orden, así que debemos "
            "especificar $u(x, 0)$ **y** $u_t(x, 0)$, igual que en "
            "mecánica clásica fijamos posición y velocidad inicial."
        ),
    ),
    "wave_harmonic_frequencies": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Por qué una cuerda suena bien afinada.** Los modos "
            "normales tienen frecuencias $\\omega_n = c n\\pi/L$, que "
            "son múltiplos enteros de la frecuencia fundamental "
            "$\\omega_1 = c\\pi/L$. Esa **relación armónica entera** es "
            "precisamente lo que el oído percibe como una nota musical "
            "consistente. Una membrana 2D, en cambio, tiene frecuencias "
            "asociadas a ceros de Bessel: irracionales entre sí, y por "
            "eso un tambor suena \"a percusión\", no a nota."
        ),
    ),
    "wave_no_dissipation": DidacticObservation(
        kind="intuition",
        text_md=(
            "**La onda no disipa energía.** A diferencia del calor "
            "(decaimiento exponencial), aquí la dependencia temporal "
            "es trigonométrica: cada modo oscila con amplitud constante. "
            "Esto es consecuencia de la simetría $t \\leftrightarrow -t$ "
            "de la EDP. Físicamente: en este modelo idealizado no hay "
            "fricción ni viscosidad."
        ),
    ),
    # ---- D'Alembert --------------------------------------------------------
    "dalembert_factorization": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Factorización del d'Alembertiano.** "
            "$\\partial_t^2 - c^2 \\partial_x^2 = "
            "(\\partial_t - c\\partial_x)(\\partial_t + c\\partial_x)$. "
            "Esta factorización es lo que motiva el cambio de variables "
            "característico: cada factor anula a las soluciones del "
            "tipo \"onda viajera\" en una dirección."
        ),
    ),
    "dalembert_domain_of_dependence": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Dominio de dependencia.** El valor de $u(x_0, t_0)$ "
            "depende sólo de los datos iniciales en el intervalo "
            "$[x_0 - c t_0,\\ x_0 + c t_0]$. Esto es el concepto físico "
            "de **causalidad relativista**: ninguna información viaja "
            "más rápido que $c$. Contrasta con el calor, donde "
            "$u(x_0, t_0)$ depende formalmente de **todos** los $x$ "
            "(velocidad infinita de propagación — una de las "
            "limitaciones físicas del modelo de difusión)."
        ),
    ),
    # ---- Laplace -----------------------------------------------------------
    "laplace_sign_swap": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**Al separar $\\Delta u = 0$, una dirección sale "
            "oscilatoria y la otra hiperbólica.** Es inevitable: la "
            "suma de las dos derivadas segundas debe dar cero, así que "
            "los signos de $X''/X$ y $Y''/Y$ deben ser opuestos. La "
            "elección habitual es ponerlos para que la dirección con "
            "condiciones de contorno homogéneas en ambos extremos sea "
            "la oscilatoria — eso garantiza un problema de "
            "Sturm-Liouville con autovalores discretos."
        ),
    ),
    "laplace_max_principle": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Principio del máximo (Laplace).** Si $u$ es armónica en "
            "un dominio acotado $\\Omega$ y continua en su clausura, "
            "entonces $u$ alcanza su máximo y su mínimo en la frontera "
            "$\\partial\\Omega$. En particular, las soluciones del "
            "problema de Dirichlet son **únicas** (dos soluciones "
            "diferirían en una armónica nula en la frontera, que por "
            "el principio del máximo debe ser idénticamente cero)."
        ),
    ),
}


def get(slug: str) -> DidacticObservation:
    """Retrieve an observation by slug."""
    return _REGISTRY[slug]


def maybe(slugs: list[str]) -> list[DidacticObservation]:
    """Convenience: build a list of observations from a list of slugs."""
    return [_REGISTRY[s] for s in slugs if s in _REGISTRY]
