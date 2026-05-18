"""Claude as math-OCR + structurer.

A single Claude call:
1. Sees the image (vision-capable model).
2. Transcribes the math verbatim as LaTeX (so the student can
   compare with the original photo, the pedagogical contract).
3. Structures the transcription into a canonical PDEProblem via
   tool use (same schema as the natural-language classifier).
4. Self-rates its confidence so the UI can warn on `low`.

Why one call instead of OCR-then-classify
----------------------------------------
Claude vision is already a strong math reader. Splitting into two
calls (pix2tex → text classifier) costs more, doubles the surfaces of
error, and loses the cross-information between the visual layout and
the structural classification (e.g. the model can disambiguate
`u_xx` vs `u_x x` from how tightly the subscripts are written). One
call is faster, cheaper, and more accurate for our use case.

The pix2tex / Nougat / Mathpix paths from the original spec stay
**documented as alternatives** in `app/vision/__init__.py` for users
who want a fully offline pipeline or who prefer a deterministic OCR
backend. They're not implemented in Phase 4 — switching them on is a
matter of writing a parallel `extractor.py` and registering it in
`pipeline.py`.
"""

from __future__ import annotations

import base64
import logging
from dataclasses import dataclass
from typing import Any, Literal

from app.config import settings
from app.parser.llm_classifier import _build_tool_schema  # reuse
from app.schemas import PDEProblem
from app.schemas.vision import Confidence

logger = logging.getLogger(__name__)


_PRIMARY_MODEL = "claude-haiku-4-5"
_FALLBACK_MODEL = "claude-sonnet-4-6"

ImageMediaType = Literal["image/jpeg", "image/png", "image/webp", "image/gif"]


@dataclass
class VisionResult:
    problem: PDEProblem
    transcribed_latex: str
    confidence: Confidence
    model: str
    notes: str | None


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
Eres un asistente que LEE problemas de ecuaciones en derivadas parciales
(EDPs) desde imágenes — fotos de páginas de libro, exámenes, pizarras o
apuntes — y los traduce a estructura matemática canónica para un solver
simbólico.

Tu trabajo consta de TRES partes — todas obligatorias en cada llamada:

1. **Transcribe** la fórmula visible al campo `transcribed_latex` como
   LaTeX limpio, lo más fiel posible a lo que ves. Incluye la EDP, el
   dominio, las condiciones de contorno e iniciales, y los parámetros
   que aparezcan.

2. **Estructura** el problema en el resto de los campos
   (`equation_latex`, `equation_kind`, `domain`, `boundary_conditions`,
   `initial_conditions`, `parameters`, `geometry`, `source_term`).

3. **Califica tu confianza** en `confidence`:
   - `high` — fórmula impresa nítida, todos los símbolos legibles.
   - `medium` — algunos símbolos requirieron inferir contexto pero el
     resultado es razonablemente fiable.
   - `low` — manuscrito difícil, foto borrosa, ambigüedades serias.
     El usuario debe revisar con cuidado.

Reglas estrictas — léelas con atención:

a. **NO resuelves la EDP.** Sólo transcribes y estructuras. El motor
   simbólico determinista resolverá después.

b. **NO inventes datos.** Si la imagen no especifica una condición
   inicial, deja `f(x)` como placeholder y reporta en `notes` que el
   estudiante debe llenarla. Inventar es peor que pedir aclaración.

c. **Notación física esperada por el parser:**
   - Derivadas con subíndice: `u_t`, `u_x`, `u_{xx}`, `u_{tt}`. No
     uses `\\partial` (salvo en `transcribed_latex`, donde sí puedes
     reflejar lo que escribe el autor).
   - Productos explícitos con `*`. Potencias con `^`.
   - Letras griegas sin backslash en los campos estructurados
     (`theta`, no `\\theta`). En `transcribed_latex` puedes mantener
     el formato original.
   - Constantes conocidas: `pi`, `e`, `infty`, `hbar`, `alpha`, `beta`,
     `c`, `k`, `L`, `R`, `m`, `a`, `b`.

d. **Repertorio del solver:** calor 1D, onda 1D (acotada e infinita),
   Laplace (rectángulo, disco, semiplano, bola axisimétrica), Poisson
   1D, Helmholtz en rectángulo, telégrafo, Schrödinger pozo infinito,
   transporte 1D, viga simplemente apoyada, calor/onda en disco
   axisimétrico. Si la imagen muestra algo fuera del repertorio,
   reporta `equation_kind: "general"` y explícalo en `notes`.

e. **Si la imagen contiene varios sub-problemas** (a, b, c, …),
   resuelve sólo el primero y menciona los demás en `notes` para que
   el usuario los procese uno a uno.

