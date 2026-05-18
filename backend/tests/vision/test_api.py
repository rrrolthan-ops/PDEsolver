"""Smoke tests for /vision/extract via FastAPI's TestClient."""

from __future__ import annotations

import io
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.vision import claude_extractor

client = TestClient(app)


def _png_bytes() -> bytes:
    img = Image.new("RGB", (120, 80), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _heat_tool_input() -> dict:
    return {
        "equation_latex": "u_t = alpha^2 * u_{xx}",
        "equation_kind": "heat",
        "domain": {"x": ["0", "L"], "t": ["0", "infty"]},
        "boundary_conditions": [
            {"type": "dirichlet", "where": "x=0", "value": "0"},
            {"type": "dirichlet", "where": "x=L", "value": "0"},
        ],
        "initial_conditions": [{"order": 0, "value": "sin(pi*x/L)"}],
        "parameters": {"alpha": "positive", "L": "positive"},
        "transcribed_latex": r"u_t = \alpha^2 u_{xx}",
        "confidence": "high",
    }


class _FakeMessages:
    def create(self, **_):
        return SimpleNamespace(
            content=[SimpleNamespace(type="tool_use", input=_heat_tool_input())],
            usage=SimpleNamespace(
                cache_read_input_tokens=0, cache_creation_input_tokens=0
            ),
        )


class _FakeClient:
    def __init__(self, **_):
        self.messages = _FakeMessages()


def test_vision_extract_endpoint(monkeypatch):
    monkeypatch.setattr(claude_extractor, "is_available", lambda: True)
    monkeypatch.setattr(
        claude_extractor, "settings", SimpleNamespace(anthropic_api_key="sk-test")
    )
    with patch("anthropic.Anthropic", _FakeClient):
        files = {"file": ("photo.png", _png_bytes(), "image/png")}
        r = client.post("/vision/extract", files=files)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["problem"]["equation_kind"] == "heat"
    assert body["confidence"] == "high"
    assert "alpha" in body["transcribed_latex"]
    # The preprocessed JPEG preview should round-trip as a data URL.
    assert body["image_preview_data_url"].startswith("data:image/jpeg;base64,")
    assert body["engine"].startswith("claude-vision:")


def test_vision_extract_empty_upload_returns_400(monkeypatch):
    monkeypatch.setattr(claude_extractor, "is_available", lambda: True)
    monkeypatch.setattr(
        claude_extractor, "settings", SimpleNamespace(anthropic_api_key="sk-test")
    )
    files = {"file": ("empty.png", b"", "image/png")}
    r = client.post("/vision/extract", files=files)
    assert r.status_code == 400


def test_vision_extract_unsupported_mime_returns_415(monkeypatch):
    monkeypatch.setattr(claude_extractor, "is_available", lambda: True)
    files = {"file": ("doc.pdf", b"%PDF-1.4 fake", "application/pdf")}
    r = client.post("/vision/extract", files=files)
    assert r.status_code == 415
    assert "PDF" in r.json()["detail"] or "soportado" in r.json()["detail"].lower()


def test_vision_extract_no_api_key_returns_503(monkeypatch):
    monkeypatch.setattr(claude_extractor, "is_available", lambda: False)
    files = {"file": ("photo.png", _png_bytes(), "image/png")}
    r = client.post("/vision/extract", files=files)
    assert r.status_code == 503


def test_vision_extract_passes_hint(monkeypatch):
    """The user's free-text hint is forwarded into the Claude call."""
    captured: dict = {}

    class _RecordingMessages:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                content=[SimpleNamespace(type="tool_use", input=_heat_tool_input())],
                usage=SimpleNamespace(
                    cache_read_input_tokens=0, cache_creation_input_tokens=0
                ),
            )

    class _RecordingClient:
        def __init__(self, **_):
            self.messages = _RecordingMessages()

    monkeypatch.setattr(claude_extractor, "is_available", lambda: True)
    monkeypatch.setattr(
        claude_extractor, "settings", SimpleNamespace(anthropic_api_key="sk-test")
    )
    with patch("anthropic.Anthropic", _RecordingClient):
        files = {"file": ("photo.png", _png_bytes(), "image/png")}
        data = {"hint": "Es la ecuación del calor."}
        r = client.post("/vision/extract", files=files, data=data)
    assert r.status_code == 200
    user_msg = captured["messages"][0]
    text_blocks = [c["text"] for c in user_msg["content"] if c["type"] == "text"]
    assert any("Contexto adicional" in t for t in text_blocks)
