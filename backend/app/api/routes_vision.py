"""HTTP endpoint for image-based PDE extraction.

POST /vision/extract takes a multipart upload (an image file plus an
optional `hint` text field) and returns a `VisionExtractionResult` —
the structured `PDEProblem` plus a verbatim LaTeX transcription and a
confidence rating. The frontend then shows the original image
side-by-side with the transcription for the user to confirm before
calling /solve.
"""

from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas import VisionExtractionResult
from app.vision import (
    VisionExtractionError,
    VisionUnavailableError,
    extract_from_image,
)

router = APIRouter(prefix="/vision", tags=["vision"])

#: Cap on uploaded image size (bytes). 12 MB covers a 50 MP phone photo
#: post-EXIF-rotation while staying well under typical proxy limits.
_MAX_UPLOAD_BYTES = 12 * 1024 * 1024

_ALLOWED_MIMES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/heic",
}


@router.post("/extract", response_model=VisionExtractionResult)
async def extract_endpoint(
    file: UploadFile = File(..., description="Image of the PDE problem (JPG/PNG/WEBP)."),
    hint: str | None = Form(default=None, description="Optional free-text context."),
) -> VisionExtractionResult:
    """Extract a PDEProblem from an uploaded image via Claude vision."""
    content_type = (file.content_type or "").lower()
    if content_type and content_type not in _ALLOWED_MIMES:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Tipo de archivo no soportado: {content_type}. "
                "Sube una imagen JPG, PNG, WEBP, GIF o HEIC. Los PDFs "
                "todavía no son soportados directamente (Fase 4 cubre "
                "imágenes; PDFs llegarán al añadir pdf2image)."
            ),
        )

    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Archivo vacío.")
    if len(image_bytes) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"La imagen es demasiado grande ({len(image_bytes)/1e6:.1f} MB). "
                f"Máximo permitido: {_MAX_UPLOAD_BYTES/1e6:.0f} MB."
            ),
        )

    try:
        return extract_from_image(
            image_bytes,
            content_type=content_type or None,
            user_hint=hint,
        )
    except VisionUnavailableError as exc:
        # 503: server-side configuration issue, not user input. Client
        # can retry once `ANTHROPIC_API_KEY` is set.
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except VisionExtractionError as exc:
        # 422: the upload itself is the problem (blurry, off-repertoire).
        # The detail message tells the user what to fix.
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"Fallo en el pipeline de visión: {exc}"
        ) from exc
