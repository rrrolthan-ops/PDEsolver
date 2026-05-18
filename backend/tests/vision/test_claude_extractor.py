"""Tests for the Claude-vision extractor (mocked Anthropic SDK)."""

from __future__ import annotations

import io
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from PIL import Image

from app.schemas import PDEProblem
from app.vision import claude_extractor


def _png_bytes() -> bytes:
    img = Image.new("RGB", (100, 100), color="white")
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
        "transcribed_latex": r"u_t = \alpha^2 u_{xx}, \quad u(0, t) = u(L, t) = 0",
        "confidence": "high",
    }


def _fake_response(tool_input: dict) -> SimpleNamespace:
    return SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", input=tool_input)],
        usage=SimpleNamespace(
            cache_read_input_tokens=0,
            cache_creation_input_tokens=0,
        ),
    )


@pytest.fixture
def fake_client():
    recorded: dict = {}

    class FakeMessages:
        def create(self, **kwargs):
            recorded.update(kwargs)
            return _fake_response(recorded["_next_tool_input"])

    class FakeClient:
        def __init__(self, **_):
            self.messages = FakeMessages()

    return FakeClient, recorded


def test_extract_returns_none_without_api_key(monkeypatch):
    monkeypatch.setattr(claude_extractor, "is_available", lambda: False)
    assert claude_extractor.extract(_png_bytes()) is None


def test_extract_returns_problem_and_transcription(monkeypatch, fake_client):
    FakeClient, recorded = fake_client
    monkeypatch.setattr(claude_extractor, "is_available", lambda: True)
    monkeypatch.setattr(
        claude_extractor, "settings", SimpleNamespace(anthropic_api_key="sk-test")
    )
    with patch("anthropic.Anthropic", FakeClient):
        recorded["_next_tool_input"] = _heat_tool_input()
        result = claude_extractor.extract(_png_bytes())

    assert result is not None
    assert isinstance(result.problem, PDEProblem)
    assert result.problem.equation_kind == "heat"
    assert "alpha" in result.transcribed_latex
    assert result.confidence == "high"
    # The image block was sent
    msg = recorded["messages"][0]
    content_types = [c["type"] for c in msg["content"]]
    assert "image" in content_types
    # The tool was forced
    assert recorded["tool_choice"]["name"] == "record_pde_problem_from_image"
    # System prompt is cache-marked
    assert recorded["system"][0]["cache_control"] == {"type": "ephemeral"}


def test_low_confidence_passes_through(monkeypatch, fake_client):
    FakeClient, recorded = fake_client
    monkeypatch.setattr(claude_extractor, "is_available", lambda: True)
    monkeypatch.setattr(
        claude_extractor, "settings", SimpleNamespace(anthropic_api_key="sk-test")
    )
    with patch("anthropic.Anthropic", FakeClient):
        bad = _heat_tool_input()
        bad["confidence"] = "low"
        bad["notes"] = "Foto borrosa; revisar con cuidado."
        recorded["_next_tool_input"] = bad
        result = claude_extractor.extract(_png_bytes())
    assert result is not None
    assert result.confidence == "low"
    assert result.notes == "Foto borrosa; revisar con cuidado."


def test_invalid_schema_returns_none(monkeypatch, fake_client):
    """If Claude emits an unparseable PDEProblem, return None."""
    FakeClient, recorded = fake_client
    monkeypatch.setattr(claude_extractor, "is_available", lambda: True)
    monkeypatch.setattr(
        claude_extractor, "settings", SimpleNamespace(anthropic_api_key="sk-test")
    )
    with patch("anthropic.Anthropic", FakeClient):
        recorded["_next_tool_input"] = {
            # missing required `equation_latex`
            "equation_kind": "heat",
            "domain": {"x": ["0", "L"]},
            "boundary_conditions": [],
            "initial_conditions": [],
            "parameters": {},
            "transcribed_latex": "",
            "confidence": "low",
        }
        result = claude_extractor.extract(_png_bytes())
    assert result is None


def test_user_hint_appended(monkeypatch, fake_client):
    FakeClient, recorded = fake_client
    monkeypatch.setattr(claude_extractor, "is_available", lambda: True)
    monkeypatch.setattr(
        claude_extractor, "settings", SimpleNamespace(anthropic_api_key="sk-test")
    )
    with patch("anthropic.Anthropic", FakeClient):
        recorded["_next_tool_input"] = _heat_tool_input()
        claude_extractor.extract(_png_bytes(), user_hint="Es la ecuación del calor.")
    user_msg = recorded["messages"][0]
    text_blocks = [c["text"] for c in user_msg["content"] if c["type"] == "text"]
    assert any("Contexto adicional" in t for t in text_blocks)