Llama siempre a la herramienta `record_pde_problem_from_image` — no
respondas en texto libre."""


# ---------------------------------------------------------------------------
# Tool schema — extends the text classifier's schema with vision-specific fields
# ---------------------------------------------------------------------------

def _build_vision_tool_schema() -> dict[str, Any]:
    """Same as `record_pde_problem` schema + transcription + confidence."""
    schema = _build_tool_schema()
    props = dict(schema["properties"])
    props["transcribed_latex"] = {
        "type": "string",
        "description": (
            "LaTeX verbatim de lo que aparece en la imagen, lo más fiel "
            "posible al original. Para que el estudiante compare con la "
            "foto antes de resolver."
        ),
    }
    props["confidence"] = {
        "type": "string",
        "enum": ["high", "medium", "low"],
        "description": "Auto-evaluación de la fiabilidad de la lectura.",
    }
    required = list(schema["required"]) + ["transcribed_latex", "confidence"]
    return {
        **schema,
        "properties": props,
        "required": required,
    }


_TOOL = {
    "name": "record_pde_problem_from_image",
    "description": (
        "Registra el problema EDP leído de una imagen, junto con la "
        "transcripción literal en LaTeX y una auto-evaluación de "
        "confianza."
    ),
    "input_schema": _build_vision_tool_schema(),
}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def is_available() -> bool:
    return bool(settings.anthropic_api_key)


def extract(
    image_bytes: bytes,
    *,
    media_type: ImageMediaType = "image/jpeg",
    user_hint: str | None = None,
    model: str | None = None,
) -> VisionResult | None:
    """Extract a PDEProblem + transcription from an image via Claude vision.

    Returns None if the API key is missing or the call fails. Callers
    should handle this and surface a clear error to the user.

    `user_hint` is optional free-text context the user typed alongside
    the upload — useful when the photo is ambiguous and the user
    knows the answer ("this is the heat equation in 1D").
    """
    if not is_available():
        return None

    try:
        import anthropic
    except ImportError:
        logger.warning("anthropic SDK missing; vision extractor disabled.")
        return None

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    chosen_model = model or _PRIMARY_MODEL

    b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    user_text_blocks = [
        {
            "type": "text",
            "text": (
                "Lee la imagen adjunta. Transcríbela en `transcribed_latex` "
                "y estructura el problema PDE en los campos del tool. "
                "Califica tu confianza."
            ),
        },
    ]
    if user_hint:
        user_text_blocks.append(
            {
                "type": "text",
                "text": f"Contexto adicional del usuario: {user_hint}",
            }
        )

    try:
        response = client.messages.create(
            model=chosen_model,
            max_tokens=2048,
            # Cache the system prompt and tool definition. They are
            # static across all vision uploads, so subsequent uploads
            # within the 5-minute window read the prefix from cache.
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=[_TOOL],
            tool_choice={
                "type": "tool",
                "name": "record_pde_problem_from_image",
            },
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": b64,
                            },
                        },
                        *user_text_blocks,
                    ],
                }
            ],
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Claude vision extract() failed (%s): %s", chosen_model, exc)
        return None

    tool_use = next(
        (b for b in response.content if getattr(b, "type", None) == "tool_use"),
        None,
    )
    if tool_use is None:
        logger.warning("Vision response had no tool_use block.")
        return None

    raw = dict(tool_use.input)
    transcribed = raw.pop("transcribed_latex", "")
    confidence = raw.pop("confidence", "medium")
    notes = raw.get("notes")

    problem = _coerce_to_pde_problem(raw)
    if problem is None:
        return None

    return VisionResult(
        problem=problem,
        transcribed_latex=transcribed,
        confidence=confidence if confidence in ("high", "medium", "low") else "low",
        model=chosen_model,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Coercion
# ---------------------------------------------------------------------------

def _coerce_to_pde_problem(raw: dict[str, Any]) -> PDEProblem | None:
    """Same cleanup as the text classifier."""
    raw = dict(raw)
    if raw.get("geometry") in ("none", ""):
        raw.pop("geometry", None)
    if raw.get("source_term") in ("", None):
        raw.pop("source_term", None)
    domain = raw.get("domain", {})
    if isinstance(domain, dict):
        for axis in ("x", "y", "z", "t"):
            v = domain.get(axis)
            if v is None or (isinstance(v, list) and len(v) == 0):
                domain.pop(axis, None)
    try:
        return PDEProblem.model_validate(raw)
    except Exception as exc:  # noqa: BLE001
        logger.warning("PDEProblem validation from vision failed: %s", exc)
        return None
