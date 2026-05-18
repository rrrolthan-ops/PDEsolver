"""Tests for the deterministic natural-language parser.

The LLM fallback is mocked in `test_llm_classifier.py`; here we exercise
the regex/templating layer that handles the common textbook phrasings.
"""

from __future__ import annotations

import pytest

from app.parser import ParseError, parse_natural_language


# ---------------------------------------------------------------------------
# Spanish phrasings
# ---------------------------------------------------------------------------

def test_heat_bar_with_initial_profile():
    text = (
        "Resuelve la ecuación del calor en una barra de longitud L con "
        "extremos a temperatura cero y perfil inicial f(x) = sin(pi*x/L)."
    )
    res = parse_natural_language(text)
    assert res.source == "deterministic"
    p = res.problem
    assert p.equation_kind == "heat"
    assert p.domain.x == ["0", "L"]
    assert len(p.boundary_conditions) == 2
    assert all(bc.type == "dirichlet" and bc.value == "0" for bc in p.boundary_conditions)
    assert p.initial_conditions[0].value == "sin(pi*x/L)"


def test_heat_bar_without_initial_profile():
    """If f(x) is not specified, we leave it as f(x) and note that."""
    text = "Ecuación del calor en una barra de longitud L con extremos a cero."
    res = parse_natural_language(text)
    assert res.problem.initial_conditions[0].value == "f(x)"


def test_wave_string_fixed_ends():
    text = (
        "Cuerda fija de longitud L con perfil inicial f(x) = sin(pi*x/L) "
        "y velocidad inicial cero."
    )
    res = parse_natural_language(text)
    assert res.source == "deterministic"
    assert res.problem.equation_kind == "wave"
    assert res.problem.domain.x == ["0", "L"]
    # Two ICs (position + velocity)
    assert len(res.problem.initial_conditions) == 2


def test_wave_infinite_line():
    """D'Alembert: wave equation on the real line."""
    text = "Ecuación de onda en la recta entera, con condición inicial f(x) = exp(-x^2)."
    res = parse_natural_language(text)
    assert res.source == "deterministic"
    assert res.problem.domain.x == ["-infty", "infty"]
    assert res.problem.boundary_conditions == []
    assert res.problem.initial_conditions[0].value == "exp(-x^2)"


def test_laplace_disk():
    text = (
        "Resuelve Laplace en un disco de radio R con dato en el borde "
        "f(theta) = cos(theta)."
    )
    res = parse_natural_language(text)
    assert res.source == "deterministic"
    assert res.problem.geometry == "disk"
    assert res.problem.boundary_conditions[0].where == "r=R"
    assert res.problem.boundary_conditions[0].value == "cos(theta)"


def test_drum():
    text = "Tambor circular de radio R que vibra con perfil inicial 1 - (r/R)^2."
    res = parse_natural_language(text)
    assert res.source == "deterministic"
    assert res.problem.geometry == "disk"
    assert res.problem.equation_kind == "wave"
    assert "(u_{rr} + u_r/r)" in res.problem.equation_latex


def test_schrodinger_well():
    text = "Partícula en una caja unidimensional (pozo infinito) de longitud L."
    res = parse_natural_language(text)
    assert res.source == "deterministic"
    assert res.problem.equation_kind == "schrodinger"
    assert "hbar" in res.problem.equation_latex


def test_transport_with_initial_profile():
    text = "Ecuación de transporte 1D con perfil inicial f(x) = exp(-x^2)."
    res = parse_natural_language(text)
    assert res.source == "deterministic"
    # Transport has no equation_kind enum; uses general
    assert "u_t + c*u_x" in res.problem.equation_latex
    assert res.problem.initial_conditions[0].value == "exp(-x^2)"


# ---------------------------------------------------------------------------
# English phrasings
# ---------------------------------------------------------------------------

def test_heat_english():
    text = (
        "Solve the heat equation on a bar of length L with fixed ends "
        "and initial profile f(x) = sin(pi*x/L)."
    )
    res = parse_natural_language(text)
    assert res.source == "deterministic"
    assert res.problem.equation_kind == "heat"


def test_wave_english_string():
    text = "Wave equation on a string of length L with fixed ends, initial profile sin(pi*x/L)."
    res = parse_natural_language(text)
    assert res.source == "deterministic"
    assert res.problem.equation_kind == "wave"


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_empty_input_raises():
    with pytest.raises(ParseError):
        parse_natural_language("")


def test_unrecognized_falls_back_or_raises(monkeypatch):
    """If LLM isn't available, unrecognized input must raise ParseError."""
    monkeypatch.setattr("app.parser.llm_classifier.is_available", lambda: False)
    with pytest.raises(ParseError):
        parse_natural_language(
            "Cuéntame un chiste sobre topología algebraica."
        )
