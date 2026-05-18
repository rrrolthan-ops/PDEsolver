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
    # ---- Laplace on disk --------------------------------------------------
    "disk_periodicity": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**La 2π-periodicidad es lo que cuantiza los modos.** En el "
            "rectángulo, las condiciones $X(0) = X(a) = 0$ daban "
            "$\\lambda_n = (n\\pi/a)^2$. En el disco la \"condición de "
            "contorno\" angular es **periodicidad**: $\\Phi$ debe valer "
            "lo mismo en $\\theta$ y en $\\theta + 2\\pi$. Esto fuerza "
            "$\\sqrt{\\lambda} \\in \\mathbb{Z}$, dando $\\lambda = n^2$ "
            "para $n = 0, 1, 2, \\ldots$. El **modo $n = 0$ existe** "
            "(es el término constante) — no descartar."
        ),
    ),
    "disk_origin_regularity": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**Regularidad en el origen.** Las EDO radiales tipo Euler "
            "tienen dos soluciones: $r^n$ y $r^{-n}$ (o $1$ y $\\ln r$ "
            "para $n = 0$). En un disco **sólido** descartamos las "
            "soluciones que divergen en $r = 0$. Si en cambio "
            "trabajamos en un **anillo** $r_1 < r < r_2$, mantenemos "
            "ambas y fijamos las constantes con dos condiciones de "
            "frontera (una en cada circunferencia)."
        ),
    ),
    "disk_mean_value": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Teorema del valor medio (Gauss).** Si $u$ es armónica "
            "en un disco de radio $R$ alrededor de $x_0$, entonces "
            "$u(x_0) = \\frac{1}{2\\pi R} \\oint_{|x - x_0| = R} u\\, ds$. "
            "Es decir, **el valor en el centro es el promedio sobre el "
            "círculo de cualquier radio**. Nuestro $a_0/2$ es exactamente "
            "ese promedio."
        ),
    ),
    # ---- Green's function -------------------------------------------------
    "green_reciprocity": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Principio de reciprocidad.** Para operadores autoadjuntos "
            "(como $-d^2/dx^2$ con Dirichlet 0), la función de Green es "
            "**simétrica**: $G(x, \\xi) = G(\\xi, x)$. Físicamente: la "
            "respuesta en $x$ a una fuente en $\\xi$ es igual a la "
            "respuesta en $\\xi$ a una fuente en $x$. En electricidad "
            "se conoce como el **teorema de reciprocidad de Lorentz**."
        ),
    ),
    "green_delta_intuition": DidacticObservation(
        kind="intuition",
        text_md=(
            "**$\\delta(x - \\xi)$ no es una función ordinaria**, es una "
            "**distribución**: vale cero salvo en $\\xi$ pero su "
            "\"integral\" es 1. Para construir $G$, lo único que "
            "necesitamos del delta es que **integrar la EDO en una "
            "vecindad de $\\xi$ produce un salto unitario en la "
            "derivada de $G$**. Eso es propiedad 4."
        ),
    ),
    # ---- Helmholtz --------------------------------------------------------
    "helmholtz_resonance": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**Resonancia destruye la fórmula directa.** "
            "$c_{mn} = f_{mn}/(k^2 - k_{mn}^2)$ explota cuando $k^2 = "
            "k_{mn}^2$. Antes de aplicar la fórmula, verifica que $k$ "
            "**no** sea ninguno de los autovalores del rectángulo. "
            "Si lo es, el problema sólo tiene solución si "
            "$f$ es ortogonal a todas las autofunciones "
            "correspondientes a ese autovalor (alternativa de Fredholm)."
        ),
    ),
    "helmholtz_double_basis": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Producto de dos bases SL.** Como $X_m(x) = \\sin(m\\pi x/a)$ "
            "es base ortogonal de $L^2([0, a])$ y $Y_n(y) = \\sin(n\\pi y/b)$ "
            "lo es de $L^2([0, b])$, sus **productos** "
            "$\\phi_{mn} = X_m \\cdot Y_n$ forman base ortogonal de "
            "$L^2([0, a] \\times [0, b])$. Toda función con la "
            "regularidad apropiada se desarrolla en serie doble."
        ),
    ),
    # ---- Telegraph --------------------------------------------------------
    "telegraph_three_regimes": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Los tres regímenes son los de un oscilador amortiguado.** "
            "Sobreamortiguado: la fricción es tan grande que el modo no "
            "alcanza a oscilar. Crítico: la transición entre ambos "
            "comportamientos. Subamortiguado: la fricción atenúa pero "
            "no impide la oscilación. Es el mismo análisis que para un "
            "resorte con rozamiento, aplicado a cada modo espacial por "
            "separado."
        ),
    ),
    "telegraph_heaviside": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Condición de Heaviside.** Cuando $\\alpha^2 = \\beta$, la "
            "señal viaja sin distorsión (sólo se atenúa globalmente con "
            "el factor $e^{-\\alpha t}$). Fue el descubrimiento crucial "
            "que permitió mejorar los cables submarinos del siglo XIX: "
            "balancear la inductancia con la capacitancia para acercarse "
            "a la condición."
        ),
    ),
    # ---- Schrödinger ------------------------------------------------------
    "schrodinger_complex": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**$\\psi$ es compleja.** A diferencia de heat/wave, donde "
            "$u$ era real, aquí la función de onda toma valores en "
            "$\\mathbb{C}$. Las exponenciales temporales $e^{-iEt/\\hbar}$ "
            "son **rotaciones de fase**, no decaimiento. Lo que se "
            "observa físicamente es $|\\psi|^2$."
        ),
    ),
    "schrodinger_quantization": DidacticObservation(
        kind="intuition",
        text_md=(
            "**La cuantización viene de las BCs.** Lo que cuantiza la "
            "energía no es la EDP misma — es la combinación EDP + "
            "condiciones de contorno. La misma matemática que da los "
            "**modos de una cuerda fija** da los **niveles de energía** "
            "del electrón en una caja."
        ),
    ),
    "schrodinger_ground_state": DidacticObservation(
        kind="intuition",
        text_md=(
            "**No hay reposo cuántico.** $E_1 > 0$: la partícula no "
            "puede estar quieta en el fondo del pozo. Confinar la "
            "posición ($\\Delta x \\sim L$) obliga a tener cierta "
            "extensión en momento ($\\Delta p \\gtrsim \\hbar/L$), que "
            "se traduce en energía cinética mínima."
        ),
    ),
    # ---- Characteristics --------------------------------------------------
    "characteristics_first_order": DidacticObservation(
        kind="theorem",
        text_md=(
            "**EDPs de primer orden necesitan UNA condición.** Una EDP "
            "$F(x, t, u, u_x, u_t) = 0$ tiene una sola \"dirección "
            "característica\" en cada punto. Basta especificar el dato "
            "a lo largo de una curva transversal a las características."
        ),
    ),
    "characteristics_shock_warning": DidacticObservation(
        kind="alternative",
        text_md=(
            "**Cuando $c$ depende de $u$, aparecen choques.** Para "
            "$u_t + u\\, u_x = 0$ (Burgers), las características pueden "
            "cruzarse en tiempo finito si $u_0$ es decreciente: la "
            "solución pierde diferenciabilidad. Hay que pasar a "
            "soluciones débiles (condición de Rankine-Hugoniot). Este "
            "caso lineal con $c$ constante es el escenario domesticado "
            "donde las características son rectas paralelas."
        ),
    ),
    # ---- Biharmonic -------------------------------------------------------
    "biharmonic_four_bcs": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**Cuatro BCs, no dos.** Un operador de cuarto orden "
            "requiere cuatro condiciones para tener solución única. "
            "Apoyo simple impone $u$ y $u''$ en cada extremo. Otras "
            "opciones: empotrado ($u = u' = 0$), libre ($u'' = u''' = 0$). "
            "La elección **debe ser compatible con la base** que uses."
        ),
    ),
    "biharmonic_n4_decay": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Decaimiento como $1/n^4$.** Los coeficientes de la "
            "deflexión decaen como la cuarta potencia inversa del "
            "índice del modo. Eso significa que la serie converge muy "
            "rápido y que las altas frecuencias de la carga se filtran "
            "fuertemente."
        ),
    ),
    # ---- Method of images -------------------------------------------------
    "images_mirror_trick": DidacticObservation(
        kind="intuition",
        text_md=(
            "**El truco de espejo.** Para anular una función armónica "
            "en una superficie plana, reflejamos la fuente a través de "
            "esa superficie y le cambiamos el signo. La superposición "
            "tiene **simetría especular** y por tanto vale cero en el "
            "plano de simetría — sin necesidad de calcular nada más."
        ),
    ),
    "images_general_geometry": DidacticObservation(
        kind="alternative",
        text_md=(
            "**Qué dominios admiten imágenes.** El método funciona "
            "limpiamente cuando la geometría es generada por "
            "**reflexiones e inversiones** elementales: semiplano "
            "(reflexión), cuña con ángulo $\\pi/n$ (varias reflexiones), "
            "rectángulo (rejilla infinita), disco (inversión). Para "
            "geometrías irregulares hay que recurrir a transformada "
            "conforme (2D) o métodos numéricos."
        ),
    ),
    # ---- Bessel / disk ---------------------------------------------------
    "bessel_weighted_orthogonality": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**Las autofunciones de Bessel son ortogonales con peso "
            "$r$, no con peso $1$.** Esto es estructural: el "
            "Laplaciano en polares se escribe como "
            "$\\Delta u = \\tfrac{1}{r}(r u_r)_r + \\dots$, y esa "
            "$r$ extra es exactamente el peso $r\\, dr$ de la integral "
            "de área. Si lo olvidas y proyectas con la integral plana, "
            "los coeficientes te salen mal."
        ),
    ),
    "bessel_inharmonic_drum": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Por qué un tambor no suena a nota.** Los ceros de $J_0$ "
            "están en proporciones irracionales no enteras "
            "($\\mu_2/\\mu_1 \\approx 2.295$, $\\mu_3/\\mu_1 \\approx 3.598$, …). "
            "Sus frecuencias asociadas $\\omega_n = c\\mu_n/R$ son "
            "**inarmónicas**: el oído no las percibe como una nota "
            "musical limpia, sino como un sonido de percusión."
        ),
    ),
    "bessel_regularity_at_origin": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**$Y_0$ se descarta por regularidad.** Las dos soluciones "
            "de Bessel de orden 0, $J_0$ y $Y_0$, son linealmente "
            "independientes. $Y_0(s)$ diverge como $\\tfrac{2}{\\pi}\\ln s$ "
            "cuando $s \\to 0^+$. En un disco **sólido** la solución debe "
            "ser finita en $r = 0$, así que $Y_0$ queda excluida. En un "
            "**anillo** (con un agujero central) mantendríamos las dos."
        ),
    ),
    # ---- Legendre / sphere -----------------------------------------------
    "legendre_pole_regularity": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Los autovalores $\\ell$ vienen forzados por la "
            "regularidad en los polos.** La EDO de Legendre tiene "
            "soluciones para cualquier valor de $\\ell$, pero sólo "
            "cuando $\\ell$ es un **entero no negativo** la solución "
            "es polinómica y por tanto **regular** en $\\xi = \\pm 1$ "
            "(los polos norte y sur). Esto explica por qué "
            "$\\ell = 0, 1, 2, \\dots$ y no algún continuo."
        ),
    ),
    "legendre_multipole_meaning": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Los términos $r^\\ell P_\\ell$ son los multipolos.** "
            "$\\ell = 0$ — monopolo (carga total promediada en la "
            "esfera). $\\ell = 1$ — dipolo (variación de orden $\\cos\\theta$). "
            "$\\ell = 2$ — cuadrupolo. Esta serie es la **expansión "
            "multipolar** que se usa en electrostática y gravitación "
            "para describir el campo lejano de una distribución de "
            "fuentes."
        ),
    ),
    "ball_mean_value_3d": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Teorema del valor medio en 3D.** Si $u$ es armónica en "
            "una bola alrededor de $\\mathbf{x}_0$, entonces "
            "$u(\\mathbf{x}_0) = \\tfrac{1}{4\\pi R^2} \\oint_{|x - x_0| = R} "
            "u\\, dS$. En nuestra expansión, esto se manifiesta como "
            "$u(0) = A_0$, el coeficiente del monopolo: el promedio "
            "esférico del dato $f$."
        ),
    ),
    # ---- Quantum harmonic oscillator -------------------------------------
    "oscillator_quantization_from_termination": DidacticObservation(
        kind="theorem",
        text_md=(
            "**De dónde sale la cuantización.** La EDO de Hermite "
            "$H'' - 2\\xi H' + (\\varepsilon - 1)H = 0$ tiene soluciones "
            "en serie de potencias para **cualquier** $\\varepsilon$. Lo "
            "que cuantiza el espectro es la condición de que la serie "
            "**termine** en un polinomio — sin terminación, $H$ crece "
            "como $e^{\\xi^2}$ y $\\varphi = H\\, e^{-\\xi^2/2}$ "
            "explota en lugar de decaer. La terminación pasa exactamente "
            "cuando $\\varepsilon = 2n + 1$ con $n$ entero no negativo. "
            "La normalizabilidad es lo que selecciona el espectro discreto."
        ),
    ),
    "oscillator_equispaced_spectrum": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Por qué el espectro es equiespaciado.** "
            "$E_{n+1} - E_n = \\hbar\\omega$, constante para todo $n$. "
            "Esta es **la** característica del oscilador armónico — "
            "ningún otro potencial tiene espectro perfectamente "
            "equiespaciado. Es lo que hace que los modos del campo "
            "electromagnético cuantizado se comporten como **partículas** "
            "(fotones), cada uno llevando una energía $\\hbar\\omega$: "
            "los \"escalones\" entre niveles son siempre iguales, así "
            "que sumar $N$ excitaciones es indistinguible de tener $N$ "
            "partículas idénticas."
        ),
    ),
    "oscillator_zero_point_energy": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Energía de punto cero.** "
            "$E_0 = \\tfrac{1}{2}\\hbar\\omega > 0$: el oscilador "
            "**no puede estar en reposo**. La interpretación es la "
            "del principio de indeterminación, pero las consecuencias "
            "son medibles: las vibraciones residuales de moléculas en "
            "$T = 0$, el efecto Casimir (fuerza entre placas metálicas "
            "debida a las fluctuaciones del vacío de QED), y la "
            "estabilidad del átomo (sin punto cero, el electrón "
            "colapsaría al núcleo)."
        ),
    ),
    "oscillator_nodes_count": DidacticObservation(
        kind="intuition",
        text_md=(
            "**$\\varphi_n$ tiene exactamente $n$ nodos.** El polinomio "
            "de Hermite $H_n$ es de grado $n$ con $n$ raíces reales. "
            "$\\varphi_0$ es estrictamente positiva, $\\varphi_1$ "
            "cambia de signo una vez, $\\varphi_2$ dos veces, etc. "
            "Es un patrón general en Sturm-Liouville: el "
            "**$n$-ésimo autoestado tiene $n$ ceros**, y eso permite "
            "identificar visualmente a qué nivel corresponde una "
            "función de onda."
        ),
    ),
}


def get(slug: str) -> DidacticObservation:
    """Retrieve an observation by slug."""
    return _REGISTRY[slug]


def maybe(slugs: list[str]) -> list[DidacticObservation]:
    """Convenience: build a list of observations from a list of slugs."""
    return [_REGISTRY[s] for s in slugs if s in _REGISTRY]
