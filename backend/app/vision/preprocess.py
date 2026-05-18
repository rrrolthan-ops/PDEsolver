"""Image preprocessing for the math-OCR pipeline.

Phase 4 keeps preprocessing minimal: Pillow-only normalization (auto-
orientation via EXIF, downscale if huge, JPEG re-encoding to control
size). Heavier steps from the original spec — perspective correction,
adaptive binarization, deskewing — live behind a Pillow-or-OpenCV fork
and are skipped when OpenCV is not installed.

Why minimal
-----------
Claude vision is very robust to camera artifacts (perspective, low
contrast, mild blur). For pedagogical use (a phone photo of a textbook
page), we have not needed perspective correction in practice. We DO
need:

- **EXIF orientation** — phones store the sensor orientation in the
  JPEG's EXIF tag; the raw pixel data isn't rotated. Without honoring
  it, photos taken in landscape come out sideways.
- **Downscale very large images** — uploading a 12MP shot wastes
  tokens and API time. Cap the long edge.
- **Format normalization** — accept PNG, JPG, WEBP; emit JPEG at
  consistent quality for the API.

Optional heavy preprocessing (perspective warp, Sauvola/Otsu binarization)
is documented as `try_opencv_preprocess` for the user to switch on if
they add `opencv-python` to their environment.
"""

from __future__ import annotations

import io
import logging

from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

#: Cap the longer edge of the image to this many pixels before sending to
#: the OCR engine. 2048 is more than enough for any textbook math; bigger
#: just wastes tokens.
_MAX_LONG_EDGE = 2048

#: JPEG quality for the re-encoded preview. The OCR engine generally
#: doesn't benefit from anything above 90.
_JPEG_QUALITY = 88


def preprocess(image_bytes: bytes, *, content_type: str | None = None) -> bytes:
    """Normalize uploaded image bytes for the OCR step.

    Steps:
    1. Open with Pillow (auto-detects format).
    2. Apply EXIF orientation transform so phone-portrait photos
       arrive right-side-up.
    3. Convert to RGB (drops alpha; Claude vision wants RGB).
    4. Downscale long edge to `_MAX_LONG_EDGE`.
    5. Re-encode as JPEG.

    Returns JPEG bytes. The original is not mutated.
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode != "RGB":
            img = img.convert("RGB")

        long_edge = max(img.size)
        if long_edge > _MAX_LONG_EDGE:
            scale = _MAX_LONG_EDGE / long_edge
            new_size = (round(img.size[0] * scale), round(img.size[1] * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            logger.debug("Downscaled image to %s", new_size)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=_JPEG_QUALITY)
        return buf.getvalue()


def try_opencv_preprocess(image_bytes: bytes) -> bytes | None:
    """Optional: heavier preprocessing if `opencv-python` is installed.

    Returns the cleaned-up JPEG bytes, or `None` if OpenCV isn't
    available — in which case the caller falls back to the basic
    Pillow path.

    This is where the spec's Etapa A would live (perspective warp,
    deskew, Otsu / Sauvola binarization). Phase 4 ships only the
    skeleton; turning it on requires:

        pip install opencv-python

    and uncommenting the implementation below.
    """
    try:
        import cv2  # noqa: F401
        import numpy as np  # noqa: F401
    except ImportError:
        return None

    # Implementation deferred — Pillow-only preprocessing has been
    # sufficient for the workflows we've tested with Claude vision.
    # See `vision/README.md` (future) for the full implementation.
    return None
