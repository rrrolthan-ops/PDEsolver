"""Schemas for the vision extraction pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .problem import PDEProblem


Confidence = Literal["high", "medium", "low"]


class VisionExtractionResult(BaseModel):
    """What the `/vision/extract` endpoint returns.

    The `problem` is the same canonical `PDEProblem` that `/parse_natural`
    returns, so the same confirmation-then-solve flow works for both
    input modes.

    Additionally, vision extractions carry:

    - `transcribed_latex` — verbatim LaTeX as read from the image, for
      side-by-side comparison with the original photo. Crucial for the
      pedagogical contract: the student must see what we **think** the
      image says before we go solve it.
    - `confidence` — self-rated quality (high / medium / low). The
      frontend surfaces a warning for `low`.
    - `engine` — which OCR backend produced this. Phase 4 ships
      `"claude-vision"` only; the field exists so future
      pix2tex / Nougat / Mathpix paths can be distinguished.
    - `image_preview_data_url` — the (possibly preprocessed) image as
      a data URL, so the frontend can render it alongside the LaTeX
      transcription without a separate fetch.
    - `notes` — human-readable warnings (blurry image, ambiguous
      symbols, missing initial condition, etc.).
    """

    problem: PDEProblem
    transcribed_latex: str = Field(
        description="Verbatim LaTeX as read from the image."
    )
    confidence: Confidence
    engine: str = "claude-vision"
    image_preview_data_url: str | None = None
    notes: str | None = None
