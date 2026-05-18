"""Vision pipeline orchestrator.

End-to-end flow:

    image bytes  →  preprocess  →  extractor (Claude)  →  VisionExtractionResult

Each stage is replaceable. To plug in a different OCR backend
(pix2tex / Nougat / Mathpix), write a parallel module with the same
shape as `claude_extractor.extract()` and dispatch from here.
"""

from __future__ import annotations

import base64
import logging

from app.schemas.vision import VisionExtractionResult

from . import claude_extractor, preprocess as preprocess_module

logger = logging.getLogger(__name__)


class VisionUnavailableError(Exception):
    """Raised when no extractor backend is configured."""


class VisionExtractionError(Exception):
    """Raised when extraction fails for reasons unrelated to availability."""


def extract_from_image(
    image_bytes: bytes,
    *,
    content_type: str | None = None,
    user_hint: str | None = None,
) -> VisionExtractionResult:
    """Run the full pipeline and return a confirmation-ready result.

    The returned object includes:
    - The structured `PDEProblem` (ready for `/solve`).
    - The verbatim `transcribed_latex` for side-by-side review.
    - A `confidence` rating the frontend can use to warn the student.
    - A data-URL preview of the (preprocessed) image so the frontend
      can render it without uploading separately.
    """
    if not claude_extractor.is_available():
        raise VisionUnavailableError(
            "El clasificador visual no está disponible. Para activarlo, "
            "configura la variable de entorno ANTHROPIC_API_KEY (el "
            "modelo claude-haiku-4-5 lee la imagen y estructura el "
            "problema). Sin API key, el modo 'Subir foto' está "
            "deshabilitado; usa el modo 'Escribir' o 'Lenguaje natural'."
        )

    # 1. Preprocess. We always normalise to JPEG even if the user uploaded
    #    PNG/WEBP — it keeps the API call shape stable and shrinks the
    #    upload size for large images.
    processed_bytes = preprocess_module.preprocess(
        image_bytes, content_type=content_type
    )

    # 2. Extract via Claude vision.
    result = claude_extractor.extract(
        processed_bytes,
        media_type="image/jpeg",
        user_hint=user_hint,
    )
    if result is None:
        raise VisionExtractionError(
            "El clasificador visual no logró estructurar la imagen. "
            "Razones probables: foto demasiado borrosa o de baja "
            "resolución, contenido fuera del repertorio de EDPs "
            "soportadas, o un fallo transitorio del servicio. "
            "Mejora la foto (iluminación uniforme, encuadre perpendicular "
            "a la página, suficiente resolución) o transcríbela "
            "manualmente con el modo 'Escribir'."
        )

    # 3. Build the preview data URL so the frontend can render the
    #    (preprocessed) image alongside the LaTeX transcription.
    preview_b64 = base64.standard_b64encode(processed_bytes).decode("ascii")
    preview_data_url = f"data:image/jpeg;base64,{preview_b64}"

    return VisionExtractionResult(
        problem=result.problem,
        transcribed_latex=result.transcribed_latex,
        confidence=result.confidence,
        engine=f"claude-vision:{result.model}",
        image_preview_data_url=preview_data_url,
        notes=result.notes,
    )
