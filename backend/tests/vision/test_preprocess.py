"""Tests for the Pillow-based preprocessing step."""

from __future__ import annotations

import io

from PIL import Image

from app.vision.preprocess import preprocess


def _make_test_image(size: tuple[int, int], format: str = "PNG") -> bytes:
    """Build a synthetic image as raw bytes."""
    img = Image.new("RGB", size, color=(220, 220, 220))
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def test_preprocess_returns_jpeg_bytes():
    raw = _make_test_image((400, 300), "PNG")
    out = preprocess(raw)
    # JPEG magic
    assert out[:3] == b"\xff\xd8\xff"


def test_preprocess_downscales_huge_image():
    raw = _make_test_image((5000, 3000), "PNG")
    out = preprocess(raw)
    out_img = Image.open(io.BytesIO(out))
    assert max(out_img.size) <= 2048


def test_preprocess_preserves_small_image():
    raw = _make_test_image((800, 600), "PNG")
    out = preprocess(raw)
    out_img = Image.open(io.BytesIO(out))
    assert out_img.size == (800, 600)


def test_preprocess_converts_rgba_to_rgb():
    img = Image.new("RGBA", (200, 200), color=(255, 0, 0, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    out = preprocess(buf.getvalue())
    out_img = Image.open(io.BytesIO(out))
    assert out_img.mode == "RGB"
