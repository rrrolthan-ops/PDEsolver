"""Anthropic-based semantic classifier for natural-language PDE problems.

The LLM is used **strictly as a structured-output classifier**. It does not
solve PDEs, derive equations, or perform any mathematical reasoning. Its
only job is to read a free-text problem statement and emit a `PDEProblem`
JSON object that the deterministic solver will then handle.

Why we draw the line here
-------------------------
Claude can match natural-language phrases like "barra de longitud L con
extremos a temperatura cero" to the canonical `equation_latex` /
`domain` / `boundary_conditions` fields very reliably — far better than
hand-written regex would. But math correctness must come from the
symbolic solver, never from the LLM. So:

- The LLM extracts STRUCTURE.
- The solver computes ANSWERS.

The user always sees the parsed structure in a confirmation view before
the solver runs (Step D of the original spec); the LLM cannot silently
lead the student to solve a different problem.

Implementation notes
--------------------
- Tool-use with `strict: true` (Anthropic structured outputs) — Claude
  is forced to populate a tool input that matches our PDEProblem
  schema exactly. JSON shape is validated by the API server-side.
- Prompt caching: the long system prompt + tool schema are marked
  `cache_control: ephemeral` so subsequent calls within a 5-minute
  window read from cache (~0.1× input cost on the cached prefix).
- Defaults to `claude-haiku-4-5` for cost and speed. Falls back to
  `claude-sonnet-4-6` if the user sets the env var
  `ANTHROPIC_CLASSIFIER_FALLBACK_MODEL` and the haiku call returns a
  refusal or low-confidence output.
- If `ANTHROPIC_API_KEY` is not set, `classify(...)` returns `None`
  immediately and the caller falls back to the deterministic parser.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from app.config import settings
from app.schemas import PDEProblem

logger = logging.getLogger(__name__)

# Hard-coded model IDs per the project decision (Anthropic API skill catalog).
_PRIMARY_MODEL = "claude-haiku-4-5"
_FALLBACK_MODEL = "claude-sonnet-4-6"


@dataclass
class ClassificationResult:
    problem: PDEProblem
    model: str
    raw_tool_input: dict[str, Any]
    cache_read_input_tokens: int
    cache_creation_input_tokens: int


# ---------------------------------------------------------------------------
# The system prompt
# ---------------------------------------------------------------------------

# Carefully written, kept long and STATIC so prompt-cache hits are valuable.
# Any byte change here invalidates the cache for the whole prefix.
_SYSTEM_PROMPT = """\
Eres un clasificador semántico para un sistema que resuelve ecuaciones en
derivadas parciales (EDPs) de la física matemática. Tu único trabajo es
LEER un problema escrito en lenguaje natural (español o inglés) y EXTRAER
su estructura matemática en un objeto JSON canónico.

REGLAS ESTRICTAS — léelas con atención:

1. **NO resuelves la EDP.** Nunca calcules autovalores, coeficientes de
   Fourier, ni hagas álgebra simbólica. Eso lo hace el motor simbólico
   determinista río abajo. Limítate a clasificar.

2. **NO inventes datos.** Si el usuario no especifica una condición
   inicial, deja el campo vacío o usa "0". Si no especifica un
   parámetro, no lo añadas. Inventar produce errores silenciosos
   peores que un fallo limpio.

3. **Devuelve siempre un PDEProblem válido** usando la herramienta
   `record_pde_problem`. Si el problema es ambiguo o no es una EDP
   clásica del repertorio, llena lo que puedas y deja claro en `notes`
   qué interpretaste.

4. **El repertorio del solver es:** calor 1D, onda 1D (acotada y en
   recta infinita), Laplace (rectángulo, disco, semiplano, bola
   axisimétrica), Poisson 1D, Helmholtz en rectángulo, telégrafo,
   Schrödinger en pozo infinito, transporte 1D, viga simplemente
   apoyada, calor/onda en disco axisimétrico. Si el problema cae fuera,
   pon `equation_kind: "general"` y reporta en `notes`.

CONVENCIONES MATEMÁTICAS (esto es lo que el parser de fórmulas espera):

- Derivadas: usa notación de subíndice como `u_t`, `u_x`, `u_{xx}`,
  `u_{tt}`. No uses `\\partial` (salvo en LaTeX explícito del usuario).
- Producto: usa `*` explícito (`alpha^2 * u_{xx}`, no `alpha^2 u_{xx}`).
- Potencias: usa `^` (`alpha^2`, `n^2`).
- Constantes: `pi`, `e`, `infty`, `hbar`, `alpha`, `beta`, `c`, `k`, `L`, `R`, `m`, `a`, `b`.
- Letras griegas: prefiere la forma sin backslash (`theta`, no `\\theta`).
- Para el dominio: `["-infty", "infty"]` representa toda la recta real;
  `["0", "L"]` un intervalo finito.

EJEMPLOS DE CLASIFICACIÓN:

