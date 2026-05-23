"""Markdown explanation templates used by the methods.

Each template is a function `T_…(**kwargs) -> str`. The `kwargs` carry
the algebraic context of the moment (e.g. the boundary length `L`, the
diffusivity name `alpha`). Templates produce **only** the prose; the
LaTeX equations are attached separately in the corresponding `Step`.

Style guide
-----------
- Write in Spanish, as the pilot audience is Spanish-speaking.
- Always answer "why" before "how".
- Cite a theorem by name in bold when invoking it.
- One paragraph is usually enough; longer than three is suspicious.
- Refer to mathematical symbols inline with `$…$`.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# PASO 0 — Planteamiento
# ---------------------------------------------------------------------------

def T_statement_heat() -> str:
    return (
        "Tenemos una EDP de segundo orden lineal en dos variables: una "
        "espacial $x$ y otra temporal $t$. La incógnita $u(x, t)$ "
        "representa, físicamente, la **temperatura** a lo largo de una "
        "barra unidimensional homogénea con difusividad térmica "
        "$\\alpha^2 > 0$.\n\n"
        "Las condiciones de contorno fijan los extremos a temperatura "
        "cero y la condición inicial describe el perfil térmico de "
        "partida. Buscamos $u$ válida para todo $t > 0$."
    )


# ---------------------------------------------------------------------------
# PASO 1 — Clasificación
# ---------------------------------------------------------------------------

def T_classification_intro() -> str:
    return (
        "Antes de elegir un método, conviene clasificar la EDP. Para "
        "una EDP lineal de segundo orden en dos variables\n\n"
        "$$A\\,u_{xx} + B\\,u_{xy} + C\\,u_{yy} + (\\text{términos menores}) = 0$$\n\n"
        "se define el **discriminante** $\\Delta = B^2 - 4AC$. Su signo "
        "determina el carácter cualitativo de la ecuación:\n\n"
        "- $\\Delta > 0$ → **hiperbólica** (propagación).\n"
        "- $\\Delta = 0$ → **parabólica** (difusión).\n"
        "- $\\Delta < 0$ → **elíptica** (equilibrio).\n\n"
        "Calculamos los coeficientes en nuestra ecuación reescribiéndola "
        "como expresión igualada a cero."
    )


# ---------------------------------------------------------------------------
# PASO 3 — Separación de variables (calor)
# ---------------------------------------------------------------------------

def T_sov_ansatz() -> str:
    return (
        "**Hipótesis de separación.** Probamos un ansatz "
        "$u(x, t) = X(x)\\, T(t)$, donde $X$ depende sólo de $x$ y $T$ "
        "sólo de $t$. ¿Por qué tiene sentido esto?\n\n"
        "Porque la EDP es **lineal y homogénea**: el espacio de "
        "soluciones es un espacio vectorial. Basta encontrar una "
        "familia de soluciones particulares con esta forma; cualquier "
        "combinación lineal (incluso infinita) será también solución, "
        "y por **superposición** podremos ajustar la condición inicial.\n\n"
        "No estamos perdiendo generalidad: el teorema espectral de "
        "Sturm-Liouville garantiza que las soluciones del problema "
        "espacial forman una base ortogonal del $L^2([0, L])$, así que "
        "**toda** condición inicial razonable se desarrollará como "
        "combinación lineal de productos $X_n(x)T_n(t)$."
    )


def T_sov_separate_into_ode() -> str:
    return (
        "Sustituimos el ansatz en la EDP, calculamos las derivadas "
        "parciales y agrupamos cada lado de la ecuación con una sola "
        "variable. Veamos paso a paso."
    )


def T_sov_constant_separation() -> str:
    return (
        "Tenemos una identidad entre una función que depende **sólo de "
        "$t$** y otra que depende **sólo de $x$**. La única forma de que "
        "dos cosas independientes sean siempre iguales es que ambas "
        "sean **constantes**. Llamamos a esa constante $-\\lambda$ "
        "(el signo negativo es convencional y simplifica el álgebra "
        "posterior; veremos que $\\lambda$ resultará ser real y positivo).\n\n"
        "**Ojo:** la elección del signo de la constante no cambia la "
        "matemática, pero sí la cosmética. Hay libros que escriben "
        "$+\\lambda$ y obtienen exactamente las mismas soluciones con "
        "$\\lambda$ negativo."
    )


def T_sov_three_cases_intro() -> str:
    return (
        "La EDO espacial $X'' + \\lambda X = 0$ tiene **tres familias "
        "de soluciones** según el signo de $\\lambda$. Hay que examinar "
        "las tres y descartar las que sean incompatibles con las "
        "condiciones de contorno. Este examen es la parte donde más "
        "estudiantes se confunden, así que lo hacemos minuciosamente."
    )


def T_sov_case_lambda_negative() -> str:
    return (
        "**Caso 1: $\\lambda < 0$.** Escribimos $\\lambda = -\\mu^2$ con "
        "$\\mu > 0$ para tener un parámetro positivo. La EDO se "
        "convierte en $X'' - \\mu^2 X = 0$, cuya solución general es "
        "una combinación de **exponenciales reales** "
        "$X(x) = A\\, e^{\\mu x} + B\\, e^{-\\mu x}$ (equivalentemente, "
        "combinación de senos y cosenos hiperbólicos)."
    )


def T_sov_case_lambda_negative_discard() -> str:
    return (
        "Imponemos $X(0) = 0$ y $X(L) = 0$. La primera da $A + B = 0$, "
        "es decir $B = -A$, y la segunda obliga a "
        "$A(e^{\\mu L} - e^{-\\mu L}) = 2A \\sinh(\\mu L) = 0$. "
        "Como $\\mu > 0$ implica $\\sinh(\\mu L) \\neq 0$, debe ser "
        "$A = 0$ y por tanto $B = 0$. La única solución es la **trivial** "
        "$X \\equiv 0$, que no nos sirve. Descartamos este caso."
    )


def T_sov_case_lambda_zero() -> str:
    return (
        "**Caso 2: $\\lambda = 0$.** La EDO se reduce a $X'' = 0$, "
        "cuya solución general es la **función afín** "
        "$X(x) = A x + B$."
    )


def T_sov_case_lambda_zero_discard() -> str:
    return (
        "$X(0) = 0$ da $B = 0$, y $X(L) = 0$ da $AL = 0$, así que "
        "$A = 0$. Otra vez la solución trivial. Descartamos este caso "
        "también."
    )


def T_sov_case_lambda_positive() -> str:
    return (
        "**Caso 3: $\\lambda > 0$.** Escribimos $\\lambda = \\mu^2$ con "
        "$\\mu > 0$. La EDO es $X'' + \\mu^2 X = 0$, cuya solución "
        "general es una combinación de **funciones trigonométricas**\n\n"
        "$$X(x) = A \\cos(\\mu x) + B \\sin(\\mu x).$$"
    )


def T_sov_eigenvalues() -> str:
    return (
        "Imponemos $X(0) = 0$: $A \\cos 0 + B \\sin 0 = A = 0$. "
        "Queda $X(x) = B \\sin(\\mu x)$. Ahora imponemos $X(L) = 0$:\n\n"
        "$$B \\sin(\\mu L) = 0.$$\n\n"
        "Para no caer en la solución trivial necesitamos $B \\neq 0$, "
        "luego **$\\sin(\\mu L) = 0$**. Eso obliga a $\\mu L = n\\pi$ "
        "con $n \\in \\mathbb{Z}^+$.\n\n"
        "Hemos llegado al núcleo del método: el problema espacial "
        "tiene **una familia discreta** de soluciones no triviales, "
        "una por cada $n = 1, 2, 3, \\dots$. Estas se llaman "
        "**autofunciones** y los $\\lambda_n = (n\\pi / L)^2$ "
        "correspondientes, **autovalores**.\n\n"
        "Esto es un caso particular del **teorema de Sturm-Liouville**: "
        "todo problema de la forma $-(p X')' + q X = \\lambda r X$ con "
        "condiciones de contorno separadas tiene una sucesión "
        "creciente $\\lambda_1 < \\lambda_2 < \\dots \\to \\infty$ de "
        "autovalores reales, con autofunciones que forman base "
        "ortogonal."
    )


def T_sov_temporal_ode() -> str:
    return (
        "Resuelta la parte espacial, volvemos a la EDO temporal. Para "
        "cada autovalor $\\lambda_n$ tenemos\n\n"
        "$$T_n'(t) + \\alpha^2 \\lambda_n T_n(t) = 0,$$\n\n"
        "una EDO lineal de primer orden con coeficiente constante. "
        "Su solución es la exponencial decreciente "
        "$T_n(t) = C_n \\, e^{-\\alpha^2 \\lambda_n t}$.\n\n"
        "El factor $e^{-\\alpha^2 \\lambda_n t}$ tiene una "
        "interpretación física inmediata: cuanto mayor sea $n$ "
        "(modos más oscilatorios en el espacio), más rápido se "
        "**amortiguan en el tiempo**. Por eso, pasado un cierto "
        "tiempo, sólo sobreviven los primeros armónicos: la barra "
        "tiende a la solución estacionaria $u \\equiv 0$."
    )


def T_sov_superposition() -> str:
    return (
        "Cada producto $X_n(x) T_n(t)$ es una solución particular. "
        "Por la **linealidad y homogeneidad** de la EDP, cualquier "
        "combinación lineal sigue siendo solución; al pasar al "
        "límite con infinitos términos obtenemos\n\n"
        "$$u(x, t) = \\sum_{n=1}^{\\infty} B_n \\sin\\!\\left(\\tfrac{n\\pi x}{L}\\right) "
        "e^{-\\alpha^2 (n\\pi/L)^2 t}.$$\n\n"
        "Los coeficientes $B_n$ son hasta ahora **constantes libres** "
        "que se fijarán con la condición inicial."
    )


# ---------------------------------------------------------------------------
# PASO 5 — Coeficientes de Fourier
# ---------------------------------------------------------------------------

def T_fourier_coefficients_setup() -> str:
    return (
        "Imponemos la condición inicial $u(x, 0) = f(x)$. Como "
        "$e^{0} = 1$, la serie en $t = 0$ se reduce a\n\n"
        "$$f(x) = \\sum_{n=1}^{\\infty} B_n \\sin\\!\\left(\\tfrac{n\\pi x}{L}\\right).$$\n\n"
        "Reconocemos el **desarrollo de Fourier de senos** de $f$ en "
        "$[0, L]$. Para extraer $B_n$ usamos la **relación de "
        "ortogonalidad**\n\n"
        "$$\\int_0^L \\sin\\!\\left(\\tfrac{m\\pi x}{L}\\right) \\sin\\!\\left(\\tfrac{n\\pi x}{L}\\right) dx = "
        "\\begin{cases} L/2 & m = n \\\\ 0 & m \\neq n \\end{cases}.$$\n\n"
        "Multiplicamos la serie por $\\sin(m\\pi x / L)$ e integramos "
        "término a término en $[0, L]$. Sólo sobrevive el sumando "
        "$m = n$, de donde despejamos:"
    )


def T_fourier_coefficient_formula() -> str:
    return (
        "$$B_n = \\frac{2}{L} \\int_0^L f(x) \\sin\\!\\left(\\tfrac{n\\pi x}{L}\\right) dx.$$"
    )


def T_fourier_coefficient_compute(f_latex: str) -> str:
    return (
        f"Calculamos la integral con $f(x) = {f_latex}$. Vamos a "
        "desarrollar toda la integración, sin saltarnos pasos."
    )


# ---------------------------------------------------------------------------
# PASO 6 — Solución final
# ---------------------------------------------------------------------------

def T_final_solution() -> str:
    return (
        "Sustituyendo los coeficientes obtenidos en la superposición, "
        "la solución del problema es:"
    )


# ---------------------------------------------------------------------------
# PASO 7 — Verificación
# ---------------------------------------------------------------------------

def T_verification_intro() -> str:
    return (
        "Antes de dar por terminado el ejercicio, **verificamos**. La "
        "verificación es una práctica matemática esencial y, en este "
        "caso, mecanizable: sustituimos $u(x, t)$ en la EDP original "
        "y comprobamos que la igualdad se cumple idénticamente.\n\n"
        "También verificamos las condiciones de contorno e iniciales "
        "una por una."
    )


def T_verification_pde_ok() -> str:
    return (
        "Calculando $u_t$ y $\\alpha^2 u_{xx}$ término a término y "
        "restándolas, todos los sumandos se cancelan. La EDP se "
        "satisface idénticamente."
    )


def T_verification_bc_ok(where: str) -> str:
    return f"Evaluando la serie en $x = {where}$, todos los senos se anulan: la condición de contorno se cumple."


def T_verification_ic_ok() -> str:
    return (
        "Por construcción de los coeficientes $B_n$ como desarrollo de "
        "Fourier de $f$, la suma en $t = 0$ reproduce $f(x)$ en sentido "
        "$L^2$, y puntualmente donde $f$ sea continua."
    )


# ---------------------------------------------------------------------------
# PASO 9 — Interpretación física
# ---------------------------------------------------------------------------

def T_physical_interpretation() -> str:
    return (
        "La solución es una **suma de modos normales** $\\sin(n\\pi x / L)$ "
        "que oscilan en el espacio y se amortiguan exponencialmente en "
        "el tiempo. El modo $n$ decae con tiempo característico "
        "$\\tau_n = L^2 / (\\alpha^2 n^2 \\pi^2)$.\n\n"
        "Consecuencias físicas:\n\n"
        "- Cuanto **más alta** la frecuencia espacial (mayor $n$), "
        "**más rápido** se disipa. Las irregularidades finas se "
        "alisan primero.\n"
        "- La barra tiende uniformemente a la temperatura cero (la "
        "**solución estacionaria** del problema con extremos a cero).\n"
        "- El **principio del máximo** garantiza que la temperatura no "
        "puede crecer en ningún punto del interior si no entra calor: "
        "se cumple visualmente en la gráfica."
    )


# ===========================================================================
# WAVE EQUATION (1D bounded) — separation of variables
# ===========================================================================

def T_statement_wave() -> str:
    return (
        "Tenemos la **ecuación de onda 1D** con velocidad de propagación "
        "$c > 0$. La incógnita $u(x, t)$ representa, por ejemplo, el "
        "desplazamiento transversal de una cuerda elástica fija en sus "
        "dos extremos. A diferencia del calor, **el tiempo entra al "
        "cuadrado** ($u_{tt}$): la EDP es invariante por inversión "
        "temporal y no disipa — las soluciones oscilan indefinidamente.\n\n"
        "Necesitamos **dos** condiciones iniciales: el perfil $u(x, 0)$ "
        "y la velocidad inicial $u_t(x, 0)$. Esto es estructural: el "
        "operador temporal es de segundo orden, así que su problema "
        "de Cauchy en $t = 0$ requiere posición y velocidad, "
        "igual que en mecánica clásica."
    )


def T_wave_temporal_ode() -> str:
    return (
        "La ecuación temporal $T_n'' + c^2 \\lambda_n\\, T_n = 0$ es una "
        "**EDO de segundo orden con coeficiente constante positivo**: su "
        "solución general es una combinación de seno y coseno. "
        "Comparemos con el caso del calor:\n\n"
        "- **Calor:** $T_n' + \\alpha^2 \\lambda_n T_n = 0$ → "
        "$T_n = e^{-\\alpha^2 \\lambda_n t}$ (decaimiento).\n"
        "- **Onda:** $T_n'' + c^2 \\lambda_n T_n = 0$ → "
        "$T_n = A_n \\cos(c \\mu_n t) + B_n \\sin(c \\mu_n t)$ "
        "(oscilación), donde $\\mu_n = \\sqrt{\\lambda_n} = n\\pi/L$.\n\n"
        "Cada modo $n$ tiene una **frecuencia angular** $\\omega_n = c\\mu_n "
        "= c n\\pi/L$. Las frecuencias forman una sucesión armónica "
        "(múltiplos enteros de $c\\pi/L$): por eso una cuerda suena "
        "musicalmente afinada."
    )


def T_wave_two_ics() -> str:
    return (
        "Para fijar **dos** familias de coeficientes ($A_n$ y $B_n$) "
        "necesitamos **dos** condiciones iniciales. Sustituyendo en "
        "$t = 0$:\n\n"
        "- De $u(x, 0) = f(x)$ obtenemos los $A_n$ (la parte coseno "
        "del modo temporal vale 1 en $t = 0$).\n"
        "- De $u_t(x, 0) = g(x)$ obtenemos los $B_n$: al derivar la "
        "serie y evaluar en $t = 0$, la parte coseno se anula y queda "
        "el seno multiplicado por $c\\mu_n$.\n\n"
        "Ambas familias son coeficientes de Fourier en seno, con sus "
        "fórmulas integrales de siempre, salvo que la de $B_n$ trae un "
        "factor $1/(c\\mu_n)$ de la derivación."
    )


def T_wave_physical_interpretation() -> str:
    return (
        "La cuerda vibra como **superposición de modos normales** "
        "$\\sin(n\\pi x/L)$ cada uno con su propia frecuencia "
        "$\\omega_n = c n\\pi/L$. La energía no se disipa: el "
        "sistema es conservativo. Observaciones físicas:\n\n"
        "- Los modos forman una **serie armónica** (frecuencias en "
        "razón 1, 2, 3, …): si arrancamos un piano, escuchamos la "
        "fundamental más sus armónicos superiores.\n"
        "- La forma de la onda es **2L-periódica en el tiempo**: "
        "todos los $\\omega_n$ son múltiplos enteros de $\\omega_1$.\n"
        "- La **fórmula de D'Alembert** (otro método en este repo) "
        "muestra que la misma solución se puede ver como dos pulsos "
        "viajando: $u(x,t) = \\Phi(x - ct) + \\Psi(x + ct)$. Ambas "
        "visiones son equivalentes."
    )


# ===========================================================================
# D'ALEMBERT — wave 1D on the infinite line
# ===========================================================================

def T_dalembert_statement() -> str:
    return (
        "Resolvemos la **ecuación de onda 1D sin fronteras**: la cuerda "
        "es infinitamente larga ($x \\in \\mathbb{R}$), o bien estudiamos "
        "un intervalo de tiempo lo bastante corto como para que las "
        "fronteras todavía no influyan. Dadas las condiciones iniciales "
        "$u(x, 0) = f(x)$ y $u_t(x, 0) = g(x)$, buscamos $u(x, t)$ para "
        "$t > 0$."
    )


def T_dalembert_method_motivation() -> str:
    return (
        "Vamos a **factorizar el operador de onda**. Notamos que\n\n"
        "$$\\partial_t^2 - c^2 \\partial_x^2 = "
        "(\\partial_t - c\\partial_x)(\\partial_t + c\\partial_x).$$\n\n"
        "Cada factor anula a funciones de la forma $\\Phi(x \\pm ct)$. "
        "Esto sugiere el **cambio de variables características** "
        "$\\xi = x - ct$, $\\eta = x + ct$, en el que la EDP se "
        "convierte en $u_{\\xi\\eta} = 0$, integrable trivialmente."
    )


def T_dalembert_change_of_variables() -> str:
    return (
        "Definamos $\\xi = x - ct$ y $\\eta = x + ct$. Por la regla de la "
        "cadena:\n\n"
        "- $u_x = u_\\xi + u_\\eta$,\n"
        "- $u_t = -c\\, u_\\xi + c\\, u_\\eta$.\n\n"
        "Iterando para las segundas derivadas (cuidado con los productos "
        "cruzados, este es el paso donde más se equivoca uno):\n\n"
        "- $u_{xx} = u_{\\xi\\xi} + 2 u_{\\xi\\eta} + u_{\\eta\\eta}$,\n"
        "- $u_{tt} = c^2 u_{\\xi\\xi} - 2 c^2 u_{\\xi\\eta} + c^2 u_{\\eta\\eta}$.\n\n"
        "Sustituyendo en $u_{tt} - c^2 u_{xx} = 0$ casi todo se cancela y "
        "queda $-4 c^2 u_{\\xi\\eta} = 0$, es decir $u_{\\xi\\eta} = 0$."
    )


def T_dalembert_general_solution() -> str:
    return (
        "Integrando $u_{\\xi\\eta} = 0$ primero respecto a $\\eta$ "
        "(la \"constante\" depende de $\\xi$) y luego en $\\xi$:\n\n"
        "$$u(\\xi, \\eta) = \\Phi(\\xi) + \\Psi(\\eta),$$\n\n"
        "donde $\\Phi$ y $\\Psi$ son funciones arbitrarias (de "
        "clase $C^2$). Deshaciendo el cambio:\n\n"
        "$$u(x, t) = \\Phi(x - ct) + \\Psi(x + ct).$$\n\n"
        "**Interpretación inmediata:** la solución es la superposición de "
        "dos ondas que viajan sin deformarse, una hacia la derecha con "
        "velocidad $+c$ y otra hacia la izquierda con velocidad $-c$."
    )


def T_dalembert_apply_ics() -> str:
    return (
        "Ahora ajustamos $\\Phi$ y $\\Psi$ a las condiciones iniciales.\n\n"
        "**Posición en $t=0$:** $\\Phi(x) + \\Psi(x) = f(x)$.\n\n"
        "**Velocidad en $t=0$:** derivando, "
        "$-c\\Phi'(x) + c\\Psi'(x) = g(x)$, es decir "
        "$\\Psi'(x) - \\Phi'(x) = g(x)/c$.\n\n"
        "Integrando la segunda de $0$ a $x$:\n\n"
        "$$\\Psi(x) - \\Phi(x) = "
        "\\frac{1}{c}\\int_0^x g(s)\\, ds + K,$$\n\n"
        "con $K$ una constante de integración. Junto con la primera "
        "ecuación tenemos un sistema lineal en $\\Phi(x)$ y $\\Psi(x)$ "
        "que se resuelve sumando y restando."
    )


def T_dalembert_formula() -> str:
    return (
        "Sumando y restando las dos ecuaciones, despejamos:\n\n"
        "$$\\Phi(x) = \\frac{f(x)}{2} - \\frac{1}{2c}\\int_0^x g(s)\\, ds - \\frac{K}{2},$$\n\n"
        "$$\\Psi(x) = \\frac{f(x)}{2} + \\frac{1}{2c}\\int_0^x g(s)\\, ds + \\frac{K}{2}.$$\n\n"
        "Las constantes $K$ se cancelan al formar $u = \\Phi(x-ct) + \\Psi(x+ct)$. "
        "Sustituyendo y agrupando se obtiene la célebre **fórmula de D'Alembert**:"
    )


def T_dalembert_final_box() -> str:
    return (
        "$$\\boxed{\\; u(x, t) = \\frac{f(x - ct) + f(x + ct)}{2} + "
        "\\frac{1}{2c}\\int_{x-ct}^{x+ct} g(s)\\, ds. \\;}$$"
    )


def T_dalembert_physical_interpretation() -> str:
    return (
        "Tres lecturas físicas se extraen directamente de la fórmula:\n\n"
        "- **Dominio de dependencia.** $u(x, t)$ sólo depende de los "
        "valores iniciales en el intervalo $[x - ct, x + ct]$. Lo que "
        "ocurra fuera no afecta a $(x, t)$. La información viaja a "
        "velocidad **finita** $c$.\n"
        "- **Dos pulsos viajeros.** El perfil inicial $f$ se reparte por "
        "mitades en dos copias que se separan: una a velocidad $+c$, "
        "otra a $-c$. Es el famoso \"truco del pulso partido en dos\".\n"
        "- **Velocidad inicial → desplazamiento medio.** La integral de "
        "$g$ en el intervalo dependiente añade un \"empuje acumulado\" "
        "proporcional al impulso recibido entre los dos rayos "
        "característicos."
    )


# ===========================================================================
# LAPLACE on a rectangle — separation of variables
# ===========================================================================

def T_statement_laplace_rect() -> str:
    return (
        "Resolvemos la **ecuación de Laplace** $\\Delta u = u_{xx} + u_{yy} = 0$ "
        "en el rectángulo $[0, a] \\times [0, b]$. La EDP es elíptica "
        "y describe estados de equilibrio: por ejemplo, la **temperatura "
        "estacionaria** de una placa rectangular cuando ya no varía con "
        "el tiempo, o un potencial electrostático en un dominio sin "
        "cargas internas.\n\n"
        "El problema clásico fija el valor de $u$ en cada lado (Dirichlet). "
        "Tomamos el caso simétrico más sencillo:\n\n"
        "- $u(x, 0) = 0$,\n"
        "- $u(x, b) = f(x)$,\n"
        "- $u(0, y) = u(a, y) = 0$.\n\n"
        "Es decir, una placa caliente sólo por arriba y refrigerada por "
        "los otros tres lados."
    )


def T_laplace_signs() -> str:
    return (
        "**Atención al signo de la constante de separación.** En el "
        "calor escribíamos $-\\lambda$ para que las autofunciones "
        "espaciales fueran trigonométricas. Aquí, separando "
        "$u(x, y) = X(x) Y(y)$ y dividiendo, obtenemos\n\n"
        "$$\\frac{X''(x)}{X(x)} = -\\frac{Y''(y)}{Y(y)} = -\\lambda.$$\n\n"
        "Esto da $X'' + \\lambda X = 0$ (oscilatoria, como antes) y "
        "$Y'' - \\lambda Y = 0$ (**hiperbólica**: combinaciones de "
        "exponenciales o, equivalentemente, $\\sinh$ y $\\cosh$). "
        "La asimetría es clave: una dirección oscila, la otra crece o "
        "decrece exponencialmente."
    )


def T_laplace_Y_ode() -> str:
    return (
        "La EDO en $y$ es $Y'' - \\lambda_n Y = 0$ con "
        "$\\lambda_n = (n\\pi/a)^2 > 0$. Su solución general se "
        "escribe convenientemente con senos y cosenos hiperbólicos "
        "(equivalente a $A e^{\\mu y} + B e^{-\\mu y}$):\n\n"
        "$$Y_n(y) = C_n \\sinh\\!\\left(\\tfrac{n\\pi y}{a}\\right) "
        "+ D_n \\cosh\\!\\left(\\tfrac{n\\pi y}{a}\\right).$$\n\n"
        "La condición $u(x, 0) = 0$ se traduce en $Y_n(0) = 0$, "
        "esto es $D_n = 0$. Sobreviven sólo las $\\sinh$."
    )


def T_laplace_physical_interpretation() -> str:
    return (
        "La solución de Laplace en el rectángulo es la **distribución "
        "estacionaria** de temperatura (o potencial). Observaciones:\n\n"
        "- **Principio del máximo.** El máximo y el mínimo de $u$ se "
        "alcanzan **en la frontera**. En el interior, $u$ es "
        "armónica y nunca presenta extremos locales estrictos.\n"
        "- **Suavizado.** Los modos altos $n$ crecen como "
        "$\\sinh(n\\pi y/a)$ y por tanto requieren coeficientes "
        "pequeños para no explotar. La solución hereda el contenido "
        "espectral de $f$ pero se suaviza al alejarse de la frontera "
        "caliente.\n"
        "- **Unicidad.** Las soluciones de Dirichlet en dominios "
        "acotados son únicas (corolario del principio del máximo): "
        "lo que obtenemos es la única respuesta posible."
    )


# ===========================================================================
# LAPLACE on a disk — separation in polar coordinates
# ===========================================================================

def T_statement_laplace_disk() -> str:
    return (
        "Resolvemos la **ecuación de Laplace en un disco** de radio $R$: "
        "$\\Delta u = 0$ para $r < R$, $\\theta \\in [0, 2\\pi)$, con "
        "el valor de $u$ prescrito en la circunferencia $u(R, \\theta) = "
        "f(\\theta)$. Físicamente: la temperatura estacionaria de un "
        "disco cuyo borde está a una temperatura dada, o el potencial "
        "electrostático en un dominio circular.\n\n"
        "La geometría circular hace que las **coordenadas polares** sean "
        "la elección natural. En polares, "
        "$\\Delta u = u_{rr} + \\tfrac{1}{r} u_r + "
        "\\tfrac{1}{r^2} u_{\\theta\\theta}$."
    )


def T_disk_method_choice() -> str:
    return (
        "**Separación en coordenadas polares.** Probamos "
        "$u(r, \\theta) = \\Phi(\\theta)\\, P(r)$. Sustituyendo en "
        "$\\Delta u = 0$ y multiplicando por $r^2 / (P\\Phi)$, "
        "obtenemos\n\n"
        "$$\\frac{r^2 P'' + r P'}{P} = -\\frac{\\Phi''}{\\Phi} = \\lambda,$$\n\n"
        "donde $\\lambda$ es la constante de separación. La elección de "
        "signo (positiva esta vez, contraria al calor) viene determinada "
        "por la **2π-periodicidad** que vamos a imponer en $\\Phi$, "
        "que sólo es compatible con $\\lambda \\geq 0$."
    )


def T_disk_angular_periodicity() -> str:
    return (
        "**EDO angular:** $\\Phi'' + \\lambda \\Phi = 0$, con la condición "
        "implícita de **periodicidad** $\\Phi(\\theta + 2\\pi) = "
        "\\Phi(\\theta)$ (la coordenada $\\theta$ es angular: $\\theta = 0$ "
        "y $\\theta = 2\\pi$ son el mismo punto físico).\n\n"
        "Examinemos los signos posibles de $\\lambda$:\n\n"
        "- **$\\lambda < 0$:** soluciones exponenciales reales. **No son "
        "periódicas** (a menos que sean cero). Descartado.\n"
        "- **$\\lambda = 0$:** $\\Phi(\\theta) = A\\theta + B$. El término "
        "$A\\theta$ no es periódico, así que $A = 0$. Queda $\\Phi = B$ "
        "constante: el modo $n = 0$.\n"
        "- **$\\lambda > 0$:** $\\Phi = A\\cos(\\sqrt{\\lambda}\\,\\theta) + "
        "B\\sin(\\sqrt{\\lambda}\\,\\theta)$. La periodicidad obliga a "
        "$\\sqrt{\\lambda} = n$ entero positivo. Autovalores "
        "$\\lambda_n = n^2$ con autofunciones $\\cos(n\\theta), \\sin(n\\theta)$."
    )


def T_disk_radial_euler() -> str:
    return (
        "**EDO radial:** $r^2 P'' + r P' - n^2 P = 0$, la **ecuación de "
        "Euler** (también llamada equidimensional). Su forma sugiere "
        "intentar $P(r) = r^p$: sustituyendo, "
        "$p(p-1) r^p + p r^p - n^2 r^p = 0$, es decir "
        "$p^2 = n^2$, así que $p = \\pm n$.\n\n"
        "- **Para $n = 0$:** raíz doble $p = 0$, soluciones $P = 1$ y "
        "$P = \\ln r$. **Descartamos $\\ln r$** porque diverge en el "
        "origen; en un disco sólido (sin agujero) la solución debe ser "
        "regular allí.\n"
        "- **Para $n \\geq 1$:** soluciones $P = r^n$ y $P = r^{-n}$. "
        "**Descartamos $r^{-n}$** por la misma razón: explota en el "
        "centro."
    )


def T_disk_fourier_coefficients() -> str:
    return (
        "Aplicamos la condición de frontera $u(R, \\theta) = f(\\theta)$. "
        "La serie evaluada en $r = R$ se convierte en la **serie de "
        "Fourier completa** de $f$ en $[0, 2\\pi]$:\n\n"
        "$$f(\\theta) = \\tfrac{a_0}{2} + \\sum_{n=1}^{\\infty} "
        "R^n \\bigl[a_n \\cos(n\\theta) + b_n \\sin(n\\theta)\\bigr].$$\n\n"
        "Usando la **ortogonalidad** estándar de cosenos y senos en "
        "$[0, 2\\pi]$:"
    )


def T_disk_poisson_kernel_note() -> str:
    return (
        "**Nota:** la serie obtenida tiene una forma cerrada notable. "
        "Sumando explícitamente la geometric series asociada, se llega a "
        "la **fórmula integral de Poisson**:\n\n"
        "$$u(r, \\theta) = \\frac{1}{2\\pi} \\int_0^{2\\pi} "
        "\\frac{R^2 - r^2}{R^2 - 2Rr\\cos(\\theta - \\theta') + r^2}\\, "
        "f(\\theta')\\, d\\theta'.$$\n\n"
        "El núcleo $K(r, \\theta - \\theta') = (R^2 - r^2) / "
        "(R^2 - 2Rr\\cos(\\Delta\\theta) + r^2)$ se llama **núcleo de "
        "Poisson** y es la **función de Green** del disco para Laplace. "
        "Esta fórmula muestra que $u(r, \\theta)$ es un **promedio "
        "ponderado** de los valores de $f$ en la frontera; en el centro "
        "($r = 0$) el peso se vuelve uniforme y $u(0) = \\tfrac{1}{2\\pi} "
        "\\int_0^{2\\pi} f(\\theta')\\, d\\theta'$ es el **promedio "
        "circular** de $f$ — el famoso **teorema del valor medio para "
        "funciones armónicas**."
    )


def T_disk_physical_interpretation() -> str:
    return (
        "La solución $u(r, \\theta)$ describe la **distribución "
        "estacionaria** dentro del disco. Observaciones:\n\n"
        "- **Suavizado radial.** El modo angular $n$ entra con peso "
        "$(r/R)^n$. Cuanto más alta la frecuencia angular, **más rápido** "
        "se atenúa al alejarse del borde. En el centro, sólo sobrevive "
        "el modo $n = 0$ (constante).\n"
        "- **Valor en el centro.** $u(0) = a_0/2 = \\frac{1}{2\\pi}\\int "
        "f(\\theta') d\\theta'$: el valor en el centro es el promedio del "
        "dato de frontera. Es el teorema del valor medio.\n"
        "- **Principio del máximo:** como en el rectángulo, los extremos "
        "viven en la frontera."
    )


# ===========================================================================
# POISSON 1D — Green's function
# ===========================================================================

def T_statement_poisson_1d() -> str:
    return (
        "Resolvemos el problema de **Poisson 1D**: una EDP elíptica "
        "con **término fuente** $f(x)$ y condiciones de Dirichlet "
        "homogéneas. Físicamente: el desplazamiento estacionario de "
        "una cuerda tensa con carga distribuida $f(x)$ por unidad de "
        "longitud y extremos fijos. O el potencial 1D con densidad de "
        "carga prescrita.\n\n"
        "Notar que esta es una EDO de segundo orden, no una EDP "
        "propiamente dicha. La elegimos como **caso piloto del método "
        "de la función de Green**, porque permite ver el método en su "
        "forma más limpia antes de generalizarlo a 2D o 3D."
    )


def T_greens_function_motivation() -> str:
    return (
        "**Idea del método.** Buscamos un operador lineal $\\mathcal{G}$ "
        "tal que la solución se escriba como\n\n"
        "$$u(x) = \\int_0^L G(x, \\xi)\\, f(\\xi)\\, d\\xi.$$\n\n"
        "El **núcleo** $G(x, \\xi)$ se llama **función de Green** del "
        "operador. Físicamente, $G(x, \\xi)$ es la respuesta del sistema "
        "a una **fuente puntual unitaria** localizada en $x = \\xi$: el "
        "desplazamiento de la cuerda con la masa de $1$ kg colgando en "
        "el punto $\\xi$. Una vez conocido $G$, **cualquier** distribución "
        "$f$ se trata por superposición integral."
    )


def T_greens_function_defining_properties() -> str:
    return (
        "Caracterizamos $G(x, \\xi)$ con cuatro propiedades:\n\n"
        "1. **EDO con delta en la fuente:** "
        "$-\\frac{\\partial^2 G}{\\partial x^2} = \\delta(x - \\xi)$. "
        "Lejos de $\\xi$ ($x \\neq \\xi$), $G$ satisface "
        "$G_{xx} = 0$, así que en cada lado de $\\xi$ es **lineal en $x$**.\n"
        "2. **Condiciones de contorno homogéneas:** "
        "$G(0, \\xi) = G(L, \\xi) = 0$.\n"
        "3. **Continuidad** en $x = \\xi$: $G(\\xi^-, \\xi) = G(\\xi^+, \\xi)$.\n"
        "4. **Salto de la derivada** en $x = \\xi$: integrando la EDO "
        "alrededor de $\\xi$, $\\partial_x G(\\xi^+) - "
        "\\partial_x G(\\xi^-) = -1$.\n\n"
        "Las propiedades 1 y 2 dan dos rectas (una en cada lado), las 3 y 4 "
        "fijan las cuatro constantes."
    )


def T_greens_function_construction() -> str:
    return (
        "Construimos $G$ explícitamente:\n\n"
        "En $0 < x < \\xi$: $G(x, \\xi) = A x + B$. Por $G(0, \\xi) = 0$, "
        "$B = 0$, así $G = A x$.\n\n"
        "En $\\xi < x < L$: $G(x, \\xi) = C x + D$. Por $G(L, \\xi) = 0$, "
        "$D = -CL$, así $G = C(x - L)$.\n\n"
        "**Continuidad** en $x = \\xi$: $A \\xi = C(\\xi - L)$.\n\n"
        "**Salto** de derivadas en $x = \\xi$: derivada por la derecha "
        "menos derivada por la izquierda = $-1$, es decir $C - A = -1$.\n\n"
        "Resolviendo el sistema $2\\times2$:\n\n"
        "$$A = \\frac{L - \\xi}{L}, \\qquad C = -\\frac{\\xi}{L}.$$"
    )


def T_greens_function_final() -> str:
    return (
        "La función de Green es por tanto la **tienda de campaña** "
        "(pieza-lineal, continua, con pico en $\\xi$):\n\n"
        "$$\\boxed{\\;G(x, \\xi) = \\begin{cases} "
        "\\dfrac{x(L - \\xi)}{L} & 0 \\leq x \\leq \\xi, \\\\[6pt] "
        "\\dfrac{\\xi(L - x)}{L} & \\xi \\leq x \\leq L. \\end{cases}\\;}$$\n\n"
        "Nótese la **simetría** $G(x, \\xi) = G(\\xi, x)$ (es una "
        "manifestación del **principio de reciprocidad**: la respuesta "
        "en $x$ a una fuente en $\\xi$ es igual a la respuesta en $\\xi$ "
        "a una fuente en $x$). Esta simetría se cumple para operadores "
        "autoadjuntos."
    )


def T_poisson_1d_physical_interpretation() -> str:
    return (
        "El método de la función de Green resuelve el problema "
        "**descomponiendo la fuente en deltas** y sumando las "
        "respuestas individuales. Cada elemento $f(\\xi)\\, d\\xi$ "
        "actúa como una fuente puntual de masa $f(\\xi)\\, d\\xi$ en "
        "$\\xi$, que produce el desplazamiento $G(x, \\xi)\\, f(\\xi)\\, d\\xi$ "
        "en el punto $x$.\n\n"
        "Esta misma estrategia se generaliza a 2D y 3D, con funciones de "
        "Green logarítmicas (Laplace 2D) o coulombianas (Laplace 3D); "
        "y a operadores con tiempo (calor, onda) usando funciones de "
        "Green retardadas que incorporan causalidad."
    )


# ===========================================================================
# HELMHOLTZ on rectangle (inhomogeneous, eigenfunction expansion)
# ===========================================================================

def T_statement_helmholtz_rect() -> str:
    return (
        "Resolvemos la **ecuación de Helmholtz** $\\Delta u + k^2 u = f$ "
        "en el rectángulo $[0, a] \\times [0, b]$ con $u = 0$ en toda "
        "la frontera. Físicamente: la **amplitud estacionaria** de una "
        "membrana rectangular forzada armónicamente a frecuencia $k$, "
        "o un problema acústico en una cavidad rectangular.\n\n"
        "Cuando $f \\equiv 0$ se reduce a un **problema de autovalores**: "
        "buscar los valores de $k^2$ para los que hay solución no "
        "trivial (los **modos normales** de la membrana). Cuando "
        "$f \\neq 0$, hay solución para cualquier $k^2$ **fuera** del "
        "espectro de autovalores; en resonancia ($k^2 = k_{mn}^2$) el "
        "problema es singular."
    )


def T_helmholtz_eigenpairs() -> str:
    return (
        "**Paso clave: identificar el espectro.** Las autofunciones del "
        "Laplaciano con Dirichlet 0 en el rectángulo son\n\n"
        "$$\\phi_{mn}(x, y) = \\sin\\!\\bigl(\\tfrac{m\\pi x}{a}\\bigr)"
        "\\sin\\!\\bigl(\\tfrac{n\\pi y}{b}\\bigr), \\quad m, n \\geq 1,$$\n\n"
        "con autovalores\n\n"
        "$$k_{mn}^2 = \\left(\\tfrac{m\\pi}{a}\\right)^2 "
        "+ \\left(\\tfrac{n\\pi}{b}\\right)^2.$$\n\n"
        "Se verifica: $\\Delta \\phi_{mn} = -k_{mn}^2 \\phi_{mn}$. "
        "Las $\\phi_{mn}$ forman base ortogonal de $L^2([0,a]\\times[0,b])$ "
        "(producto de dos bases SL unidimensionales)."
    )


def T_helmholtz_expansion() -> str:
    return (
        "**Expansión de la solución y de la fuente.** Escribimos\n\n"
        "$$u(x, y) = \\sum_{m, n \\geq 1} c_{mn}\\, \\phi_{mn}(x, y),"
        "\\qquad f(x, y) = \\sum_{m, n \\geq 1} f_{mn}\\, \\phi_{mn}(x, y).$$\n\n"
        "Aplicando $\\Delta + k^2$ a la primera serie:\n\n"
        "$$\\sum_{m,n} c_{mn}(k^2 - k_{mn}^2)\\, \\phi_{mn} = "
        "\\sum_{m,n} f_{mn}\\, \\phi_{mn}.$$\n\n"
        "Igualando coeficientes:\n\n"
        "$$c_{mn} = \\frac{f_{mn}}{k^2 - k_{mn}^2}, \\quad "
        "\\text{siempre que } k^2 \\notin \\{k_{mn}^2\\}.$$"
    )


def T_helmholtz_resonance() -> str:
    return (
        "**Resonancia.** Si $k^2$ coincide con algún autovalor "
        "$k_{m_0 n_0}^2$, el denominador $c_{m_0 n_0}$ explota: el "
        "problema no tiene solución acotada salvo que $f$ sea ortogonal "
        "a $\\phi_{m_0 n_0}$ (condición de **alternativa de Fredholm**). "
        "Físicamente: forzar la membrana a una frecuencia exactamente "
        "igual a uno de sus modos provoca crecimiento sin límite, como "
        "un columpio que se mece a su propia frecuencia natural."
    )


def T_helmholtz_physical_interpretation() -> str:
    return (
        "La solución es una **superposición ponderada de modos normales**, "
        "donde cada peso depende de qué tan cerca esté $k^2$ del autovalor "
        "correspondiente. Lejos de cualquier resonancia, todos los modos "
        "contribuyen modestamente. Cerca de una resonancia $k^2 \\approx "
        "k_{mn}^2$, ese modo domina enormemente: es el efecto de "
        "amplificación selectiva que explota cualquier instrumento "
        "musical o cavidad acústica."
    )


# ===========================================================================
# TELEGRAPH equation (damped wave)
# ===========================================================================

def T_statement_telegraph() -> str:
    return (
        "La **ecuación del telégrafo** "
        "$u_{tt} + 2\\alpha u_t + \\beta u = c^2 u_{xx}$ "
        "(con $\\alpha, \\beta \\geq 0$) modela la transmisión de "
        "señales en una línea de transmisión real, donde $u$ "
        "representa el voltaje (o la corriente). Los parámetros tienen "
        "interpretación física directa: $\\alpha$ es disipación "
        "(resistencia + fugas), $\\beta$ es \"masa efectiva\" "
        "(producto de la inductancia y la conductancia), y $c$ es la "
        "velocidad nominal de propagación.\n\n"
        "Es una **interpolación** entre la ecuación de onda "
        "($\\alpha = \\beta = 0$) y la del calor "
        "($\\beta \\to \\infty$ tras un reescalado). Heaviside la "
        "estudió para explicar por qué los telégrafos transatlánticos "
        "se distorsionaban menos de lo que se temía."
    )


def T_telegraph_temporal_ode() -> str:
    return (
        "Tras la separación de variables $u = X(x) T(t)$ y el "
        "análisis espacial usual (idéntico al del calor: $X_n = "
        "\\sin(n\\pi x/L)$, $\\lambda_n = (n\\pi/L)^2$), la EDO temporal es\n\n"
        "$$T_n'' + 2\\alpha\\, T_n' + (\\beta + c^2 \\lambda_n)\\, T_n = 0.$$\n\n"
        "Es una EDO lineal de segundo orden con coeficientes constantes. "
        "Su ecuación característica es\n\n"
        "$$r^2 + 2\\alpha\\, r + (\\beta + c^2 \\lambda_n) = 0,$$\n\n"
        "con raíces\n\n"
        "$$r_\\pm = -\\alpha \\pm \\sqrt{\\alpha^2 - \\beta - c^2 \\lambda_n}.$$\n\n"
        "El signo del **discriminante temporal** $\\Delta_n = "
        "\\alpha^2 - \\beta - c^2 \\lambda_n$ define **tres regímenes** "
        "físicamente distintos."
    )


def T_telegraph_three_regimes() -> str:
    return (
        "Para cada modo espacial $n$ tenemos uno de estos tres comportamientos:\n\n"
        "- **Sobreamortiguado ($\\Delta_n > 0$):** "
        "$T_n(t) = e^{-\\alpha t}(A_n e^{\\sqrt{\\Delta_n}\\, t} + "
        "B_n e^{-\\sqrt{\\Delta_n}\\, t})$. El modo decae sin oscilar.\n"
        "- **Críticamente amortiguado ($\\Delta_n = 0$):** "
        "$T_n(t) = e^{-\\alpha t}(A_n + B_n t)$. Decaimiento lo más rápido "
        "posible sin oscilar.\n"
        "- **Subamortiguado ($\\Delta_n < 0$):** "
        "$T_n(t) = e^{-\\alpha t}\\bigl[A_n \\cos(\\omega_n t) + "
        "B_n \\sin(\\omega_n t)\\bigr]$ con $\\omega_n = \\sqrt{-\\Delta_n}$. "
        "Oscila con frecuencia desplazada y amplitud decreciente.\n\n"
        "Para un modo dado, el régimen lo decide la magnitud relativa "
        "de la **disipación** $\\alpha$ frente a la **rigidez efectiva** "
        "$\\beta + c^2 \\lambda_n$. Los modos altos (grande $\\lambda_n$) "
        "tienden a estar subamortiguados (oscilan)."
    )


def T_telegraph_physical_interpretation() -> str:
    return (
        "La solución es una mezcla de **decaimiento** (factor $e^{-\\alpha t}$, "
        "común a todos los modos) y **oscilación** (modos subamortiguados). "
        "Lecturas físicas:\n\n"
        "- Si $\\alpha$ es **grande**, dominan los modos sobreamortiguados: "
        "comportamiento difusivo, parecido al calor.\n"
        "- Si $\\alpha$ es **pequeño** comparado con $c\\sqrt{\\lambda_n}$, "
        "el modo $n$ oscila a frecuencia $\\omega_n$ con amortiguamiento "
        "lento: comportamiento ondulatorio, parecido a la cuerda.\n"
        "- La **condición de Heaviside** $\\alpha^2 = \\beta$ (resistencia "
        "y fuga balanceadas) hace que $\\Delta_n = -c^2 \\lambda_n < 0$ "
        "para todo $n$: todos los modos oscilan con la **misma frecuencia "
        "espacial** desplazada, y la señal viaja sin distorsión, sólo "
        "atenuándose globalmente — el descubrimiento clave de Heaviside."
    )


# ===========================================================================
# SCHRÖDINGER — particle in an infinite 1D well
# ===========================================================================

def T_statement_schrodinger_well() -> str:
    return (
        "Resolvemos la **ecuación de Schrödinger dependiente del tiempo** "
        "para una partícula libre confinada en una caja unidimensional "
        "(pozo infinito) de longitud $L$:\n\n"
        "$$i\\hbar\\, \\psi_t = -\\frac{\\hbar^2}{2m}\\, \\psi_{xx},"
        "\\quad 0 < x < L,\\quad t > 0.$$\n\n"
        "Las paredes infinitas se traducen en condiciones de Dirichlet "
        "homogéneas $\\psi(0, t) = \\psi(L, t) = 0$ (la función de onda "
        "no puede penetrar las paredes). Iniciamos con un estado "
        "$\\psi(x, 0) = \\psi_0(x)$. La incógnita $\\psi$ es **compleja**: "
        "$|\\psi|^2$ es la densidad de probabilidad de hallar la "
        "partícula en $x$ al tiempo $t$."
    )


def T_schrodinger_method_choice() -> str:
    return (
        "La EDP es **lineal y homogénea** y las BCs son Dirichlet "
        "homogéneas en un intervalo finito. Separación de variables "
        "aplica directamente. La novedad respecto a heat/wave es que "
        "la **constante de separación** será **real** pero la EDO "
        "temporal involucra la **unidad imaginaria** $i$, así que las "
        "soluciones temporales son **rotaciones de fase** complejas, "
        "no decaimiento ni oscilación real."
    )


def T_schrodinger_separation() -> str:
    return (
        "Probamos $\\psi(x, t) = \\varphi(x)\\, T(t)$. Sustituyendo:\n\n"
        "$$i\\hbar\\, \\varphi(x)\\, T'(t) = -\\frac{\\hbar^2}{2m}\\, "
        "\\varphi''(x)\\, T(t).$$\n\n"
        "Dividiendo por $\\varphi(x) T(t)$, queda toda dependencia en $t$ "
        "a un lado y toda en $x$ al otro. Llamamos a la constante de "
        "separación **$E$** (anticipando su interpretación como energía):"
    )


def T_schrodinger_spatial_temporal() -> str:
    return (
        "El **lado izquierdo** (sólo en $t$) iguala $E$:\n\n"
        "$$i\\hbar\\, \\frac{T'(t)}{T(t)} = E \\Rightarrow "
        "T(t) = T_0\\, e^{-i E t / \\hbar}.$$\n\n"
        "El **lado derecho** (sólo en $x$) iguala $E$ también:\n\n"
        "$$-\\frac{\\hbar^2}{2m}\\, \\frac{\\varphi''(x)}{\\varphi(x)} = E "
        "\\Rightarrow \\varphi''(x) + \\frac{2mE}{\\hbar^2}\\, \\varphi(x) = 0.$$\n\n"
        "Esta es la **ecuación de Schrödinger independiente del tiempo**: "
        "un problema de Sturm-Liouville idéntico al del calor pero con "
        "$\\lambda = 2mE/\\hbar^2$ como autovalor."
    )


def T_schrodinger_eigenvalues() -> str:
    return (
        "Las BCs $\\varphi(0) = \\varphi(L) = 0$ fuerzan, repitiendo el "
        "análisis de los tres casos (idéntico al del calor), "
        "$\\sqrt{2mE/\\hbar^2}\\cdot L = n\\pi$. Despejando $E$:\n\n"
        "$$\\boxed{\\, E_n = \\frac{n^2 \\pi^2 \\hbar^2}{2 m L^2},\\quad "
        "\\varphi_n(x) = \\sqrt{\\tfrac{2}{L}}\\, \\sin\\!\\bigl(\\tfrac{n\\pi x}{L}\\bigr),"
        "\\quad n = 1, 2, 3, \\dots \\,}$$\n\n"
        "Estos son los **niveles de energía cuantizados** de la partícula "
        "en la caja: el resultado más icónico de la mecánica cuántica "
        "elemental. La cuantización aparece por las condiciones de "
        "contorno, **exactamente como los modos de una cuerda fija en "
        "ambos extremos**: la matemática es la misma; la diferencia es "
        "que aquí $E$ tiene unidades de energía y etiqueta estados, no "
        "frecuencias."
    )


def T_schrodinger_superposition() -> str:
    return (
        "La solución general es la **superposición** de los estados "
        "estacionarios $\\varphi_n e^{-i E_n t / \\hbar}$:\n\n"
        "$$\\psi(x, t) = \\sum_{n=1}^{\\infty} c_n\\, \\varphi_n(x)\\, "
        "e^{-i E_n t / \\hbar}.$$\n\n"
        "Los coeficientes $c_n$ son complejos en general. Al aplicar "
        "$\\psi(x, 0) = \\psi_0(x)$ y usar la ortonormalidad de "
        "$\\{\\varphi_n\\}$:\n\n"
        "$$c_n = \\int_0^L \\varphi_n(x)\\, \\psi_0(x)\\, dx.$$"
    )


def T_schrodinger_physical_interpretation() -> str:
    return (
        "La función de onda $\\psi(x, t)$ no es directamente observable; "
        "lo es **$|\\psi(x, t)|^2$**, la densidad de probabilidad. "
        "Observaciones físicas clave:\n\n"
        "- **Estados estacionarios.** Si $\\psi_0 = \\varphi_n$, entonces "
        "$\\psi(x, t) = \\varphi_n(x)\\, e^{-i E_n t / \\hbar}$ y "
        "$|\\psi|^2 = |\\varphi_n|^2$ **no depende del tiempo**.\n"
        "- **Cuantización.** Las energías $E_n$ forman un conjunto "
        "**discreto**. No hay continuo de niveles permitidos: ése es "
        "el descubrimiento revolucionario de la mecánica cuántica.\n"
        "- **Energía del estado fundamental.** $E_1 = \\pi^2 \\hbar^2 / (2mL^2) > 0$. "
        "**No hay estado de energía cero.** Una consecuencia del "
        "principio de indeterminación: confinar la partícula obliga a "
        "que tenga energía cinética mínima.\n"
        "- **Espacios entre niveles.** $E_{n+1} - E_n = (2n+1)\\pi^2 \\hbar^2 / (2mL^2)$ "
        "crece linealmente con $n$. Pozos más pequeños o partículas "
        "más ligeras dan espacios más grandes (efectos cuánticos más "
        "visibles)."
    )


# ===========================================================================
# CHARACTERISTICS — first-order transport
# ===========================================================================

def T_statement_characteristics() -> str:
    return (
        "Resolvemos la **ecuación de transporte 1D**\n\n"
        "$$u_t + c\\, u_x = 0, \\quad x \\in \\mathbb{R},\\ t > 0,\\qquad "
        "u(x, 0) = u_0(x).$$\n\n"
        "Es la EDP de primer orden más sencilla. Físicamente: una "
        "concentración $u$ que se transporta por un flujo a velocidad "
        "constante $c$, sin difusión ni reacción. Aunque sea simple, "
        "es el **modelo de juguete** que introduce el método de las "
        "**características**, técnica fundamental para EDPs hiperbólicas "
        "de primer orden (incluida la ecuación de Burgers no lineal y "
        "la dinámica de fluidos compresibles)."
    )


def T_characteristics_method_motivation() -> str:
    return (
        "**Idea geométrica.** Pensamos en $u(x, t)$ como una función "
        "definida en el plano $(x, t)$ y buscamos **curvas** a lo largo "
        "de las cuales $u$ sea **constante**. Si encontramos tales "
        "curvas, conocer $u$ en un punto basta para conocerlo en toda "
        "la curva.\n\n"
        "A lo largo de una curva $x = x(t)$, por la regla de la cadena:\n\n"
        "$$\\frac{du}{dt} = u_t + u_x\\, \\frac{dx}{dt}.$$\n\n"
        "Comparando con $u_t + c\\, u_x = 0$, vemos que $u$ es constante "
        "a lo largo de curvas con $dx/dt = c$. Esas son rectas "
        "$x = ct + \\text{cte}$, llamadas **rectas características**."
    )


def T_characteristics_solve() -> str:
    return (
        "**Resolución.** A cada característica le asignamos su parámetro "
        "$\\xi = x - ct$ (el punto donde la característica corta el eje "
        "$t = 0$). Como $u$ es constante a lo largo de cada característica:\n\n"
        "$$u(x, t) = u(\\xi, 0) = u_0(\\xi) = u_0(x - ct).$$\n\n"
        "Es decir, **la solución es el perfil inicial trasladado a "
        "velocidad $c$**, sin deformación."
    )


def T_characteristics_physical_interpretation() -> str:
    return (
        "Tres lecturas inmediatas:\n\n"
        "- **Propagación sin distorsión.** El perfil $u_0$ viaja "
        "rígidamente. Esto contrasta con la ecuación del calor "
        "(difunde, suaviza) y con Burgers (se deforma y puede formar "
        "choques).\n"
        "- **Sin condiciones de contorno.** Como la EDP es de primer "
        "orden, basta con la condición inicial. En la línea infinita "
        "no hay otras condiciones que imponer.\n"
        "- **Generalización.** Para $u_t + c(x, t)\\, u_x = f(x, t, u)$, "
        "las características dejan de ser rectas y $u$ ya no es "
        "constante a lo largo de ellas, pero el método sigue: se "
        "resuelve una EDO a lo largo de cada característica. Es la "
        "puerta de entrada al análisis de leyes de conservación y "
        "dinámica de gases."
    )


# ===========================================================================
# BIHARMONIC — beam deflection (1D fourth-order)
# ===========================================================================

def T_statement_biharmonic_beam() -> str:
    return (
        "Resolvemos la **ecuación de la viga simplemente apoyada**:\n\n"
        "$$EI\\, u''''(x) = q(x), \\quad 0 < x < L,$$\n\n"
        "con $u$ el desplazamiento transversal, $q(x)$ la carga "
        "distribuida, y $EI$ la rigidez a flexión. Las condiciones de "
        "**apoyo simple** en ambos extremos son\n\n"
        "$$u(0) = u(L) = 0 \\quad \\text{(sin deflexión)}, \\qquad "
        "u''(0) = u''(L) = 0 \\quad \\text{(sin momento flector)}.$$\n\n"
        "Es una EDO de **cuarto orden**, así que necesitamos **cuatro** "
        "condiciones, dos en cada extremo."
    )


def T_biharmonic_method_choice() -> str:
    return (
        "Como las cuatro condiciones de apoyo simple son compatibles "
        "con la base $\\sin(n\\pi x/L)$ — cada seno satisface las cuatro "
        "automáticamente — usamos **expansión en serie de senos**. Para "
        "BCs distintas se necesitaría una base diferente (la teoría de "
        "Sturm-Liouville de cuarto orden la provee).\n\n"
        "**Verificación cosmética:** $\\sin(n\\pi x/L)$ se anula en "
        "$0$ y en $L$, y su segunda derivada $-(n\\pi/L)^2 \\sin(n\\pi x/L)$ "
        "también. Las cuatro BCs se satisfacen por construcción."
    )


def T_biharmonic_expansion() -> str:
    return (
        "Expandimos $u$ y $q$ en serie de senos:\n\n"
        "$$u(x) = \\sum_{n=1}^{\\infty} A_n \\sin\\!\\bigl(\\tfrac{n\\pi x}{L}\\bigr),"
        "\\qquad q(x) = \\sum_{n=1}^{\\infty} q_n \\sin\\!\\bigl(\\tfrac{n\\pi x}{L}\\bigr).$$\n\n"
        "Al sustituir en $EI\\, u'''' = q$ y observando que "
        "$d^4/dx^4 \\sin(n\\pi x/L) = (n\\pi/L)^4 \\sin(n\\pi x/L)$, "
        "igualamos coeficientes término a término:\n\n"
        "$$EI\\, \\left(\\tfrac{n\\pi}{L}\\right)^4 A_n = q_n "
        "\\Rightarrow A_n = \\frac{q_n}{EI\\, (n\\pi/L)^4}.$$"
    )


def T_biharmonic_physical_interpretation() -> str:
    return (
        "Lecturas físicas:\n\n"
        "- **Atenuación de modos altos.** El factor $1/(n\\pi/L)^4$ es "
        "**muy pequeño** para $n$ grande: una carga oscilatoria de "
        "frecuencia espacial alta produce una deflexión minúscula. Por "
        "eso las vigas filtran muy bien las vibraciones de alta "
        "frecuencia.\n"
        "- **Modo dominante.** Para una carga uniforme o concentrada en "
        "el centro, $q_1$ domina: la deflexión se parece mucho a "
        "$\\sin(\\pi x/L)$ con máximo en el centro.\n"
        "- **Comparación con la cuerda.** Las EDOs son distintas "
        "(cuarto orden vs segundo) pero las **autofunciones son las "
        "mismas**: las simetrías del intervalo finito con BCs "
        "compatibles fuerzan la base trigonométrica."
    )


# ===========================================================================
# METHOD OF IMAGES — Laplace in half-plane
# ===========================================================================

def T_statement_images_halfplane() -> str:
    return (
        "Resolvemos el problema de Dirichlet en el **semiplano superior**:\n\n"
        "$$\\Delta u = 0, \\quad y > 0,\\quad u(x, 0) = f(x),$$\n\n"
        "con la condición adicional de **decaimiento al infinito**.\n\n"
        "Físicamente: el potencial electrostático en una región limitada "
        "por un conductor a tierra ($u = 0$) con un dato $f$ aplicado en "
        "la pared; o la temperatura estacionaria de un semiplano con "
        "una distribución de temperatura prescrita en el borde."
    )


def T_images_method_motivation() -> str:
    return (
        "**Idea del método.** Construimos primero la **función de Green** "
        "del semiplano, $G(\\mathbf{r}; \\mathbf{r}')$, que resuelve\n\n"
        "$$-\\Delta G = \\delta(\\mathbf{r} - \\mathbf{r}'), "
        "\\quad G\\bigr|_{y=0} = 0.$$\n\n"
        "Sin la condición de frontera, la solución fundamental del "
        "Laplaciano 2D es $\\Phi(\\mathbf{r}) = -\\tfrac{1}{2\\pi} "
        "\\ln|\\mathbf{r}|$. Para imponer $G\\bigr|_{y = 0} = 0$ usamos "
        "un **truco geométrico**: colocar una **imagen especular** del "
        "punto fuente $(x', y')$ del otro lado del muro, en $(x', -y')$, "
        "con signo opuesto. La superposición se anula en el muro por "
        "simetría."
    )


def T_images_green_construction() -> str:
    return (
        "Definimos\n\n"
        "$$G(x, y; x', y') = -\\tfrac{1}{2\\pi} \\ln\\sqrt{(x - x')^2 + (y - y')^2} "
        "+ \\tfrac{1}{2\\pi} \\ln\\sqrt{(x - x')^2 + (y + y')^2}.$$\n\n"
        "**Verificación de las propiedades:**\n\n"
        "- $-\\Delta G = \\delta$ en $y > 0$: el segundo término es "
        "armónico en $y > 0$ (su singularidad está en $y = -y' < 0$, "
        "fuera del semiplano), así que sólo el primer término aporta "
        "el delta.\n"
        "- En $y = 0$: las dos distancias coinciden "
        "($\\sqrt{(x-x')^2 + y'^2}$ en ambos términos), los logaritmos "
        "se cancelan exactamente, y $G = 0$. ✓"
    )


def T_images_poisson_kernel() -> str:
    return (
        "**Solución para datos en la frontera.** Para resolver "
        "$\\Delta u = 0$ con $u(x, 0) = f(x)$, usamos la **fórmula de "
        "representación de Green**\n\n"
        "$$u(x, y) = -\\int_{-\\infty}^{\\infty} f(x')\\, "
        "\\left.\\frac{\\partial G}{\\partial y'}\\right|_{y' = 0}\\, dx'.$$\n\n"
        "Calculando la derivada normal de $G$ en $y' = 0$ llegamos al "
        "**núcleo de Poisson del semiplano**:\n\n"
        "$$P(x - x', y) = \\frac{1}{\\pi}\\, \\frac{y}{(x - x')^2 + y^2}.$$\n\n"
        "Es un perfil **lorentziano** centrado en $x'$, con anchura "
        "proporcional a $y$."
    )


def T_images_solution_formula() -> str:
    return (
        "**Fórmula final (Poisson para el semiplano):**\n\n"
        "$$\\boxed{\\, u(x, y) = \\frac{y}{\\pi}\\, "
        "\\int_{-\\infty}^{\\infty} \\frac{f(x')}{(x - x')^2 + y^2}\\, dx' \\,}$$"
    )


def T_images_physical_interpretation() -> str:
    return (
        "Tres lecturas:\n\n"
        "- **Ventana de Poisson.** Cada punto $(x, y)$ promedia el "
        "dato $f$ con peso $y / ((x - x')^2 + y^2)$, una **lorentziana** "
        "de anchura $\\sim y$. Lejos del muro promediamos mucho (la "
        "solución se suaviza); cerca del muro la ventana es estrecha y "
        "preservamos los detalles de $f$.\n"
        "- **Promedio total.** $\\int_{-\\infty}^\\infty P(s, y)\\, ds = 1$ "
        "para todo $y > 0$: el núcleo es una **densidad de "
        "probabilidad** y el método respeta promedios.\n"
        "- **Generalización.** El método de imágenes funciona en "
        "dominios con simetría especular: cuña (con varias imágenes), "
        "tira semi-infinita (imágenes periódicas), o disco (con la "
        "transformación de inversión $r \\mapsto R^2/r$)."
    )


# ===========================================================================
# WAVE / HEAT on a disk — Bessel-Fourier
# ===========================================================================

def T_statement_wave_disk() -> str:
    return (
        "Resolvemos la **ecuación de onda en un disco** (membrana "
        "elástica circular, p. ej. un tambor) de radio $R$, fija en su "
        "borde:\n\n"
        "$$u_{tt} = c^2\\, \\Delta u, \\quad r < R,\\ t > 0, \\qquad "
        "u(R, t) = 0.$$\n\n"
        "Para mantener la pedagogía limpia consideramos el caso "
        "**axialmente simétrico** (la membrana se golpea con un perfil "
        "que sólo depende de $r$, no de $\\theta$). El Laplaciano "
        "radial en polares es entonces $\\Delta u = u_{rr} + u_r/r$. "
        "Necesitamos dos condiciones iniciales: posición y velocidad."
    )


def T_statement_heat_disk() -> str:
    return (
        "Resolvemos la **ecuación del calor en un disco** circular de "
        "radio $R$ con frontera a temperatura cero, en el caso "
        "**axialmente simétrico** (datos iniciales que sólo dependen "
        "del radio):\n\n"
        "$$u_t = \\alpha^2 \\bigl(u_{rr} + u_r/r\\bigr), \\quad r < R,\\ "
        "t > 0,\\qquad u(R, t) = 0,\\quad u(r, 0) = f(r).$$\n\n"
        "El Laplaciano radial en polares incluye el término "
        "$u_r/r$ — la curvatura geométrica del sistema de coordenadas. "
        "Esa es la única diferencia con el problema del calor 1D, "
        "pero basta para hacer que la solución natural se exprese en "
        "**funciones de Bessel** en vez de senos."
    )


def T_bessel_method_choice() -> str:
    return (
        "**Separación de variables en polares.** Probamos "
        "$u(r, t) = R(r)\\, T(t)$. Sustituyendo en la EDP y dividiendo "
        "por $\\alpha^2 R T$ (heat) o $c^2 R T$ (onda), las dos "
        "dependencias se separan. Como antes, llamamos $-\\lambda$ a "
        "la constante de separación:"
    )


def T_bessel_radial_ode() -> str:
    return (
        "La EDO radial es:\n\n"
        "$$R'' + \\frac{R'}{r} + \\lambda R = 0.$$\n\n"
        "Multiplicando por $r^2$ y haciendo el cambio $s = \\sqrt{\\lambda}\\, r$ "
        "(asumiendo $\\lambda > 0$, que justificaremos pronto), la "
        "EDO se convierte en la **ecuación de Bessel de orden cero**:\n\n"
        "$$s^2 \\tilde R''(s) + s \\tilde R'(s) + s^2 \\tilde R(s) = 0,$$\n\n"
        "cuyas dos soluciones independientes son las **funciones de "
        "Bessel** $J_0(s)$ (regular en el origen) y $Y_0(s)$ "
        "(logarítmicamente divergente en $s = 0$). En un disco sólido "
        "**descartamos $Y_0$** por la condición de regularidad en "
        "$r = 0$. Queda $R(r) = J_0(\\sqrt{\\lambda}\\, r)$ salvo "
        "escala."
    )


def T_bessel_eigenvalues() -> str:
    return (
        "Aplicamos la BC $R(R) = 0$, es decir $J_0(\\sqrt{\\lambda}\\, R) = 0$. "
        "Esto fuerza a que $\\sqrt{\\lambda}\\, R$ sea **un cero "
        "positivo de $J_0$**. Los ceros de $J_0$ forman una sucesión "
        "creciente $\\mu_1 < \\mu_2 < \\mu_3 < \\dots \\to \\infty$ "
        "(numéricamente $\\mu_1 \\approx 2.405$, $\\mu_2 \\approx 5.520$, …) "
        "y producen los autovalores y las autofunciones:\n\n"
        "$$\\lambda_n = \\left(\\tfrac{\\mu_n}{R}\\right)^2, \\qquad "
        "R_n(r) = J_0\\!\\bigl(\\tfrac{\\mu_n r}{R}\\bigr), "
        "\\quad n = 1, 2, 3, \\dots$$\n\n"
        "Las $R_n$ son **ortogonales con peso $r$** sobre $[0, R]$ "
        "(no con peso $1$, ¡atención!): "
        "$\\int_0^R r\\, J_0(\\mu_m r/R)\\, J_0(\\mu_n r/R)\\, dr = "
        "\\tfrac{R^2}{2} [J_1(\\mu_n)]^2\\, \\delta_{nm}$. El peso $r$ "
        "viene del **elemento de área** $dA = r\\, dr\\, d\\theta$."
    )


def T_bessel_temporal_wave() -> str:
    return (
        "La EDO temporal $T_n'' + c^2 \\lambda_n T_n = 0$ es la del "
        "oscilador armónico simple, con frecuencia "
        "$\\omega_n = c \\sqrt{\\lambda_n} = c \\mu_n / R$:\n\n"
        "$$T_n(t) = A_n \\cos(\\omega_n t) + B_n \\sin(\\omega_n t).$$\n\n"
        "**Aquí está la diferencia clave con la cuerda 1D:** los "
        "modos del tambor tienen frecuencias $\\omega_n \\propto \\mu_n$, "
        "y los ceros de $J_0$ **no están en proporción entera entre sí** "
        "($\\mu_2/\\mu_1 \\approx 2.295$, no 2). Por eso un tambor no "
        "produce notas musicales claras como una cuerda: sus armónicos "
        "son **inarmónicos**."
    )


def T_bessel_temporal_heat() -> str:
    return (
        "La EDO temporal $T_n' + \\alpha^2 \\lambda_n T_n = 0$ es de "
        "primer orden, con decaimiento exponencial:\n\n"
        "$$T_n(t) = C_n\\, e^{-\\alpha^2 \\lambda_n t} = "
        "C_n\\, e^{-\\alpha^2 (\\mu_n / R)^2 t}.$$\n\n"
        "El primer modo $J_0(\\mu_1 r/R)$ tiene la constante de tiempo "
        "más larga ($\\tau_1 = R^2 / (\\alpha^2 \\mu_1^2)$); los modos "
        "altos decaen rápidamente porque $\\mu_n^2$ crece "
        "**cuadráticamente** con $n$ (a diferencia de la cuerda, donde "
        "crecía como $n^2 \\pi^2$, pero la idea es la misma)."
    )


def T_bessel_coefficients() -> str:
    return (
        "Para extraer los coeficientes de la expansión, "
        "$f(r) = \\sum_n B_n J_0(\\mu_n r/R)$ (o, para la onda, las "
        "fórmulas análogas con $A_n$ y $B_n$), usamos la ortogonalidad "
        "**con peso $r$**:\n\n"
        "$$B_n = \\frac{2}{R^2\\, [J_1(\\mu_n)]^2} \\int_0^R r\\, f(r)\\, "
        "J_0\\!\\bigl(\\tfrac{\\mu_n r}{R}\\bigr)\\, dr.$$\n\n"
        "El factor $[J_1(\\mu_n)]^2$ viene de la **fórmula de Lommel** "
        "que da la norma de las autofunciones radiales."
    )


def T_bessel_physical_interpretation_wave() -> str:
    return (
        "Lecturas físicas del tambor circular:\n\n"
        "- **Frecuencias inarmónicas.** $\\omega_n / \\omega_1 = "
        "\\mu_n / \\mu_1$ son números **irracionales no enteros**: "
        "$\\mu_2/\\mu_1 \\approx 2.295$, $\\mu_3/\\mu_1 \\approx 3.598$, …. "
        "Por eso un tambor suena \"a percusión\", no a nota. La cuerda, "
        "en cambio, tiene $\\omega_n/\\omega_1 = n$ exacto.\n"
        "- **Modos angulares.** Si admitimos perfiles iniciales no "
        "axisimétricos, aparecen modos con $J_m(\\mu_{m,n} r/R)$ y "
        "factor $\\cos(m\\theta)$ o $\\sin(m\\theta)$. Sus "
        "**líneas nodales** son círculos concéntricos y diámetros "
        "respectivamente — los famosos patrones de Chladni circulares.\n"
        "- **Velocidad efectiva.** En el modo $n$, los nodos se "
        "mueven a velocidad de fase $c$; el modo no \"viaja\" "
        "(la onda es estacionaria), pero la frecuencia revela $c$."
    )


def T_bessel_physical_interpretation_heat() -> str:
    return (
        "Lecturas físicas:\n\n"
        "- **Decaimiento del modo fundamental.** El modo $J_0(\\mu_1 r/R)$ "
        "domina a tiempos largos: $\\mu_1 \\approx 2.405$, "
        "$\\lambda_1 = (\\mu_1/R)^2 \\approx 5.78/R^2$. Es la **temperatura "
        "característica** del disco con extremos a cero.\n"
        "- **Comparación con el calor 1D.** En 1D, $\\lambda_1 = \\pi^2/L^2 "
        "\\approx 9.87/L^2$. El disco se enfría algo más lento que una "
        "barra del mismo \"radio\" porque la geometría circular "
        "atrapa el calor en el centro un poco más.\n"
        "- **Validez del ansatz axisimétrico.** Sólo si los datos "
        "iniciales son axisimétricos. Para datos generales se "
        "necesitan los modos con $m \\geq 1$."
    )


# ===========================================================================
# LAPLACE in a 3D ball — axisymmetric Dirichlet, Legendre expansion
# ===========================================================================

def T_statement_laplace_ball() -> str:
    return (
        "Resolvemos la **ecuación de Laplace en una bola** de radio "
        "$R$, con dato Dirichlet en la esfera que depende sólo de la "
        "**colatitud** $\\theta$ (no del ángulo azimutal $\\phi$):\n\n"
        "$$\\Delta u = 0, \\quad r < R, \\qquad u(R, \\theta) = f(\\theta).$$\n\n"
        "El caso **axisimétrico** (sin dependencia de $\\phi$) lo "
        "elegimos por claridad pedagógica: la expansión natural usa "
        "**polinomios de Legendre** $P_\\ell(\\cos\\theta)$ en lugar de "
        "los armónicos esféricos completos $Y_\\ell^m(\\theta, \\phi)$. "
        "El caso general es una generalización directa que mencionamos "
        "al final."
    )


def T_laplace_ball_method_choice() -> str:
    return (
        "Separamos $u(r, \\theta) = R(r)\\, \\Theta(\\theta)$. El "
        "Laplaciano en esféricas (sin $\\phi$) es:\n\n"
        "$$\\Delta u = \\frac{1}{r^2}(r^2 u_r)_r "
        "+ \\frac{1}{r^2 \\sin\\theta}(\\sin\\theta\\, u_\\theta)_\\theta.$$\n\n"
        "Sustituyendo y multiplicando por $r^2/(R\\Theta)$, separamos "
        "en una EDO radial y una angular, con constante $\\ell(\\ell + 1)$ "
        "(la elección de esta forma se justificará en el paso "
        "angular: es la única que da soluciones polinómicas regulares)."
    )


def T_laplace_ball_angular() -> str:
    return (
        "La EDO angular, con el cambio $\\xi = \\cos\\theta$ "
        "(transforma $\\sin\\theta\\, d\\theta$ en $-d\\xi$), se convierte "
        "en la **ecuación de Legendre**:\n\n"
        "$$\\bigl[(1 - \\xi^2)\\, \\Theta'(\\xi)\\bigr]' + \\ell(\\ell + 1)\\, "
        "\\Theta(\\xi) = 0.$$\n\n"
        "Para que $\\Theta$ sea **regular** en $\\xi = \\pm 1$ "
        "($\\theta = 0, \\pi$: los polos norte y sur), $\\ell$ debe ser "
        "un **entero no negativo**. Las soluciones regulares son los "
        "**polinomios de Legendre** $P_\\ell(\\xi) = P_\\ell(\\cos\\theta)$, "
        "que forman una base ortogonal de $L^2([-1, 1])$:\n\n"
        "$$\\int_{-1}^{1} P_\\ell(\\xi)\\, P_{\\ell'}(\\xi)\\, d\\xi "
        "= \\tfrac{2}{2\\ell + 1}\\, \\delta_{\\ell \\ell'}.$$"
    )


def T_laplace_ball_radial() -> str:
    return (
        "La EDO radial es una **ecuación de Euler**:\n\n"
        "$$r^2 R'' + 2 r R' - \\ell(\\ell + 1)\\, R = 0.$$\n\n"
        "Probando $R = r^p$: $p(p-1) + 2p - \\ell(\\ell + 1) = 0$, "
        "que se factoriza como $(p - \\ell)(p + \\ell + 1) = 0$. "
        "Soluciones $R = r^\\ell$ y $R = r^{-\\ell - 1}$.\n\n"
        "En una **bola sólida** descartamos $r^{-\\ell - 1}$ (diverge "
        "en el origen). Queda $R(r) = r^\\ell$ salvo escala. La "
        "solución general toma la forma\n\n"
        "$$u(r, \\theta) = \\sum_{\\ell = 0}^{\\infty} A_\\ell\\, r^\\ell\\, "
        "P_\\ell(\\cos\\theta).$$"
    )


def T_laplace_ball_coefficients() -> str:
    return (
        "Aplicamos la BC $u(R, \\theta) = f(\\theta)$. La serie en "
        "$r = R$ es la expansión de $f$ en polinomios de Legendre:\n\n"
        "$$f(\\theta) = \\sum_{\\ell} A_\\ell\\, R^\\ell\\, "
        "P_\\ell(\\cos\\theta).$$\n\n"
        "Por la ortogonalidad de los $P_\\ell$:\n\n"
        "$$A_\\ell = \\frac{2\\ell + 1}{2 R^\\ell} \\int_{-1}^{1} "
        "f(\\theta(\\xi))\\, P_\\ell(\\xi)\\, d\\xi = "
        "\\frac{2\\ell + 1}{2 R^\\ell} \\int_0^\\pi f(\\theta)\\, "
        "P_\\ell(\\cos\\theta)\\, \\sin\\theta\\, d\\theta.$$"
    )


def T_laplace_ball_physical_interpretation() -> str:
    return (
        "Tres lecturas:\n\n"
        "- **Expansión multipolar.** Los términos $r^\\ell P_\\ell$ "
        "son los **multipolos** del electromagnetismo y la "
        "gravitación: $\\ell = 0$ es la **monopolo** (carga total), "
        "$\\ell = 1$ es el **dipolo**, $\\ell = 2$ el **cuadrupolo**, …. "
        "Una carga puntual fuera de la bola genera precisamente esta "
        "serie como su potencial restringido a la bola.\n"
        "- **Promedio esférico.** El término $\\ell = 0$ es "
        "$A_0 = \\tfrac{1}{2}\\int_0^\\pi f \\sin\\theta\\, d\\theta$, "
        "el promedio de $f$ sobre la esfera. En $r = 0$: "
        "$u(0) = A_0$, el **teorema del valor medio** para funciones "
        "armónicas en 3D.\n"
        "- **Generalización (no axisimétrico).** Con dependencia en "
        "$\\phi$ las autofunciones son los **armónicos esféricos** "
        "$Y_\\ell^m(\\theta, \\phi)$, con $-\\ell \\leq m \\leq \\ell$. "
        "La solución es $u = \\sum_{\\ell, m} A_{\\ell m}\\, r^\\ell\\, "
        "Y_\\ell^m(\\theta, \\phi)$ con $A_{\\ell m}$ dado por "
        "integrales sobre la esfera completa."
    )


# ===========================================================================
# SCHRÖDINGER — quantum harmonic oscillator (V = ½ m ω² x²)
# ===========================================================================

def T_statement_schrodinger_oscillator() -> str:
    return (
        "Resolvemos la **ecuación de Schrödinger con potencial armónico**:\n\n"
        "$$i\\hbar\\, \\psi_t = -\\frac{\\hbar^2}{2m}\\, \\psi_{xx} + "
        "\\tfrac{1}{2} m \\omega^2 x^2\\, \\psi, \\quad x \\in \\mathbb{R},\\ t > 0.$$\n\n"
        "Es el modelo más estudiado de la mecánica cuántica: una partícula "
        "atrapada en un pozo parabólico de frecuencia clásica $\\omega$. "
        "Aparece como **aproximación de bajo orden** alrededor del mínimo "
        "de cualquier potencial suave, así que su espectro y autofunciones "
        "describen el comportamiento universal cerca del equilibrio (vibraciones "
        "moleculares, modos del campo electromagnético cuantizado, fonones, …).\n\n"
        "Como en el pozo infinito, la incógnita $\\psi$ es **compleja** y "
        "lo observable es $|\\psi|^2$. A diferencia del pozo, ahora **no hay "
        "paredes**: las condiciones de contorno son que $\\psi \\to 0$ "
        "cuando $|x| \\to \\infty$ (la partícula está confinada por el "
        "potencial, no por una caja)."
    )


def T_oscillator_method_choice() -> str:
    return (
        "**Separación de variables** funciona porque la EDP es lineal y la "
        "dependencia temporal está desacoplada: $\\psi(x, t) = \\varphi(x) "
        "T(t)$. La novedad respecto al pozo infinito es que la "
        "ecuación espacial pasa a tener un coeficiente que **depende de "
        "$x$** ($\\tfrac{1}{2} m \\omega^2 x^2$), lo que la convierte en un "
        "problema de Sturm-Liouville más rico — uno cuyas autofunciones "
        "son **polinomios de Hermite** multiplicados por una gaussiana, "
        "y cuyos autovalores son los famosos niveles de energía "
        "equiespaciados $E_n = \\hbar\\omega(n + 1/2)$."
    )


def T_oscillator_separation() -> str:
    return (
        "Probamos $\\psi(x, t) = \\varphi(x)\\, T(t)$ y sustituimos:\n\n"
        "$$i\\hbar\\, \\varphi(x)\\, T'(t) = "
        "\\left[-\\frac{\\hbar^2}{2m}\\, \\varphi''(x) + "
        "\\tfrac{1}{2} m \\omega^2 x^2 \\varphi(x)\\right]\\, T(t).$$\n\n"
        "Dividiendo por $\\varphi(x) T(t)$ separamos: el lado izquierdo "
        "depende sólo de $t$, el derecho sólo de $x$. Llamamos $E$ a "
        "la constante de separación (anticipando su interpretación "
        "física como energía):"
    )


def T_oscillator_tise() -> str:
    return (
        "La **EDO temporal** es de primer orden con coeficiente imaginario, "
        "idéntica al caso del pozo:\n\n"
        "$$T(t) = T_0\\, e^{-i E t / \\hbar}.$$\n\n"
        "La **ecuación de Schrödinger independiente del tiempo (TISE)** es:\n\n"
        "$$-\\frac{\\hbar^2}{2m}\\, \\varphi''(x) + "
        "\\tfrac{1}{2} m \\omega^2 x^2 \\varphi(x) = E\\, \\varphi(x).$$\n\n"
        "Este es el corazón pedagógico del problema. A diferencia del pozo "
        "(donde la TISE era $\\varphi'' + k^2 \\varphi = 0$ con $k$ constante), "
        "ahora el coeficiente de $\\varphi$ depende de $x$. Toca un cambio "
        "de variable para limpiar las constantes."
    )


def T_oscillator_dimensionless() -> str:
    return (
        "**Adimensionalizamos.** Definimos la longitud característica del "
        "oscilador $\\ell = \\sqrt{\\hbar / (m\\omega)}$ y la variable "
        "$\\xi = x / \\ell = \\sqrt{m\\omega/\\hbar}\\, x$. Con el cambio "
        "$\\varepsilon = 2E/(\\hbar\\omega)$ la TISE queda:\n\n"
        "$$\\varphi''(\\xi) + (\\varepsilon - \\xi^2)\\, \\varphi(\\xi) = 0.$$\n\n"
        "Hemos absorbido todas las constantes dimensionales en $\\ell$ y "
        "$\\varepsilon$. Lo que queda es la **ecuación de Hermite-Weber**, "
        "una EDO clásica cuyas soluciones físicamente aceptables (las que "
        "decaen al infinito) están parametrizadas por un entero $n \\geq 0$."
    )


def T_oscillator_asymptotic_and_hermite() -> str:
    return (
        "**Análisis asintótico.** Para $|\\xi| \\to \\infty$ el término "
        "$\\varepsilon$ es despreciable frente a $\\xi^2$, y la EDO se "
        "comporta como $\\varphi'' \\approx \\xi^2 \\varphi$. Las dos "
        "soluciones asintóticas son $\\varphi \\sim e^{\\pm \\xi^2/2}$. "
        "La condición de normalización ($\\int |\\varphi|^2 < \\infty$) "
        "descarta la creciente; queda la **gaussiana decreciente** "
        "$\\varphi \\sim e^{-\\xi^2/2}$.\n\n"
        "**Ansatz.** Buscamos $\\varphi(\\xi) = H(\\xi)\\, e^{-\\xi^2/2}$ "
        "con $H$ polinómica. Sustituyendo en la EDO y usando que "
        "$(He^{-\\xi^2/2})'' = (H'' - 2\\xi H' + (\\xi^2 - 1) H)\\, e^{-\\xi^2/2}$:\n\n"
        "$$H''(\\xi) - 2\\xi H'(\\xi) + (\\varepsilon - 1)\\, H(\\xi) = 0.$$\n\n"
        "Esta es la **ecuación de Hermite**. La condición de que $H$ sea "
        "polinómica (y por tanto $\\varphi$ normalizable) **cuantiza $\\varepsilon$**: "
        "sólo $\\varepsilon = 2n + 1$ con $n \\in \\{0, 1, 2, \\dots\\}$ da "
        "soluciones que terminan en grado finito."
    )


def T_oscillator_eigenvalues() -> str:
    return (
        "Despejando $E$ de $\\varepsilon = 2n + 1 = 2E/(\\hbar\\omega)$:\n\n"
        "$$\\boxed{\\;E_n = \\hbar\\omega\\!\\left(n + \\tfrac{1}{2}\\right),"
        "\\quad n = 0, 1, 2, \\dots\\;}$$\n\n"
        "Y las autofunciones, normalizadas en $L^2(\\mathbb{R})$:\n\n"
        "$$\\varphi_n(x) = \\sqrt{\\frac{\\alpha}{2^n\\, n!\\, \\sqrt{\\pi}}}\\, "
        "H_n(\\alpha x)\\, e^{-\\alpha^2 x^2 / 2},\\quad "
        "\\alpha = \\sqrt{m\\omega/\\hbar},$$\n\n"
        "donde $H_n$ es el **polinomio de Hermite físico** "
        "($H_0 = 1$, $H_1 = 2\\xi$, $H_2 = 4\\xi^2 - 2$, $H_3 = 8\\xi^3 - 12\\xi$, …). "
        "La constante de normalización viene de la integral de Hermite "
        "$\\int H_n(\\xi)^2\\, e^{-\\xi^2}\\, d\\xi = 2^n n! \\sqrt{\\pi}$."
    )


def T_oscillator_ground_state_energy() -> str:
    return (
        "**Energía del estado fundamental: $E_0 = \\tfrac{1}{2}\\hbar\\omega > 0$.** "
        "Igual que en el pozo, no existe un estado cuántico de energía cero. "
        "La interpretación física es la misma — el principio de "
        "indeterminación — pero el contexto es más rico: aquí la "
        "**energía de punto cero** $\\tfrac{1}{2}\\hbar\\omega$ tiene "
        "consecuencias medibles (vibraciones residuales de moléculas a $T = 0$, "
        "efecto Casimir, fluctuaciones del vacío en QFT)."
    )


def T_oscillator_superposition() -> str:
    return (
        "La solución general es la **superposición** de los estados "
        "estacionarios, cada uno rotando con su fase propia "
        "$e^{-i E_n t / \\hbar}$:\n\n"
        "$$\\psi(x, t) = \\sum_{n=0}^{\\infty} c_n\\, \\varphi_n(x)\\, "
        "e^{-i\\omega(n + 1/2)\\, t}.$$\n\n"
        "Los coeficientes $c_n$ se determinan por la condición inicial "
        "$\\psi(x, 0) = \\psi_0(x)$ usando **ortonormalidad** de las "
        "$\\varphi_n$:\n\n"
        "$$c_n = \\int_{-\\infty}^{\\infty} \\varphi_n(x)\\, \\psi_0(x)\\, dx.$$"
    )


def T_oscillator_physical_interpretation() -> str:
    return (
        "Lecturas físicas del oscilador armónico cuántico:\n\n"
        "- **Espectro equiespaciado.** $E_{n+1} - E_n = \\hbar\\omega$, "
        "constante. Esta es la razón por la que los fonones (vibraciones de "
        "red cristalina) y los fotones (modos del campo EM) llevan **un "
        "cuanto de energía $\\hbar\\omega$**: cada oscilador armónico se "
        "excita en pasos discretos del mismo tamaño. Es lo que hace que "
        "los osciladores se comporten **como partículas** al cuantizar.\n"
        "- **Estado fundamental gaussiano.** $\\varphi_0(x) \\propto "
        "e^{-\\alpha^2 x^2/2}$. La densidad de probabilidad "
        "$|\\varphi_0|^2$ es una gaussiana centrada en el origen, "
        "ancho $\\sim \\ell = \\sqrt{\\hbar/(m\\omega)}$. **No** está "
        "concentrada en el mínimo del potencial como predeciría la "
        "mecánica clásica: el principio de indeterminación la dispersa.\n"
        "- **Estados excitados.** $\\varphi_n$ tiene exactamente $n$ "
        "nodos. El polinomio $H_n(\\alpha x)$ es de grado $n$ con $n$ "
        "raíces reales — los puntos donde la función de onda se anula.\n"
        "- **Estados coherentes.** Una superposición especial de "
        "$\\varphi_n$ (con $c_n = e^{-|z|^2/2}\\, z^n/\\sqrt{n!}$) produce "
        "una gaussiana que **oscila clásicamente** alrededor del "
        "mínimo. Conecta el mundo cuántico con el clásico — los "
        "**estados de luz coherente** del láser son su análogo en QED."
    )


# ===========================================================================
# FOURIER TRANSFORM — heat equation on the real line
# ===========================================================================

def T_statement_heat_line() -> str:
    return (
        "Resolvemos la **ecuación del calor en una varilla infinita**:\n\n"
        "$$u_t = \\alpha^2\\, u_{xx}, \\quad x \\in \\mathbb{R},\\ t > 0,\\qquad "
        "u(x, 0) = f(x).$$\n\n"
        "A diferencia del problema en la barra de longitud $L$, aquí no "
        "hay fronteras — la varilla se extiende a todo $\\mathbb{R}$. "
        "Esto cambia el método: sin condiciones de Dirichlet en los "
        "extremos, no hay un problema de Sturm-Liouville que produzca "
        "autovalores discretos. La herramienta natural es la "
        "**transformada de Fourier**, que diagonaliza $\\partial_x$ y "
        "convierte la EDP en una EDO en el dominio de frecuencias."
    )


def T_heat_line_method_choice() -> str:
    return (
        "**Por qué Fourier y no separación.** La separación de variables "
        "funciona cuando las condiciones de contorno producen un problema "
        "de autovalores con espectro discreto (Sturm-Liouville en un "
        "intervalo finito). Aquí el dominio es infinito y no hay BCs, "
        "así que el espectro es **continuo**: en lugar de una serie "
        "$\\sum_n B_n \\sin(n\\pi x/L)$ aparecerá una integral "
        "$\\int_{-\\infty}^{\\infty} \\hat f(k)\\, e^{ikx}\\, dk$.\n\n"
        "La transformada de Fourier es la generalización limpia de la "
        "serie de Fourier al caso no acotado. Cumple además dos "
        "propiedades clave que vamos a explotar:\n\n"
        "1. **Diagonaliza $\\partial_x$**: $\\mathcal{F}[u_x] = ik\\, \\mathcal{F}[u]$, "
        "$\\mathcal{F}[u_{xx}] = -k^2\\, \\mathcal{F}[u]$. La EDP en "
        "$x$ se vuelve **multiplicación por $-k^2$**.\n"
        "2. **Conmuta con derivadas en $t$**: $\\mathcal{F}[u_t] = "
        "\\partial_t \\mathcal{F}[u]$.\n\n"
        "Combinadas, transformar la EDP la reduce a una EDO de primer "
        "orden en $t$ para cada modo $k$."
    )


def T_heat_line_pde_to_ode() -> str:
    return (
        "Aplicamos $\\mathcal{F}$ a ambos lados de $u_t = \\alpha^2 u_{xx}$. "
        "Denotamos $\\hat u(k, t) = \\mathcal{F}[u(\\cdot, t)](k) = "
        "\\int_{-\\infty}^{\\infty} u(x, t)\\, e^{-ikx}\\, dx$:\n\n"
        "$$\\partial_t \\hat u(k, t) = \\alpha^2\\, (ik)^2\\, \\hat u(k, t) = "
        "-\\alpha^2 k^2\\, \\hat u(k, t).$$\n\n"
        "**Lo importante.** Para cada $k$ fijo, esto es una EDO lineal "
        "de primer orden en $t$ con coeficiente constante $-\\alpha^2 k^2$ "
        "(negativo — clave para el decaimiento). El problema espacial-"
        "temporal ha pasado de ser una EDP a un **continuo de EDOs "
        "desacopladas**, una por cada frecuencia $k$."
    )


def T_heat_line_solve_ode() -> str:
    return (
        "La EDO temporal en cada $k$ se resuelve directamente:\n\n"
        "$$\\hat u(k, t) = \\hat u(k, 0)\\, e^{-\\alpha^2 k^2 t} = "
        "\\hat f(k)\\, e^{-\\alpha^2 k^2 t}.$$\n\n"
        "Las **altas frecuencias decaen más rápido** ($e^{-\\alpha^2 k^2 t}$ "
        "cae cuadráticamente en $k$), lo que es el origen matemático del "
        "**efecto suavizante** del calor: cualquier irregularidad del "
        "dato inicial se borra en tiempo positivo."
    )


def T_heat_line_inverse() -> str:
    return (
        "Para recuperar $u(x, t)$ tomamos la transformada inversa. "
        "Reconocemos que **multiplicar dos transformadas equivale a "
        "convolucionar las funciones originales** "
        "($\\mathcal{F}[f * g] = \\hat f\\, \\hat g$). En nuestro caso\n\n"
        "$$\\hat u(k, t) = \\hat f(k)\\, \\hat G(k, t),\\qquad "
        "\\hat G(k, t) = e^{-\\alpha^2 k^2 t},$$\n\n"
        "así que $u(x, t) = (f * G)(x, t)$ donde $G$ es la **función "
        "fundamental** (heat kernel), determinada por su transformada "
        "$\\hat G$. Calculando la inversa de una gaussiana en $k$ (que "
        "es otra gaussiana en $x$):\n\n"
        "$$\\boxed{\\;G(x, t) = \\frac{1}{\\sqrt{4\\pi \\alpha^2 t}}\\, "
        "\\exp\\!\\left(-\\frac{x^2}{4\\alpha^2 t}\\right).\\;}$$"
    )


def T_heat_line_final_formula() -> str:
    return (
        "La solución cerrada es la convolución del dato inicial con el "
        "**núcleo de Gauss**:\n\n"
        "$$\\boxed{\\;u(x, t) = \\frac{1}{\\sqrt{4\\pi \\alpha^2 t}}\\, "
        "\\int_{-\\infty}^{\\infty} \\exp\\!\\left(-\\frac{(x - y)^2}{4\\alpha^2 t}\\right) "
        "f(y)\\, dy.\\;}$$\n\n"
        "Esta es la **fórmula de Poisson para el calor**: el análogo "
        "exacto, en el contexto del calor 1D infinito, de la fórmula "
        "de D'Alembert para la onda. Lo que en D'Alembert era "
        "evaluación en dos puntos $(f(x-ct) + f(x+ct))/2$, aquí es un "
        "promedio gaussiano con anchura $\\sigma(t) = \\sqrt{2\\alpha^2 t}$ "
        "que **crece** con el tiempo."
    )


def T_heat_line_physical_interpretation() -> str:
    return (
        "Cuatro lecturas físicas que el núcleo gaussiano explicita:\n\n"
        "- **Velocidad infinita de propagación.** Para todo $t > 0$, "
        "$G(x, t) > 0$ en todo $x$. Un dato inicial concentrado en "
        "$y = 0$ \"se siente\" instantáneamente en cualquier $x$, aunque "
        "con peso exponencialmente pequeño. Esto es un **defecto "
        "modelístico** del calor (contradice la relatividad), pero es "
        "una consecuencia inevitable de la ecuación parabólica.\n"
        "- **Suavizado instantáneo.** Para cualquier $t > 0$, $u(x, t)$ "
        "es de clase $C^\\infty$, sin importar la regularidad de $f$. "
        "Una condición inicial **discontinua** (p. ej. escalón) "
        "produce una solución analítica en $t > 0$. Contrastar con la "
        "onda, donde las discontinuidades viajan sin suavizarse.\n"
        "- **Autosimilaridad.** $G(x, t)$ es invariante bajo el "
        "reescalado $(x, t) \\mapsto (\\lambda x, \\lambda^2 t)$: la "
        "anchura crece como $\\sqrt{t}$, no como $t$. Esta ley raíz-de-$t$ "
        "es la firma del fenómeno difusivo y aparece en física "
        "estadística (movimiento browniano), química (difusión "
        "molecular), y finanzas (volatilidad).\n"
        "- **Decaimiento al equilibrio.** Si $f$ es integrable, "
        "$u(x, t) \\to 0$ uniformemente cuando $t \\to \\infty$ (todo "
        "el calor inicial se ha esparcido al infinito)."
    )


# ===========================================================================
# Free Schrödinger on the real line (Fourier transform / complex Gaussian)
# ===========================================================================

def T_statement_schrodinger_free() -> str:
    return (
        "Resolvemos la **ecuación de Schrödinger libre en la recta**:\n\n"
        "$$i\\hbar\\, \\psi_t = -\\frac{\\hbar^2}{2m}\\, \\psi_{xx}, "
        "\\quad x \\in \\mathbb{R},\\ t > 0,\\qquad \\psi(x, 0) = \\psi_0(x).$$\n\n"
        "Es el caso $V(x) = 0$: no hay potencial, no hay paredes, no hay "
        "estados ligados. La partícula se propaga **libremente** sobre "
        "$\\mathbb{R}$. La herramienta natural es la **transformada de "
        "Fourier**: $\\partial_x$ no tiene autovalores discretos en "
        "$L^2(\\mathbb{R})$, pero sí un espectro continuo "
        "$\\{e^{ikx}\\}_{k \\in \\mathbb{R}}$."
    )


def T_schrodinger_free_method_choice() -> str:
    return (
        "**Por qué Fourier.** Igual que en el calor en la recta, el "
        "dominio no acotado mata la separación de variables clásica "
        "(no hay BCs que produzcan autovalores discretos). Las "
        "**ondas planas** $e^{ikx}$ son las autofunciones generalizadas "
        "de $\\partial_x$ con autovalor $ik$, parametrizadas por el "
        "**número de onda** $k \\in \\mathbb{R}$. Físicamente $k$ está "
        "ligado al **momento** $p = \\hbar k$, así que la transformada "
        "de Fourier es literalmente el cambio de la **representación "
        "de posición** a la **representación de momento**.\n\n"
        "**Contraste con el calor.** El procedimiento será idéntico al "
        "de la ecuación del calor — diagonalizar $\\partial_x^2$, "
        "resolver la EDO modal, invertir — pero el coeficiente de la "
        "EDO modal es **imaginario puro** (no real negativo). Esto "
        "cambia radicalmente la física: en lugar de **decaimiento** "
        "tendremos **rotación de fase**, y en lugar de **difusión** "
        "tendremos **dispersión**."
    )


def T_schrodinger_free_pde_to_ode() -> str:
    return (
        "Aplicamos $\\mathcal{F}$ a $i\\hbar\\, \\psi_t = "
        "-\\tfrac{\\hbar^2}{2m}\\, \\psi_{xx}$. Recordando "
        "$\\mathcal{F}[\\psi_{xx}] = -k^2\\, \\hat\\psi$:\n\n"
        "$$i\\hbar\\, \\partial_t \\hat\\psi(k, t) = \\frac{\\hbar^2 k^2}{2m}\\, "
        "\\hat\\psi(k, t)\\quad\\Longleftrightarrow\\quad "
        "\\partial_t \\hat\\psi = -i\\, \\omega(k)\\, \\hat\\psi,$$\n\n"
        "donde $\\omega(k) = \\hbar k^2 / (2m)$ es la **relación de "
        "dispersión** de la partícula libre — el análogo cuántico de "
        "la **energía cinética** $E = p^2/(2m)$ con $p = \\hbar k$ y "
        "$E = \\hbar\\omega$.\n\n"
        "**Lo crucial.** El coeficiente $-i\\omega(k)$ es **imaginario "
        "puro**. En el calor era $-\\alpha^2 k^2$ (real negativo) → "
        "exponencial real decreciente → difusión. Aquí será una "
        "exponencial **compleja** → rotación de fase pura → "
        "norma $L^2$ conservada → unitariedad cuántica."
    )


def T_schrodinger_free_solve_ode() -> str:
    return (
        "La EDO temporal se resuelve directamente:\n\n"
        "$$\\hat\\psi(k, t) = \\hat\\psi_0(k)\\, e^{-i \\omega(k) t} = "
        "\\hat\\psi_0(k)\\, \\exp\\!\\left(-i\\, \\frac{\\hbar k^2}{2m}\\, t\\right).$$\n\n"
        "**Cada modo $k$ rota con frecuencia $\\omega(k) = \\hbar k^2/(2m)$.** "
        "A diferencia del calor (donde modos altos *decaen* más rápido) "
        "y de la onda (donde todos los modos avanzan a la misma "
        "velocidad $c$), aquí cada modo gira a una velocidad de fase "
        "**distinta**: $v_\\phi(k) = \\omega(k)/k = \\hbar k/(2m)$. "
        "Esa dependencia de $k$ es la **dispersión**, y es la responsable "
        "de que los paquetes de onda **se ensanchen** con el tiempo."
    )


def T_schrodinger_free_inverse() -> str:
    return (
        "Para recuperar $\\psi(x, t)$ aplicamos la inversa. Tal como "
        "en el calor, reconocemos la estructura producto en $k$ y "
        "usamos el teorema de convolución:\n\n"
        "$$\\hat\\psi(k, t) = \\hat\\psi_0(k)\\, \\hat K(k, t),\\qquad "
        "\\hat K(k, t) = e^{-i\\hbar k^2 t / (2m)},$$\n\n"
        "así que $\\psi(x, t) = (\\psi_0 * K)(x, t)$. La inversa de "
        "$\\hat K$ es una **gaussiana compleja** (el análogo cuántico "
        "del núcleo del calor, obtenido vía rotación de Wick "
        "$t \\to it$):\n\n"
        "$$\\boxed{\\;K(x, t) = \\sqrt{\\frac{m}{2\\pi i \\hbar t}}\\, "
        "\\exp\\!\\left(\\frac{i m x^2}{2 \\hbar t}\\right).\\;}$$\n\n"
        "Este $K$ es el famoso **propagador libre** de Feynman, la "
        "amplitud de probabilidad de que una partícula que parte en "
        "$y$ llegue a $x$ en tiempo $t$."
    )


def T_schrodinger_free_final_formula() -> str:
    return (
        "La solución cerrada es la convolución del dato inicial con el "
        "**propagador libre**:\n\n"
        "$$\\boxed{\\;\\psi(x, t) = \\sqrt{\\frac{m}{2\\pi i \\hbar t}}\\, "
        "\\int_{-\\infty}^{\\infty} \\exp\\!\\left(\\frac{i m (x - y)^2}{2 \\hbar t}\\right) "
        "\\psi_0(y)\\, dy.\\;}$$\n\n"
        "**Estructura.** Es exactamente la fórmula del calor con "
        "$\\alpha^2 \\leftrightarrow i\\hbar/(2m)$ — la sustitución que "
        "convierte la ecuación de difusión real en la de difusión "
        "imaginaria. Esta correspondencia es la **rotación de Wick** "
        "y es la base de la formulación de Feynman de la mecánica "
        "cuántica como suma sobre caminos."
    )


# ===========================================================================
# Wave 2D on a rectangle (rectangular drum)
# ===========================================================================

def T_statement_wave_rect_2d() -> str:
    return (
        "Resolvemos la **ecuación de onda 2D** sobre un rectángulo con "
        "bordes fijos (un **tambor rectangular**):\n\n"
        "$$u_{tt} = c^2 (u_{xx} + u_{yy}),\\quad "
        "(x, y) \\in [0, a] \\times [0, b],\\ t > 0,$$\n\n"
        "con $u = 0$ sobre los cuatro lados, "
        "$u(x, y, 0) = f(x, y)$ y "
        "$u_t(x, y, 0) = g(x, y)$.\n\n"
        "Es el complemento natural del **tambor circular**: misma "
        "ecuación, geometría distinta. La geometría rectangular "
        "permite separar limpiamente en cartesianas y obtener una "
        "**base producto** $\\sin(m\\pi x/a)\\sin(n\\pi y/b)$ — sin "
        "necesidad de funciones especiales (a diferencia del disco, "
        "que requiere Bessel)."
    )


def T_wave_rect_method_choice() -> str:
    return (
        "**Separación doble en cartesianas.** Postulamos\n\n"
        "$$u(x, y, t) = X(x)\\, Y(y)\\, T(t),$$\n\n"
        "sustituimos en la EDP y dividimos por $X Y T$. La "
        "separación produce **tres** EDOs ordinarias:\n\n"
        "$$\\frac{T''}{c^2 T} = \\frac{X''}{X} + \\frac{Y''}{Y} = "
        "-\\mu \\quad \\text{(constante)}.$$\n\n"
        "A su vez $X''/X = -\\lambda$ y $Y''/Y = \\lambda - \\mu = -\\nu$ "
        "son separadas: dos problemas de Sturm-Liouville independientes "
        "en $x$ e $y$, cada uno con autovalores discretos. La condición "
        "$\\mu = \\lambda + \\nu$ acopla los autovalores y produce el "
        "**espectro bidimensional** $\\omega_{mn} = c\\sqrt{\\mu_{mn}}$."
    )


def T_wave_rect_eigenmodes() -> str:
    return (
        "Las cuatro BCs homogéneas en $x = 0, a$ y $y = 0, b$ "
        "determinan los modos:\n\n"
        "$$X_m(x) = \\sin\\!\\left(\\frac{m\\pi x}{a}\\right),\\ "
        "\\lambda_m = \\left(\\frac{m\\pi}{a}\\right)^2,\\quad "
        "m = 1, 2, 3, \\ldots,$$\n\n"
        "$$Y_n(y) = \\sin\\!\\left(\\frac{n\\pi y}{b}\\right),\\ "
        "\\nu_n = \\left(\\frac{n\\pi}{b}\\right)^2,\\quad "
        "n = 1, 2, 3, \\ldots.$$\n\n"
        "El **autovalor 2D** y la **frecuencia angular** de cada modo:\n\n"
        "$$\\mu_{mn} = \\lambda_m + \\nu_n = \\pi^2\\left("
        "\\frac{m^2}{a^2} + \\frac{n^2}{b^2}\\right),\\qquad "
        "\\omega_{mn} = c\\sqrt{\\mu_{mn}} = c \\pi\\, \\sqrt{"
        "\\frac{m^2}{a^2} + \\frac{n^2}{b^2}}.$$\n\n"
        "Cada par $(m, n)$ define un **patrón de nodos** (las líneas "
        "$\\sin = 0$): rectas horizontales y verticales que cuadriculan "
        "el rectángulo en $m \\times n$ celdas vibrando en fase opuesta."
    )


def T_wave_rect_solution() -> str:
    return (
        "**Solución general** (serie doble en modos normales):\n\n"
        "$$\\boxed{\\; u(x, y, t) = \\sum_{m=1}^{\\infty} \\sum_{n=1}^{\\infty} "
        "\\bigl( A_{mn} \\cos(\\omega_{mn} t) + B_{mn} \\sin(\\omega_{mn} t) \\bigr)\\, "
        "\\sin\\!\\left(\\frac{m\\pi x}{a}\\right) "
        "\\sin\\!\\left(\\frac{n\\pi y}{b}\\right), \\;}$$\n\n"
        "con coeficientes obtenidos por **doble proyección** sobre la "
        "base producto:\n\n"
        "$$A_{mn} = \\frac{4}{ab}\\int_0^a\\!\\!\\int_0^b "
        "f(x, y)\\, \\sin\\!\\left(\\frac{m\\pi x}{a}\\right)"
        "\\sin\\!\\left(\\frac{n\\pi y}{b}\\right)\\, dx\\, dy,$$\n\n"
        "$$B_{mn} = \\frac{4}{ab\\, \\omega_{mn}}\\int_0^a\\!\\!\\int_0^b "
        "g(x, y)\\, \\sin\\!\\left(\\frac{m\\pi x}{a}\\right)"
        "\\sin\\!\\left(\\frac{n\\pi y}{b}\\right)\\, dx\\, dy.$$\n\n"
        "La ortogonalidad de los senos en cada dirección, combinada "
        "vía Fubini, justifica la inversión término-a-término."
    )


def T_wave_rect_physical_interpretation() -> str:
    return (
        "**Comparación de tambores: 1D vs 2D-rectángulo vs 2D-disco.**\n\n"
        "- **Cuerda** ($n\\pi/L$): frecuencias $\\omega_n = cn\\pi/L$, "
        "**armónicas enteras**. Por eso una cuerda suena \"musical\".\n"
        "- **Tambor circular** (ceros de $J_0$): "
        "$\\mu_2/\\mu_1 \\approx 2.295$, $\\mu_3/\\mu_1 \\approx 3.598$, …, "
        "**inarmónicas irracionales**. Suena \"a percusión\", no a nota.\n"
        "- **Tambor rectangular** ($a$ y $b$ no proporcionales): "
        "$\\omega_{mn}/\\omega_{11} = "
        "\\sqrt{(m^2/a^2 + n^2/b^2)/(1/a^2 + 1/b^2)}$. Inarmónico en "
        "general; si $a = b$ (cuadrado), aparece **degeneración** "
        "$\\omega_{mn} = \\omega_{nm}$ — distintos modos comparten "
        "frecuencia.\n\n"
        "**Mark Kac (1966): \"Can one hear the shape of a drum?\"** Si "
        "te dan el espectro $\\{\\omega_{mn}\\}$ de un tambor, ¿puedes "
        "reconstruir la geometría? Para tambores convexos suficientemente "
        "simétricos, sí. **Pero existen pares de tambores no isométricos "
        "con espectros idénticos** (Gordon-Webb-Wolpert 1992 — "
        "construcciones poligonales). Es uno de los teoremas más "
        "elegantes del siglo XX: el espectro **casi** determina la "
        "geometría, pero no del todo."
    )


# ===========================================================================
# Duhamel (heat equation with source on the real line)
# ===========================================================================

def T_statement_duhamel() -> str:
    return (
        "Resolvemos la **ecuación del calor inhomogénea** en la recta:\n\n"
        "$$u_t = \\alpha^2\\, u_{xx} + f(x, t), "
        "\\quad x \\in \\mathbb{R},\\ t > 0,\\qquad "
        "u(x, 0) = u_0(x).$$\n\n"
        "Generaliza el problema homogéneo $u_t = \\alpha^2 u_{xx}$ que "
        "resolvimos con Fourier: ahora la EDP tiene un **término fuente** "
        "$f(x, t)$ que inyecta (o extrae) calor en cada instante. La "
        "**linealidad** de la EDP nos permite separar el efecto del "
        "dato inicial del efecto del forzamiento — el corazón del "
        "**principio de Duhamel**."
    )


def T_duhamel_method_choice() -> str:
    return (
        "**Principio de Duhamel: superposición continua.** La idea es "
        "**descomponer la fuente $f(x, t)$ como una superposición de "
        "fuentes instantáneas** $f(\\cdot, s)\\,\\delta(t - s)$ para "
        "$s \\in [0, t]$, resolver el efecto de cada una, y sumar:\n\n"
        "1. **Respuesta a la CI sola** ($f = 0$): es Fourier-en-recta, "
        "$u_{\\text{hom}}(x, t) = (u_0 * G(\\cdot, t))(x)$ con el núcleo "
        "de Gauss.\n"
        "2. **Respuesta a una fuente instantánea** en el tiempo $s$ "
        "con perfil espacial $f(y, s)$: para $t > s$, evoluciona como "
        "el calor con dato inicial $f(\\cdot, s)$ durante un tiempo "
        "$t - s$. Es $(f(\\cdot, s) * G(\\cdot, t - s))(x)$.\n"
        "3. **Suma sobre todas las fuentes instantáneas** integrando "
        "en $s \\in [0, t]$.\n\n"
        "**Por qué funciona.** La superposición es legítima porque la "
        "EDP es **lineal**: la solución de cada \"pieza\" se suma sin "
        "interferencia. El delta de Dirac que separa $f$ en pulsos "
        "instantáneos es el truco distribucional que cierra la "
        "construcción rigurosamente."
    )


def T_duhamel_formula() -> str:
    return (
        "Combinando la solución homogénea y la integral de Duhamel:\n\n"
        "$$\\boxed{\\; u(x, t) = \\underbrace{\\int_{-\\infty}^{\\infty} "
        "G(x - y, t)\\, u_0(y)\\, dy}_{u_{\\text{homogénea}}} "
        "+ \\underbrace{\\int_0^t \\!\\!\\int_{-\\infty}^{\\infty} "
        "G(x - y, t - s)\\, f(y, s)\\, dy\\, ds}_{u_{\\text{forzamiento}}}, \\;}$$\n\n"
        "donde $G(x, t) = \\frac{1}{\\sqrt{4\\pi \\alpha^2 t}}\\, "
        "e^{-x^2/(4\\alpha^2 t)}$ es el **núcleo de Gauss** que ya "
        "conocemos del problema homogéneo. La fórmula admite una "
        "interpretación operacional muy limpia:\n\n"
        "- $u_{\\text{hom}}$ es la convolución del **dato inicial** con "
        "el núcleo al tiempo $t$.\n"
        "- $u_{\\text{forz}}$ es una **convolución cuádruple** (en "
        "$x \\leftrightarrow y$ espacial y $0 \\leftrightarrow t$ temporal "
        "contra $s$) del forzamiento con el mismo núcleo, **donde la "
        "edad efectiva de la fuente $s$ es $t - s$**.\n\n"
        "Notación compacta: $u = G(\\cdot, t) * u_0 + "
        "\\int_0^t G(\\cdot, t-s) * f(\\cdot, s)\\, ds$."
    )


def T_duhamel_intuition() -> str:
    return (
        "**Tres lecturas físicas e intuitivas:**\n\n"
        "- **Memoria con olvido gaussiano.** Una fuente que actuó en "
        "el tiempo $s < t$ contribuye al estado actual $u(\\cdot, t)$ "
        "con un peso $G(\\cdot, t - s)$: el calor inyectado se ha "
        "**propagado y difundido** durante un tiempo $t - s$. Las "
        "fuentes muy antiguas ($t - s$ grande) tienen contribución "
        "muy esparcida y atenuada — el sistema **olvida** "
        "exponencialmente.\n"
        "- **Causalidad explícita.** La integral en $s$ va de $0$ a "
        "$t$, **no más allá** de $t$. El estado actual no depende del "
        "futuro: las fuentes que aún no han actuado no aportan nada. "
        "Esto es la **flecha del tiempo termodinámica** codificada en "
        "los límites de integración.\n"
        "- **Una sola función de Green hace todo el trabajo.** $G$ es "
        "la **función de Green del operador** $\\partial_t - "
        "\\alpha^2 \\partial_x^2$ con dato inicial delta y dato fuente "
        "delta — y aparece exactamente en los dos lugares de la "
        "fórmula. Es el patrón unificador entre Duhamel y la "
        "función de Green clásica."
    )


# ===========================================================================
# Burgers (inviscid) — characteristics + shocks
# ===========================================================================

def T_statement_burgers() -> str:
    return (
        "Resolvemos la **ecuación de Burgers no viscosa** (modelo "
        "prototipo de EDP cuasi-lineal hiperbólica):\n\n"
        "$$u_t + u\\, u_x = 0,\\quad x \\in \\mathbb{R},\\ t > 0,\\qquad "
        "u(x, 0) = u_0(x).$$\n\n"
        "**Aparente similitud con transporte lineal.** Si reemplazas "
        "el segundo coeficiente $u$ por una constante $c$, recuperas "
        "$u_t + c u_x = 0$ — el transporte lineal, cuya solución es "
        "$u(x, t) = u_0(x - ct)$ (la onda viaja sin deformarse a "
        "velocidad $c$). Pero aquí **la velocidad de propagación "
        "depende de la propia solución**, y eso lo cambia todo: las "
        "regiones donde $u$ es grande viajan más rápido que las "
        "regiones donde $u$ es pequeño. Si el dato inicial es "
        "**decreciente**, las características de atrás alcanzan a las "
        "de adelante en tiempo finito → **choque**."
    )


def T_burgers_method_choice() -> str:
    return (
        "**Método de las características generalizado.** Para una EDP "
        "de primer orden $u_t + a(u) u_x = 0$, las curvas a lo largo "
        "de las cuales $u$ es constante son las **características**, "
        "que satisfacen\n\n"
        "$$\\frac{dx}{dt} = a(u) = u(x, t).$$\n\n"
        "**Lo crucial.** Como $u$ se conserva a lo largo de la "
        "característica, su pendiente $dx/dt = u$ es **constante** "
        "sobre cada curva. Por tanto las características son "
        "**líneas rectas** — pero con **pendientes distintas** según "
        "el punto de partida.\n\n"
        "Eso es lo que produce el choque: dos características con "
        "pendientes distintas eventualmente se intersectan, y en el "
        "punto de cruce el método predice **dos valores de $u$ "
        "incompatibles**. La EDP clásica deja de tener solución "
        "diferenciable; hay que pasar a **soluciones débiles**."
    )


def T_burgers_characteristics() -> str:
    return (
        "Parametrizamos cada característica por el punto $x_0$ donde "
        "intersecta el eje $t = 0$. A lo largo de ella, $u$ es "
        "constante igual a $u_0(x_0)$, así que la pendiente $dx/dt = "
        "u = u_0(x_0)$ es también constante:\n\n"
        "$$x(t; x_0) = x_0 + u_0(x_0)\\, t,\\qquad "
        "u(x(t; x_0), t) = u_0(x_0).$$\n\n"
        "Esta es la **solución implícita** de Burgers: dado $(x, t)$, "
        "para hallar $u(x, t)$ resolvemos $x = x_0 + u_0(x_0) t$ "
        "para $x_0$ y leemos $u = u_0(x_0)$. Mientras esta inversión "
        "tenga **solución única**, la solución clásica existe."
    )


def T_burgers_breaking_time() -> str:
    return (
        "**Cuándo se rompe la solución clásica.** La inversión "
        "$x \\mapsto x_0$ es bien-planteada mientras el jacobiano "
        "$\\partial x/\\partial x_0 = 1 + u_0'(x_0)\\, t$ sea distinto "
        "de cero. Cuando alguna característica alcanza a otra:\n\n"
        "$$1 + u_0'(x_0)\\, t = 0 \\quad \\Longleftrightarrow \\quad "
        "t = -\\frac{1}{u_0'(x_0)}.$$\n\n"
        "El **tiempo de ruptura** $t_b$ es el mínimo positivo de estos "
        "tiempos, alcanzado donde $u_0'$ es más negativa:\n\n"
        "$$\\boxed{\\; t_b = -\\frac{1}{\\min_{x_0} u_0'(x_0)} "
        "= \\frac{1}{\\max_{x_0} \\bigl(-u_0'(x_0)\\bigr)}. \\;}$$\n\n"
        "Si $u_0$ es **no decreciente** (o si $\\min u_0' \\ge 0$), las "
        "características divergen y la solución clásica existe para "
        "**todo tiempo**. Si $u_0$ tiene una zona estrictamente "
        "decreciente, $t_b < \\infty$ y aparece un choque."
    )


def T_burgers_shock_rankine_hugoniot() -> str:
    return (
        "**Más allá de $t_b$: solución débil + condición de "
        "Rankine-Hugoniot.** Para $t > t_b$ buscamos una solución que "
        "sea diferenciable a trozos, con una **discontinuidad de salto** "
        "(el choque) que se propaga a lo largo de una curva $x = "
        "s(t)$. La conservación integral de Burgers, "
        "$\\frac{d}{dt}\\int u\\, dx = 0$, impone que la velocidad del "
        "choque sea la media aritmética de los valores a cada lado:\n\n"
        "$$\\boxed{\\; \\frac{ds}{dt} = "
        "\\frac{u_L + u_R}{2}, \\;}$$\n\n"
        "donde $u_L$ y $u_R$ son los valores de $u$ inmediatamente a "
        "la izquierda y a la derecha del choque. Esta es la **condición "
        "de Rankine-Hugoniot**: la deducción la verás detallada en los "
        "cursos avanzados, pero la idea geométrica es \"el choque "
        "viaja al promedio de las velocidades que conecta\"."
    )


def T_burgers_physical_interpretation() -> str:
    return (
        "Tres lecturas físicas y una matemática:\n\n"
        "- **Tráfico vehicular.** $u$ es la velocidad de los coches. "
        "Las zonas rápidas alcanzan a las lentas y se forma una onda "
        "de choque: en una autopista, eso es la frontera nítida entre "
        "tráfico fluido y atasco.\n"
        "- **Dinámica de fluidos.** Burgers es el primer paso "
        "didáctico hacia las ecuaciones de Euler — la velocidad "
        "advecta a sí misma, las regiones rápidas alcanzan a las "
        "lentas, y emergen choques (ondas sonoras de choque, "
        "explosiones).\n"
        "- **Viscosidad evanescente.** La versión viscosa $u_t + u u_x = "
        "\\nu u_{xx}$ regulariza el choque: en lugar de discontinuidad, "
        "hay una capa de transición de espesor $\\sim \\nu$. Cuando "
        "$\\nu \\to 0^+$, recuperas la onda de choque ideal — esto se "
        "llama el **límite de viscosidad evanescente** y selecciona "
        "el único choque físicamente correcto (la \"solución entrópica\").\n"
        "- **Matemáticamente:** Burgers es el ejemplo más pequeño donde "
        "una EDP suave puede generar discontinuidades a partir de "
        "datos suaves. Es la frontera entre la teoría \"limpia\" de "
        "EDPs lineales y la jungla de las cuasi-lineales hiperbólicas."
    )


# ===========================================================================
# General 2nd-order PDE classification (fallback)
# ===========================================================================

def T_statement_general_2nd_order() -> str:
    return (
        "Recibimos una **EDP lineal de segundo orden en dos variables** "
        "con la forma estándar\n\n"
        "$$A\\, u_{\\xi_1 \\xi_1} + B\\, u_{\\xi_1 \\xi_2} + "
        "C\\, u_{\\xi_2 \\xi_2} + (\\text{términos de orden inferior}) = 0,$$\n\n"
        "donde $(\\xi_1, \\xi_2)$ pueden ser $(x, y)$ (problema "
        "estacionario / elíptico) o $(x, t)$ (problema de evolución). "
        "**No tenemos un método cerrado** específico para tu ecuación, "
        "pero sí podemos hacer algo muy útil: **clasificarla**, "
        "calcular sus **curvas características** y reducirla a su "
        "**forma canónica**. Cuando los coeficientes son constantes y "
        "no hay términos de orden inferior, la forma canónica admite "
        "una solución general explícita."
    )


def T_general_method_choice() -> str:
    return (
        "**Por qué este flujo.** Toda EDP lineal de segundo orden "
        "pertenece a una de **tres familias** clasificadas por el "
        "signo del discriminante $\\Delta = B^2 - 4AC$. La "
        "clasificación es **invariante bajo cambios de variables "
        "regulares**: define las propiedades fundamentales de la EDP "
        "(suavizado vs propagación con frente neto, dominios de "
        "dependencia, número de BCs/ICs necesarias, etc.).\n\n"
        "El procedimiento sistemático es:\n\n"
        "1. Identificar $A$, $B$, $C$ leyendo los coeficientes de "
        "$u_{\\xi_1 \\xi_1}$, $u_{\\xi_1 \\xi_2}$, $u_{\\xi_2 \\xi_2}$.\n"
        "2. Calcular $\\Delta = B^2 - 4AC$ y clasificar.\n"
        "3. Resolver la **ecuación característica** "
        "$A\\, m^2 - B\\, m + C = 0$ donde $m = d\\xi_2/d\\xi_1$.\n"
        "4. Definir las **variables canónicas** $\\xi, \\eta$ a lo largo "
        "de las características.\n"
        "5. Sustituir y obtener la forma canónica. Para EDPs puras de "
        "segundo orden con coeficientes constantes, esta forma se "
        "resuelve en forma cerrada."
    )


def T_general_characteristics() -> str:
    return (
        "Las **curvas características** son las trayectorias a lo "
        "largo de las cuales la EDP **pierde control** (la unicidad "
        "del problema de Cauchy falla). Geométricamente son las "
        "direcciones a lo largo de las cuales la información se "
        "propaga (hiperbólico) o desaparece (parabólico).\n\n"
        "Derivándose de la condición de degeneración "
        "$A(d\\xi_2)^2 - B\\, d\\xi_1\\, d\\xi_2 + C(d\\xi_1)^2 = 0$, "
        "con $m = d\\xi_2/d\\xi_1$:\n\n"
        "$$A\\, m^2 - B\\, m + C = 0 \\quad \\Longrightarrow \\quad "
        "m = \\frac{B \\pm \\sqrt{B^2 - 4AC}}{2A} = "
        "\\frac{B \\pm \\sqrt{\\Delta}}{2A}.$$\n\n"
        "El **número y tipo** de raíces de esta cuadrática es lo que "
        "nombra las tres familias:\n\n"
        "- $\\Delta > 0$: **hiperbólica** — dos características reales "
        "y distintas (ondas viajeras).\n"
        "- $\\Delta = 0$: **parabólica** — una familia doble (difusión, "
        "una sola \"dirección dominante\").\n"
        "- $\\Delta < 0$: **elíptica** — características complejas "
        "conjugadas (problema estacionario, sin propagación)."
    )


def T_general_canonical_form() -> str:
    return (
        "El **cambio de variables a coordenadas canónicas** simplifica "
        "la EDP a su forma irreducible. La idea: usar las "
        "características como nuevas coordenadas.\n\n"
        "- **Hiperbólico** ($\\Delta > 0$): con raíces $m_1, m_2$, "
        "$\\xi = \\xi_2 - m_1\\, \\xi_1$, $\\eta = \\xi_2 - m_2\\, \\xi_1$. "
        "La forma canónica es $u_{\\xi\\eta} + (\\text{orden inferior}) = 0$.\n"
        "- **Parabólico** ($\\Delta = 0$): con la única raíz "
        "$m = B/(2A)$, $\\xi = \\xi_2 - m\\, \\xi_1$, $\\eta = \\xi_1$ "
        "(o cualquier otra variable transversal). La forma canónica "
        "es $u_{\\eta\\eta} + (\\text{orden inferior}) = 0$.\n"
        "- **Elíptico** ($\\Delta < 0$): con raíces complejas "
        "$m = \\alpha \\pm i\\beta$, definir "
        "$\\sigma = \\xi_2 - \\alpha\\, \\xi_1$, "
        "$\\tau = \\beta\\, \\xi_1$. La forma canónica es "
        "$u_{\\sigma\\sigma} + u_{\\tau\\tau} + (\\text{orden inferior}) = 0$ "
        "(Laplaciana en las nuevas variables).\n\n"
        "**Por qué funciona.** A lo largo de una característica $\\xi = "
        "\\text{cte}$, la EDP \"no ve\" cambios en esa dirección. "
        "Reescribirla en coordenadas alineadas con las características "
        "elimina (o simplifica al máximo) los términos cruzados y los "
        "términos de segundo orden no esenciales."
    )


def T_general_hyperbolic_closed_form() -> str:
    return (
        "**Caso favorable: hiperbólico puro de segundo orden con "
        "coeficientes constantes.** La forma canónica es exactamente "
        "$u_{\\xi\\eta} = 0$, cuya solución general es **inmediata**:\n\n"
        "$$\\boxed{\\; u(\\xi_1, \\xi_2) = F(\\xi) + G(\\eta) \\;}$$\n\n"
        "donde $F$ y $G$ son funciones arbitrarias de una variable, "
        "fijadas por las condiciones iniciales/de contorno. Es el "
        "**teorema de D'Alembert generalizado**: cualquier EDP "
        "hiperbólica pura de segundo orden con coeficientes constantes "
        "tiene soluciones tipo \"onda viajera\" a lo largo de cada "
        "familia de características.\n\n"
        "**Comparación con la onda clásica.** Para $u_{tt} = c^2 "
        "u_{xx}$ las características son $t \\mp x/c$, y la fórmula "
        "se reduce a la D'Alembert estándar $u = F(x - ct) + G(x + ct)$."
    )


def T_general_no_closed_form() -> str:
    return (
        "**Por sí sola, la clasificación no determina la solución.** "
        "Para obtenerla necesitarías especificar:\n\n"
        "- **Condiciones iniciales y de frontera** apropiadas al tipo "
        "(número y tipo varía: las EDPs elípticas son problemas de "
        "contorno; las parabólicas, mixtos; las hiperbólicas, de Cauchy).\n"
        "- Un **dominio concreto**.\n\n"
        "Con esos datos, recurre a uno de los métodos específicos del "
        "repertorio:\n\n"
        "- **Elíptica** sobre un dominio acotado: separación de "
        "variables (rectángulo, disco, bola) o función de Green.\n"
        "- **Hiperbólica** acotada: separación de variables; "
        "no acotada: D'Alembert / Fourier.\n"
        "- **Parabólica** acotada con Dirichlet 0: separación de "
        "variables; no acotada: Fourier; semi-infinita con BC en "
        "tiempo: Laplace."
    )


def T_general_physical_interpretation() -> str:
    return (
        "La clasificación elíptico/parabólico/hiperbólico tiene una "
        "interpretación física directa:\n\n"
        "- **Elíptica** ($\\Delta < 0$): describe **estados de "
        "equilibrio**. La información no se propaga: cualquier cambio "
        "en la frontera se siente instantáneamente en todo el dominio. "
        "Ejemplo: distribución estática de potencial (Laplace, Poisson).\n"
        "- **Parabólica** ($\\Delta = 0$): describe **difusión** y "
        "procesos irreversibles. La información se propaga "
        "instantáneamente (velocidad infinita formal) pero se "
        "**suaviza** rápidamente. Asimetría temporal: el pasado se "
        "puede reconstruir mal. Ejemplos: calor, Schrödinger libre, "
        "Black-Scholes.\n"
        "- **Hiperbólica** ($\\Delta > 0$): describe **propagación "
        "con velocidad finita**. Las señales viajan a lo largo de las "
        "características, sin difundirse (en el caso puro). Simetría "
        "temporal. Ejemplos: onda mecánica, electromagnética, sonido.\n\n"
        "**Esta es la lección más importante de la teoría de EDPs "
        "lineales de segundo orden:** tres tipos, tres comportamientos "
        "físicos cualitativamente distintos."
    )


def T_statement_heat_halfline() -> str:
    return (
        "Resolvemos la **conducción del calor en una barra semi-infinita** "
        "con temperatura prescrita en el extremo:\n\n"
        "$$u_t = \\alpha^2\\, u_{xx},\\quad x > 0,\\ t > 0,\\qquad "
        "u(x, 0) = 0,\\quad u(0, t) = h.$$\n\n"
        "Es el modelo prototipo de **enfriamiento/calentamiento desde "
        "una pared**: el dato físico vive en el **tiempo** (la temperatura "
        "del extremo $x = 0$), no en el espacio. Ese cambio de "
        "perspectiva sugiere transformar respecto a $t$ — no a $x$ "
        "como en el problema en la recta entera."
    )


def T_heat_halfline_method_choice() -> str:
    return (
        "**Por qué transformada de Laplace y no Fourier.** Aquí el "
        "dominio en $x$ es **semi-infinito** $[0, \\infty)$ y "
        "tenemos un dato en $x = 0$ (no una condición de decaimiento "
        "homogénea). Fourier en $x$ es incómoda — necesitaríamos "
        "extender por reflexión, lo que mete imágenes. En cambio, el "
        "dominio en $t$ es $[0, \\infty)$ con condición inicial "
        "$u(x, 0) = 0$: exactamente lo que la **transformada de "
        "Laplace** maneja con naturalidad.\n\n"
        "Recordamos su definición y propiedades clave:\n\n"
        "$$\\mathcal{L}[u](x, s) = U(x, s) = \\int_0^\\infty e^{-st}\\, u(x, t)\\, dt,$$\n\n"
        "1. $\\mathcal{L}[u_t] = s\\, U(x, s) - u(x, 0)$ — la condición "
        "inicial entra automáticamente.\n"
        "2. $\\mathcal{L}[u_{xx}] = U_{xx}(x, s)$ — $\\partial_x$ "
        "conmuta con $\\mathcal{L}$ (es transformada en $t$, no en $x$).\n"
        "3. La transformada convierte un problema **evolutivo en $t$** "
        "en una **EDO ordinaria en $x$** parametrizada por $s$."
    )


def T_heat_halfline_pde_to_ode() -> str:
    return (
        "Aplicamos $\\mathcal{L}$ a $u_t = \\alpha^2 u_{xx}$ usando "
        "la propiedad 1 y la condición inicial $u(x, 0) = 0$:\n\n"
        "$$s\\, U(x, s) - 0 = \\alpha^2\\, U_{xx}(x, s) "
        "\\quad\\Longleftrightarrow\\quad "
        "U_{xx} - \\frac{s}{\\alpha^2}\\, U = 0.$$\n\n"
        "**Resultado clave.** Hemos pasado de una EDP en dos variables "
        "$(x, t)$ a una **EDO de segundo orden en $x$** con coeficiente "
        "constante (dependiente paramétricamente de $s$). Es el mismo "
        "tipo de simplificación que la transformada de Fourier producía "
        "para el calor en la recta, pero con $x$ y $t$ intercambiados."
    )


def T_heat_halfline_solve_ode() -> str:
    return (
        "La EDO $U_{xx} - (s/\\alpha^2)U = 0$ es **lineal de segundo "
        "orden con coeficientes constantes**. La ecuación característica "
        "es $r^2 = s/\\alpha^2$, con raíces $r = \\pm\\sqrt{s}/\\alpha$. "
        "La solución general:\n\n"
        "$$U(x, s) = A(s)\\, e^{-\\sqrt{s}\\, x/\\alpha} + "
        "B(s)\\, e^{+\\sqrt{s}\\, x/\\alpha}.$$\n\n"
        "Para que $u(x, t)$ esté **acotada cuando $x \\to \\infty$** "
        "(o equivalentemente para que la inversa de Laplace exista), "
        "necesitamos $B(s) = 0$. Aplicando ahora la condición de "
        "frontera en el dominio transformado:\n\n"
        "$$u(0, t) = h \\quad\\Rightarrow\\quad U(0, s) = "
        "\\mathcal{L}[h] = \\frac{h}{s} \\quad\\Rightarrow\\quad "
        "A(s) = \\frac{h}{s}.$$\n\n"
        "Por tanto:\n\n"
        "$$U(x, s) = \\frac{h}{s}\\, e^{-\\sqrt{s}\\, x/\\alpha}.$$"
    )


def T_heat_halfline_inverse() -> str:
    return (
        "El último paso es **invertir la transformada de Laplace**. "
        "El par fundamental que usamos es:\n\n"
        "$$\\mathcal{L}^{-1}\\!\\left[\\frac{1}{s}\\, e^{-a\\sqrt{s}}\\right](t) = "
        "\\operatorname{erfc}\\!\\left(\\frac{a}{2\\sqrt{t}}\\right),"
        "\\quad a > 0,$$\n\n"
        "donde $\\operatorname{erfc}(z) = "
        "\\frac{2}{\\sqrt{\\pi}}\\int_z^\\infty e^{-\\tau^2}\\, d\\tau$ "
        "es la **función error complementaria**. Con $a = x/\\alpha$:\n\n"
        "$$\\boxed{\\;u(x, t) = h\\, \\operatorname{erfc}\\!\\left("
        "\\frac{x}{2\\alpha\\sqrt{t}}\\right).\\;}$$\n\n"
        "La aparición de $\\operatorname{erfc}$ no es accidental: es la "
        "primitiva del **núcleo de Gauss** que apareció en el problema "
        "de la recta. Físicamente $\\operatorname{erfc}$ se interpreta "
        "como la **fracción de probabilidad acumulada** más allá de un "
        "umbral en una distribución normal, lo que cuadra con la "
        "interpretación browniana del calor."
    )


def T_heat_halfline_final_formula() -> str:
    return (
        "La solución es:\n\n"
        "$$\\boxed{\\;u(x, t) = h\\, \\operatorname{erfc}\\!\\left("
        "\\frac{x}{2\\alpha\\sqrt{t}}\\right) "
        "= h\\, \\left[1 - \\operatorname{erf}\\!\\left("
        "\\frac{x}{2\\alpha\\sqrt{t}}\\right)\\right].\\;}$$\n\n"
        "La variable adimensional $\\eta = x/(2\\alpha\\sqrt{t})$ es la "
        "**variable de similaridad**: la solución **sólo depende del "
        "cociente** $x/\\sqrt{t}$. Esta autosimilaridad ya la vimos en "
        "el núcleo de Gauss (núcleo $\\propto \\sqrt{t}$, ancho $\\sim "
        "\\sqrt{t}$), y aquí se manifiesta como una propiedad del "
        "perfil entero, no sólo del núcleo."
    )


def T_heat_halfline_physical_interpretation() -> str:
    return (
        "Cuatro lecturas físicas inmediatas:\n\n"
        "- **Longitud de difusión térmica.** $\\delta(t) = "
        "2\\alpha\\sqrt{t}$ es la profundidad característica hasta "
        "donde el calor ha penetrado en tiempo $t$. Para $x \\ll "
        "\\delta(t)$ ya casi $u \\approx h$; para $x \\gg \\delta(t)$ "
        "todavía $u \\approx 0$. Es la regla práctica del ingeniero: "
        "el frente avanza como $\\sqrt{t}$, lentamente.\n"
        "- **Velocidad infinita formal pero penetración finita "
        "efectiva.** Igual que en la recta entera, $u > 0$ para "
        "**todo** $x > 0$ y todo $t > 0$ (velocidad infinita). Pero "
        "$\\operatorname{erfc}$ decae **super-exponencialmente** en su "
        "argumento, así que más allá de $3\\delta(t)$ la perturbación "
        "es despreciable.\n"
        "- **Autosimilaridad.** Si reescalamos $x \\mapsto \\lambda x$ "
        "y $t \\mapsto \\lambda^2 t$, el cociente $\\eta = "
        "x/(2\\alpha\\sqrt{t})$ no cambia, y por tanto $u$ tampoco. "
        "Esta invariancia es la firma de los problemas difusivos en "
        "dominios sin escala intrínseca de longitud.\n"
        "- **Flujo en la pared.** "
        "$-k\\, u_x(0, t) = k h / (\\alpha\\sqrt{\\pi t})$ "
        "(diverge como $1/\\sqrt{t}$ cuando $t \\to 0^+$). Aplicación "
        "directa: este es el flujo que entra a un sólido frío cuya "
        "superficie sube de golpe a $h$; es la base del análisis de "
        "**templado** en metalurgia."
    )


def T_schrodinger_free_physical_interpretation() -> str:
    return (
        "Cuatro lecturas físicas del propagador libre:\n\n"
        "- **Unitariedad.** $|K(x, t)|^2 = m/(2\\pi\\hbar t)$ es real, "
        "independiente de $x$ (¡el módulo es constante en $x$!). La "
        "norma $L^2$ de $\\psi$ se conserva: la probabilidad total "
        "$\\int |\\psi|^2\\, dx$ no cambia con el tiempo. Esto es lo "
        "que reemplaza el decaimiento difusivo del calor.\n"
        "- **Dispersión: el paquete se ensancha linealmente en $t$.** "
        "Un paquete gaussiano inicial con anchura $\\sigma_0$ tiene "
        "anchura $\\sigma(t) = \\sigma_0 \\sqrt{1 + (\\hbar t/(2m\\sigma_0^2))^2}$. "
        "Para tiempos largos, $\\sigma(t) \\sim \\hbar t / (2 m \\sigma_0)$ — "
        "**crecimiento lineal en $t$**, no $\\sqrt{t}$ como en el calor.\n"
        "- **Velocidad de fase vs velocidad de grupo.** Cada modo $k$ "
        "tiene velocidad de fase $v_\\phi = \\hbar k / (2m)$ y velocidad "
        "de grupo $v_g = d\\omega/dk = \\hbar k / m = p/m$. La velocidad "
        "del grupo coincide con la velocidad clásica $p/m$ — el "
        "**centro del paquete sigue la trayectoria newtoniana**, "
        "aunque el paquete se ensanche a su alrededor.\n"
        "- **No hay estados estacionarios normalizables.** A diferencia "
        "del pozo y del oscilador, no existen autoestados $L^2$ del "
        "Hamiltoniano libre — el espectro es **puramente continuo** "
        "$E = \\hbar^2 k^2/(2m) \\ge 0$. Las \"autofunciones\" "
        "$e^{ikx}$ no pertenecen a $L^2$ (son distribuciones)."
    )

