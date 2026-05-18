"""Vision pipeline — image upload → LaTeX + canonical PDEProblem.

Architecture
============

```
upload (JPG / PNG / WEBP)
    │
    ▼
preprocess.py        ── Pillow: EXIF orient, downscale, JPEG re-encode
    │                  (opcional: opencv-python para deskew / Otsu)
    ▼
claude_extractor.py  ── Claude vision + tool use: transcribe + structure
    │                  (alternativas pluggables: pix2tex, Nougat, Mathpix)
    ▼
pipeline.py          ── glue + image-preview data URL
    │
    ▼
VisionExtractionResult  → /vision/extract response
                        → frontend confirmation panel
                        → /solve (after user approves)
```

Why Claude vision is the default backend
----------------------------------------
The original spec listed pix2tex → Nougat → Mathpix. Claude vision wasn't
in that list because the project plan predates the maturity of Claude's
math reading. In practice it is:

- **More accurate on handwriting and pizarra photos** than pix2tex.
- **Multilingual** (Spanish prose around the formula works fine).
- **Already authenticated** (we have `ANTHROPIC_API_KEY` from Phase 3).
- **Single call** returns transcription + structured PDEProblem with a
  confidence rating — saving the chain `pix2tex → text classifier`.

The pix2tex / Nougat / Mathpix paths remain valid for users who want
fully offline pipelines, deterministic OCR, or paid OCR with SLAs. To
add one:

1. Write a parallel `app/vision/<engine>_extractor.py` that returns
   the same `VisionResult` dataclass as `claude_extractor`.
2. Register it in `pipeline.extract_from_image` with a dispatch on
   `settings` (e.g. `MATHPIX_API_KEY` set → use Mathpix).
3. Add a test that mocks the engine SDK.
"""

from .pipeline import (
    VisionExtractionError,
    VisionUnavailableError,
    extract_from_image,
)

__all__ = [
    "VisionExtractionError",
    "VisionUnavailableError",
    "extract_from_image",
]
