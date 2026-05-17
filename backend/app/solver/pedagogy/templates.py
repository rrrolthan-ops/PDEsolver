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