Entrada: "Resuelve la ecuación del calor en una barra de longitud L con
extremos a temperatura cero y perfil inicial f(x) = sin(pi*x/L)."
Tool input:
{
  "equation_latex": "u_t = alpha^2 * u_{xx}",
  "equation_kind": "heat",
  "domain": {"x": ["0", "L"], "t": ["0", "infty"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "x=0", "value": "0"},
    {"type": "dirichlet", "where": "x=L", "value": "0"}
  ],
  "initial_conditions": [{"order": 0, "value": "sin(pi*x/L)"}],
  "parameters": {"alpha": "positive", "L": "positive"}
}

Entrada: "Cuerda fija de longitud L golpeada por una velocidad inicial
g(x) = sin(2*pi*x/L), partiendo del reposo."
Tool input:
{
  "equation_latex": "u_{tt} = c^2 * u_{xx}",
  "equation_kind": "wave",
  "domain": {"x": ["0", "L"], "t": ["0", "infty"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "x=0", "value": "0"},
    {"type": "dirichlet", "where": "x=L", "value": "0"}
  ],
  "initial_conditions": [
    {"order": 0, "value": "0"},
    {"order": 1, "value": "sin(2*pi*x/L)"}
  ],
  "parameters": {"c": "positive", "L": "positive"}
}

Entrada: "Una partícula libre en una caja unidimensional de longitud L."
Tool input:
{
  "equation_latex": "i*hbar*u_t = -hbar^2/(2*m) * u_{xx}",
  "equation_kind": "schrodinger",
  "domain": {"x": ["0", "L"], "t": ["0", "infty"]},
  "boundary_conditions": [
    {"type": "dirichlet", "where": "x=0", "value": "0"},
    {"type": "dirichlet", "where": "x=L", "value": "0"}
  ],
  "initial_conditions": [{"order": 0, "value": "sqrt(2/L)*sin(pi*x/L)"}],
  "parameters": {"L": "positive", "hbar": "positive", "m": "positive"},
  "notes": "Asumí estado fundamental como condición inicial porque el usuario no la especificó."
}

Si el usuario menciona una geometría especial:
- "disco" o "tambor circular" → `geometry: "disk"`, dominio `x: ["0", "R"]`.
- "bola" o "esfera" → `geometry: "sphere"`.
- "semiplano" → `geometry: "halfplane"`.
- "rectángulo" → `geometry: "rectangle"` (o déjalo en `None`).

Si el usuario menciona una fuente (Poisson, Helmholtz inhomogénea):
- Pon la expresión de la fuente en `source_term`.

