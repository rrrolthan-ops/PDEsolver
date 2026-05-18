"""Tests for the Claude-based LLM classifier.

We mock `anthropic.Anthropic` so the tests don't require a real API key
and don't make network calls. The point is to validate:

- The classifier produces a valid `PDEProblem` from a faked tool_use response.
- It returns None when there's no API key.
- It returns None on tool-use absence or schema-validation failure.
- Coercion strips sentinel values like geometry='none' and empty source_term.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.parser import llm_classifier
from app.schemas import PDEProblem


def _fake_response(tool_input: dict) -> SimpleNamespace:
    """Build a mock Anthropic Message-like response with a single tool_use block."""
    tool_use_block = SimpleNamespace(type="tool_use", input=tool_input)
    usage = SimpleNamespace(
        cache_read_input_tokens=0,
        cache_creation_input_tokens=0,
        input_tokens=100,
        output_tokens=200,
    )
    return SimpleNamespace(content=[tool_use_block], usage=usage)


@pytest.fixture
def fake_client():
    """Yields a `(client_obj, recorded_kwargs)` tuple via context."""
    recorded: dict = {}

    class FakeMessages:
        def create(self, **kwargs):
            recorded.update(kwargs)
            return _fake_response(recorded["_next_tool_input"])

    class FakeClient:
        def __init__(self, **_):
            self.messages = FakeMessages()

    return FakeClient, recorded


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
    }


def test_classify_returns_none_without_api_key(monkeypatch):
    monkeypatch.setattr(llm_classifier, "is_available", lambda: False)
    assert llm_classifier.classify("anything") is None


def test_classify_returns_pde_problem_with_mocked_client(monkeypatch, fake_client):
    FakeClient, recorded = fake_client
    monkeypatch.setattr(llm_classifier, "is_available", lambda: True)
    monkeypatch.setattr(
        llm_classifier, "settings", SimpleNamespace(anthropic_api_key="sk-test")
    )

    # Inject the fake Anthropic class via the import inside `classify`.
    with patch("anthropic.Anthropic", FakeClient):
        recorded["_next_tool_input"] = _heat_tool_input()
        result = llm_classifier.classify("Resuelve calor 1D.")

    assert result is not None
    assert isinstance(result.problem, PDEProblem)
    assert result.problem.equation_kind == "heat"
    # Verify cache_control was applied to the system prompt block
    sys_blocks = recorded.get("system", [])
    assert isinstance(sys_blocks, list)
    assert sys_blocks[0].get("cache_control") == {"type": "ephemeral"}
    # Verify tool_choice forces our specific tool
    assert recorded["tool_choice"] == {
        "type": "tool",
        "name": "record_pde_problem",
    }


def test_geometry_none_sentinel_is_stripped(monkeypatch, fake_client):
    """The LLM may emit 'geometry': 'none' to indicate 'no hint'."""
    FakeClient, recorded = fake_client
    monkeypatch.setattr(llm_classifier, "is_available", lambda: True)
    monkeypatch.setattr(
        llm_classifier, "settings", SimpleNamespace(anthropic_api_key="sk-test")
    )
    with patch("anthropic.Anthropic", FakeClient):
        recorded["_next_tool_input"] = {**_heat_tool_input(), "geometry": "none"}
        result = llm_classifier.classify("...")
    assert result is not None
    assert result.problem.geometry is None


def test_invalid_tool_input_returns_none(monkeypatch, fake_client):
    """Malformed inputs that fail Pydantic validation cause the classifier to bail."""
    FakeClient, recorded = fake_client
    monkeypatch.setattr(llm_classifier, "is_available", lambda: True)
    monkeypatch.setattr(
        llm_classifier, "settings", SimpleNamespace(anthropic_api_key="sk-test")
    )
    with patch("anthropic.Anthropic", FakeClient):
        # missing required `equation_latex`
        recorded["_next_tool_input"] = {
            "equation_kind": "heat",
            "domain": {"x": ["0", "L"]},
            "boundary_conditions": [],
            "initial_conditions": [],
            "parameters": {},
        }
        result = llm_classifier.classify("...")
    assert result is None


def test_tool_schema_has_required_fields():
    schema = llm_classifier._build_tool_schema()
    required = set(schema["required"])
    assert {
        "equation_latex",
        "equation_kind",
        "domain",
        "boundary_conditions",
        "initial_conditions",
        "parameters",
    } <= required
