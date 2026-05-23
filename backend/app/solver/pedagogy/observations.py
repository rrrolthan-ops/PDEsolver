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
    # ---- Fourier transform on the line -----------------------------------
    "fourier_transform_diagonalizes_pde": DidacticObservation(
        kind="theorem",
        text_md=(
            "**La transformada de Fourier diagonaliza $\\partial_x$.** "
            "Bajo $\\mathcal{F}$, la derivada espacial $\\partial_x$ se "
            "convierte en multiplicación por $ik$, y $\\partial_x^2$ en "
            "multiplicación por $-k^2$. Así, una EDP con coeficientes "
            "constantes se vuelve una **EDO en $t$** parametrizada por "
            "$k$. Es el análogo continuo de la separación de variables: "
            "los modos $e^{ikx}$ son las autofunciones del operador "
            "$\\partial_x$ sobre $L^2(\\mathbb{R})$, con espectro **continuo** "
            "$k \\in \\mathbb{R}$ en lugar del espectro discreto "
            "$\\{n\\pi/L\\}$ del intervalo acotado."
        ),
    ),
    "heat_kernel_self_similar": DidacticObservation(
        kind="intuition",
        text_md=(
            "**El núcleo del calor es auto-similar.** "
            "$G(x, t) = \\frac{1}{\\sqrt{4\\pi \\alpha^2 t}}\\,"
            "e^{-x^2/(4\\alpha^2 t)}$ tiene la simetría "
            "$G(\\lambda x, \\lambda^2 t) = \\lambda^{-1} G(x, t)$: si "
            "reescalas el espacio por $\\lambda$ y el tiempo por "
            "$\\lambda^2$, recuperas el mismo perfil (salvo amplitud). "
            "Esto fija la ley de escala del problema: el ancho "
            "característico crece como $\\sqrt{t}$, no como $t$. La "
            "difusión es **subbalística**: una partícula browniana "
            "recorre una distancia $\\sim \\sqrt{t}$, no $\\sim t$ "
            "(que sería el movimiento balístico de la onda)."
        ),
    ),
    "heat_infinite_speed": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**Velocidad infinita de propagación.** "
            "Aunque $f$ tenga soporte compacto (digamos, cero fuera de "
            "$[-1, 1]$), para **cualquier** $t > 0$ y **cualquier** $x$ "
            "la integral de convolución da un valor estrictamente "
            "positivo. Esto significa que la ecuación del calor "
            "propaga **instantáneamente** información a distancia "
            "infinita — una limitación bien conocida del modelo de "
            "difusión clásico, físicamente irreal pero útil porque "
            "los valores lejanos son exponencialmente pequeños. "
            "Contrasta con la ecuación de onda y d'Alembert, donde la "
            "información viaja como mucho a velocidad $c$ (cono de luz)."
        ),
    ),
    "burgers_self_steepening": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Por qué Burgers genera choques y el transporte lineal no.** "
            "En transporte lineal $u_t + c u_x = 0$, todas las "
            "características son paralelas (pendiente común $c$). El "
            "perfil viaja rígidamente. En Burgers la pendiente depende "
            "del valor local $u$, así que zonas con $u$ grande viajan "
            "más rápido y \"empujan\" a las zonas con $u$ pequeño. "
            "Esto crea **auto-empinamiento** del frente: cualquier "
            "dato inicial decreciente acabará por desarrollar un "
            "gradiente vertical (choque) en tiempo finito."
        ),
    ),
    "rankine_hugoniot_geometric": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Geometría de Rankine-Hugoniot.** En el plano $(x, t)$, "
            "el choque es una curva $x = s(t)$ que separa dos regiones "
            "regulares. La condición $ds/dt = (u_L + u_R)/2$ tiene una "
            "interpretación gráfica clara: la pendiente del choque "
            "**biseca** a las dos características que llegan a él. "
            "Esto se generaliza a leyes de conservación más generales "
            "$u_t + f(u)_x = 0$ como "
            "$ds/dt = (f(u_L) - f(u_R))/(u_L - u_R)$ — la pendiente de "
            "la cuerda entre $(u_L, f(u_L))$ y $(u_R, f(u_R))$."
        ),
    ),
    "burgers_vanishing_viscosity": DidacticObservation(
        kind="alternative",
        text_md=(
            "**Por qué \"el límite cuando ν → 0\" no es lo mismo que "
            "\"ν = 0 desde el principio\".** Burgers viscosa $u_t + u u_x "
            "= \\nu u_{xx}$ es **parabólica**: solución suave, única, "
            "para todo $t > 0$. Burgers no viscosa ($\\nu = 0$) es "
            "**hiperbólica**: admite **muchas** soluciones débiles, no "
            "siempre todas físicas. El **principio de selección entrópica** "
            "dice: la solución física es la que se obtiene como límite "
            "de las viscosas cuando $\\nu \\to 0^+$. Esto justifica "
            "matemáticamente la regla \"el choque comprime, nunca "
            "expande\" (condición de entropía de Lax)."
        ),
    ),
    "classification_is_invariant": DidacticObservation(
        kind="theorem",
        text_md=(
            "**La clasificación es invariante bajo cambios regulares "
            "de variables.** Si reemplazas $(x, y) \\to (\\xi(x, y), "
            "\\eta(x, y))$ con jacobiano no nulo, los nuevos "
            "coeficientes $A', B', C'$ cumplen "
            "$(B')^2 - 4 A' C' = J^2\\, (B^2 - 4AC)$ donde $J$ es el "
            "jacobiano. El **signo** se conserva. Por eso elíptico, "
            "parabólico e hiperbólico son **propiedades intrínsecas** "
            "de la EDP, no de la elección de coordenadas — y por eso "
            "tiene sentido hablar de \"la familia\" a la que pertenece."
        ),
    ),
    "three_families_three_physics": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Tres familias, tres físicas.** El signo del discriminante "
            "predice **cualitativamente** lo que verás:\n\n"
            "- $\\Delta > 0$ → **propagación con frente** (cono de "
            "luz, ondas viajeras, dominios de dependencia compactos).\n"
            "- $\\Delta = 0$ → **suavizado irreversible** (núcleos "
            "gaussianos, $\\sqrt{t}$, asimetría temporal).\n"
            "- $\\Delta < 0$ → **equilibrio sin propagación** "
            "(principio del máximo, valor medio, dependencia global).\n\n"
            "Reconocer la familia antes de elegir método ahorra mucho "
            "trabajo: aplicar D'Alembert a una EDP elíptica o "
            "transformada de Fourier a una hiperbólica raramente "
            "lleva a algo útil."
        ),
    ),
    "characteristics_lose_uniqueness": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Las características son las curvas donde el problema de "
            "Cauchy degenera.** Si especificas $u$ y $\\partial_n u$ "
            "sobre una curva $C$ que es característica, **no hay "
            "unicidad** (existen infinitas soluciones que coinciden "
            "con el dato sobre $C$). Si $C$ es transversal a las "
            "características, el problema de Cauchy está bien planteado "
            "localmente. Esto explica por qué las EDPs elípticas "
            "(sin características reales) son problemas de contorno "
            "globales y no admiten datos de Cauchy puntuales sin "
            "perder regularidad."
        ),
    ),
    "laplace_diagonalizes_dt": DidacticObservation(
        kind="theorem",
        text_md=(
            "**La transformada de Laplace diagonaliza $\\partial_t$.** "
            "Bajo $\\mathcal{L}$, la derivada temporal se convierte en "
            "multiplicación por $s$ menos el dato inicial: "
            "$\\mathcal{L}[u_t] = s\\, U - u(\\cdot, 0)$. Es el "
            "análogo de la propiedad de Fourier $\\mathcal{F}[u_x] = "
            "ik\\, \\hat u$, pero con dos diferencias prácticas "
            "cruciales: (1) **la condición inicial entra automáticamente** "
            "en la transformada (no hay que añadirla por separado), y "
            "(2) está pensada para tiempos $t \\ge 0$, no para "
            "$t \\in \\mathbb{R}$. Esto la hace la herramienta natural "
            "para problemas de valor inicial."
        ),
    ),
    "diffusion_length_sqrt_t": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Longitud de difusión $\\delta(t) = 2\\alpha\\sqrt{t}$.** "
            "Es la profundidad típica hasta la que el calor (o la "
            "concentración, o cualquier cantidad difusiva) penetra en "
            "tiempo $t$. Aparece en problemas tan distintos como el "
            "templado de aceros (¿cuánto tarda en enfriarse el centro?), "
            "el espesor de la capa límite térmica en aerodinámica, o el "
            "ancho de una interfase de electrodepósito. La regla "
            "$\\delta \\propto \\sqrt{t}$ es **universal** para "
            "fenómenos puramente difusivos."
        ),
    ),
    "erfc_inverse_laplace_pair": DidacticObservation(
        kind="theorem",
        text_md=(
            "**El par clave: $\\mathcal{L}^{-1}[s^{-1} e^{-a\\sqrt{s}}] = "
            "\\operatorname{erfc}(a/(2\\sqrt{t}))$.** Aparece en "
            "cualquier problema de calor o difusión sobre un dominio "
            "semi-infinito con condición de Dirichlet constante. La "
            "demostración pasa por la fórmula de inversión de "
            "Bromwich, pero para el aula la receta es: **memorizar el "
            "par y aplicarlo**. Si el dato es $f(t)$ en lugar de "
            "constante, se usa la integral de Duhamel "
            "$u(x, t) = \\int_0^t \\partial_t G(x, t-\\tau) f(\\tau)\\, d\\tau$ "
            "con $G$ esta misma solución."
        ),
    ),
    "self_similar_diffusion_eta": DidacticObservation(
        kind="intuition",
        text_md=(
            "**La variable de similaridad $\\eta = x/(2\\alpha\\sqrt{t})$.** "
            "Aparece **antes** de transformar (puede usarse directamente "
            "para reducir la EDP a una EDO en $\\eta$, sin pasar por "
            "Laplace) y es la pista de que el problema es "
            "**auto-similar**: invariante bajo el reescalado "
            "$(x, t) \\mapsto (\\lambda x, \\lambda^2 t)$. Cualquier "
            "EDP difusiva sin escala intrínseca de longitud (sin BCs "
            "que fijen un tamaño) tendrá esta estructura."
        ),
    ),
    "wick_rotation_heat_to_schrodinger": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Rotación de Wick: calor ↔ Schrödinger.** "
            "Si en la ecuación del calor $u_t = \\alpha^2 u_{xx}$ "
            "hacemos la sustitución $t \\to i t$ (rotación de Wick), "
            "obtenemos $-i u_t = \\alpha^2 u_{xx}$, formalmente "
            "equivalente a Schrödinger con $\\alpha^2 = \\hbar/(2m)$. "
            "Esta correspondencia es **profunda**: convierte el "
            "decaimiento exponencial real de los modos del calor en "
            "la rotación de fase pura de la mecánica cuántica, y es "
            "la base de la **formulación de integral de camino de "
            "Feynman** — donde sumar amplitudes cuánticas se ve como "
            "sumar exponenciales \"evaluadas en tiempo imaginario\"."
        ),
    ),
    "schrodinger_dispersion": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Dispersión $\\omega(k) = \\hbar k^2 / (2m)$.** "
            "La relación de dispersión es **cuadrática** en $k$, no "
            "lineal (como en la onda $\\omega = ck$) ni cuadrática "
            "imaginaria (como en el calor $\\omega = -i\\alpha^2 k^2$). "
            "La cuadratura real implica dos cosas: (1) velocidad de "
            "fase $v_\\phi = \\omega/k = \\hbar k/(2m)$ depende de $k$ "
            "→ **dispersión**, paquetes se ensanchan; (2) velocidad "
            "de grupo $v_g = d\\omega/dk = \\hbar k/m = p/m$ coincide "
            "con la velocidad clásica → **principio de correspondencia**, "
            "el centro del paquete sigue la trayectoria newtoniana."
        ),
    ),
    "schrodinger_wave_packet_spreading": DidacticObservation(
        kind="pitfall",
        text_md=(
            "**El paquete se ensancha incluso sin fuerzas.** "
            "Un paquete gaussiano libre con anchura inicial $\\sigma_0$ "
            "evoluciona a $\\sigma(t) = \\sigma_0 \\sqrt{1 + "
            "(\\hbar t / (2 m \\sigma_0^2))^2}$. Asintóticamente, "
            "$\\sigma(t) \\sim \\hbar t / (2 m \\sigma_0)$ — lineal en "
            "$t$, **no $\\sqrt{t}$ como el calor**. Físicamente: el "
            "principio de indeterminación obliga a que un paquete "
            "estrecho en posición ($\\sigma_0$ pequeño) tenga gran "
            "incertidumbre en momento ($\\sim \\hbar/\\sigma_0$), y por "
            "tanto una gama de velocidades clásicas — el paquete se "
            "expande precisamente porque sus componentes viajan a "
            "velocidades distintas."
        ),
    ),
    "schrodinger_no_bound_states": DidacticObservation(
        kind="theorem",
        text_md=(
            "**Espectro puramente continuo.** A diferencia del oscilador "
            "armónico (espectro discreto $E_n = \\hbar\\omega(n+1/2)$) "
            "o del pozo infinito ($E_n = n^2\\hbar^2\\pi^2/(2mL^2)$), "
            "el hamiltoniano libre $\\hat H = -\\hbar^2\\partial_x^2/(2m)$ "
            "tiene **espectro continuo** $E \\in [0, \\infty)$, sin "
            "estados ligados normalizables. Las \"autofunciones\" "
            "$e^{ikx}$ no son elementos de $L^2(\\mathbb{R})$: son "
            "**distribuciones** que se usan vía paquetes de onda. "
            "Esto refleja el hecho físico de que **una partícula libre "
            "no puede estar confinada**."
        ),
    ),
    "gaussian_smoothing": DidacticObservation(
        kind="intuition",
        text_md=(
            "**Suavizado instantáneo.** Aunque $f$ tenga discontinuidades "
            "o esquinas, la convolución con la gaussiana "
            "$G(\\cdot, t)$ es $C^\\infty$ para todo $t > 0$. El operador "
            "del calor regulariza el dato inicial inmediatamente: las "
            "frecuencias altas $|k| \\to \\infty$ son atenuadas por "
            "$e^{-\\alpha^2 k^2 t}$, una caída super-exponencial. Esta "
            "irreversibilidad (no se puede \"des-suavizar\") refleja la "
            "asimetría temporal del problema: la entropía aumenta."
        ),
    ),
}


def get(slug: str) -> DidacticObservation:
    """Retrieve an observation by slug."""
    return _REGISTRY[slug]


def maybe(slugs: list[str]) -> list[DidacticObservation]:
    """Convenience: build a list of observations from a list of slugs."""
    return [_REGISTRY[s] for s in slugs if s in _REGISTRY]