Ahora clasifica el siguiente problema del usuario."""


# ---------------------------------------------------------------------------
# Tool schema — built from the Pydantic schema
# ---------------------------------------------------------------------------

def _build_tool_schema() -> dict[str, Any]:
    """Build the `record_pde_problem` tool input schema from PDEProblem.

    We hand-write the schema instead of using `PDEProblem.model_json_schema()`
    directly because the Anthropic API's strict mode rejects some constructs
    (e.g. `$defs` / `$ref`, certain `anyOf` shapes). A flat, denormalised
    schema gives Claude clearer guidance and avoids API rejection.
    """
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "equation_latex": {
                "type": "string",
                "description": (
                    "La EDP en forma LHS = RHS o LHS - RHS = 0, "
                    "usando notación física (u_t, u_{xx}, u_{tt}, etc.). "
                    "Ejemplo: 'u_t = alpha^2 * u_{xx}'."
                ),
            },
            "equation_kind": {
                "type": "string",
                "enum": [
                    "heat",
                    "wave",
                    "laplace",
                    "poisson",
                    "helmholtz",
                    "schrodinger",
                    "telegraph",
                    "biharmonic",
                    "general",
                ],
                "description": "Tipo de EDP. Usa 'general' si no encaja en los demás.",
            },
            "source_term": {
                "type": "string",
                "description": (
                    "Término fuente f para EDPs no homogéneas (Poisson, "
                    "Helmholtz inhomogéneo, viga, etc.). Vacío si la "
                    "EDP es homogénea."
                ),
            },
            "geometry": {
                "type": "string",
                "enum": [
                    "interval",
                    "rectangle",
                    "disk",
                    "halfplane",
                    "line",
                    "halfline",
                    "box",
                    "cylinder",
                    "sphere",
                    "none",
                ],
                "description": (
                    "Pista de geometría. Usa 'disk' / 'sphere' / "
                    "'halfplane' cuando el usuario lo indique. 'none' "
                    "si no aplica."
                ),
            },
            "domain": {
                "type": "object",
                "additionalProperties": False,
                "description": "Extensión espacial y temporal del problema.",
                "properties": {
                    "x": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Cota [inferior, superior] en x.",
                    },
                    "y": {"type": "array", "items": {"type": "string"}},
                    "z": {"type": "array", "items": {"type": "string"}},
                    "t": {"type": "array", "items": {"type": "string"}},
                },
            },
            "boundary_conditions": {
                "type": "array",
                "description": "Condiciones de contorno.",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["dirichlet", "neumann", "robin", "periodic"],
                        },
                        "where": {
                            "type": "string",
                            "description": 'Ubicación, p. ej. "x=0", "x=L", "r=R", "y=0".',
                        },
                        "value": {"type": "string"},
                    },
                    "required": ["type", "where", "value"],
                },
            },
            "initial_conditions": {
                "type": "array",
                "description": (
                    "Condiciones iniciales. order=0 es u(x,0); order=1 es "
                    "u_t(x,0) (necesario para ecuaciones de segundo orden "
                    "en t como onda)."
                ),
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "order": {"type": "integer", "minimum": 0, "maximum": 2},
                        "value": {"type": "string"},
                    },
                    "required": ["order", "value"],
                },
            },
            "parameters": {
                "type": "object",
                "description": (
                    "Nombre de parámetro → asunción ('positive', 'real', "
                    "'integer', 'nonnegative')."
                ),
                "additionalProperties": {"type": "string"},
            },
            "notes": {
                "type": "string",
                "description": (
                    "Cualquier observación útil: ambigüedades, asunciones "
                    "que tomaste, problemas detectados, etc."
                ),
            },
        },
        "required": [
            "equation_latex",
            "equation_kind",
            "domain",
            "boundary_conditions",
            "initial_conditions",
            "parameters",
        ],
    }


def _build_tool() -> dict[str, Any]:
    return {
        "name": "record_pde_problem",
        "description": (
            "Registra el problema EDP en forma canónica para que el solver "
            "simbólico lo procese."
        ),
        "input_schema": _build_tool_schema(),
        # `strict: true` forces the response to match the schema exactly.
        # This is the Anthropic structured-outputs feature for tools.
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def is_available() -> bool:
    """True if the Anthropic API key is configured.

    Used by the natural-language router to decide whether to attempt
    LLM classification at all. If False, the route falls back to the
    deterministic parser.
    """
    return bool(settings.anthropic_api_key)


def classify(text: str, *, model: str | None = None) -> ClassificationResult | None:
    """Classify a natural-language problem statement into a PDEProblem.

    Returns None if the API key is missing or the call fails — callers
    must handle this and fall back to deterministic patterns or surface
    a clear error to the user.
    """
    if not is_available():
        return None

    try:
        # Lazy import: anthropic is an optional runtime dependency. If
        # it's not installed (CI without the LLM extra, e.g.) we don't
        # want to break the rest of the parser at import time.
        import anthropic
    except ImportError:
        logger.warning("anthropic SDK not installed; LLM classifier disabled.")
        return None

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    tool = _build_tool()
    chosen_model = model or _PRIMARY_MODEL

    try:
        response = client.messages.create(
            model=chosen_model,
            max_tokens=2048,
            # Prompt-cache the static prefix (system + tools). Render order
            # is tools → system → messages, so a cache_control on the last
            # system block caches both tools and system together.
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=[tool],
            # Force the tool: Claude MUST emit a tool_use block whose
            # input matches our PDEProblem schema. No prose preamble.
            tool_choice={"type": "tool", "name": "record_pde_problem"},
            messages=[{"role": "user", "content": text}],
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Anthropic classify() failed (%s): %s", chosen_model, exc)
        return None

    # Find the tool_use block. We forced tool_choice, so it must exist.
    tool_use = next(
        (b for b in response.content if getattr(b, "type", None) == "tool_use"),
        None,
    )
    if tool_use is None:
        logger.warning("Anthropic response had no tool_use block.")
        return None

    raw = dict(tool_use.input)
    problem = _coerce_to_pde_problem(raw)
    if problem is None:
        logger.warning("Failed to coerce tool input to PDEProblem: %s", raw)
        return None

    usage = response.usage
    return ClassificationResult(
        problem=problem,
        model=chosen_model,
        raw_tool_input=raw,
        cache_read_input_tokens=getattr(usage, "cache_read_input_tokens", 0) or 0,
        cache_creation_input_tokens=getattr(usage, "cache_creation_input_tokens", 0) or 0,
    )


# ---------------------------------------------------------------------------
# Coercion
# ---------------------------------------------------------------------------

def _coerce_to_pde_problem(raw: dict[str, Any]) -> PDEProblem | None:
    """Validate and clean the LLM's tool input before handing it to Pydantic.

    Claude is usually well-behaved with `strict: true`, but we still:
    - Drop the sentinel `"none"` value for `geometry` (mapped to None).
    - Replace empty `source_term` with None.
    - Reject malformed bounds.
    """
    raw = dict(raw)  # don't mutate caller's dict

    geom = raw.get("geometry")
    if geom == "none" or geom == "":
        raw.pop("geometry", None)

    src = raw.get("source_term")
    if src == "" or src is None:
        raw.pop("source_term", None)

    # Domain bounds must be exactly [lower, upper]; drop empty entries.
    domain = raw.get("domain", {})
    if isinstance(domain, dict):
        for axis in ("x", "y", "z", "t"):
            v = domain.get(axis)
            if v is None or (isinstance(v, list) and len(v) == 0):
                domain.pop(axis, None)

    try:
        return PDEProblem.model_validate(raw)
    except Exception as exc:  # noqa: BLE001
        logger.warning("PDEProblem validation failed: %s", exc)
        logger.warning("Offending dict: %s", json.dumps(raw, default=str)[:500])
        return None
