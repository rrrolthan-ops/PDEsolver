"""Natural-language → `PDEProblem` parser.

Strategy
--------
1. **Deterministic pattern matcher** first. Recognises the most common
   phrasings from textbook problem statements (Spanish + English) and
   produces a `PDEProblem` with high confidence — no API call needed.
2. **LLM classifier** (Claude) as a fallback for inputs that don't
   match a deterministic pattern. The LLM is constrained to a tool-use
   schema; it cannot solve the problem, only structure it.
3. **Confirmation step** is enforced upstream by the frontend: the
   parsed `PDEProblem` is always shown to the user before the solver
   runs, so any wrong classification is caught at human review.

Why a deterministic layer
-------------------------
A surprisingly large fraction of natural-language inputs follow
recognisable templates — "calor en una barra de longitud L con
extremos a cero", "Laplace en un disco con dato sin(theta) en el
borde". For those we don't pay LLM latency / cost / risk-of-error.
The LLM picks up the long tail.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.parser import llm_classifier
from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)


@dataclass
class ParseResult:
    """Outcome of a natural-language parse."""

    problem: PDEProblem
    source: str  # "deterministic" | "llm:<model>"
    notes: str | None = None


class ParseError(Exception):
    """Raised when neither layer can produce a problem."""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def parse(text: str) -> ParseResult:
    """Parse a natural-language problem into a canonical `PDEProblem`.

    Tries deterministic patterns first, then falls back to the LLM
    classifier. Raises `ParseError` if neither succeeds.
    """
    text = text.strip()
    if not text:
        raise ParseError("Texto vacío.")

    det = _deterministic_parse(text)
    if det is not None:
        return det

    llm_result = llm_classifier.classify(text)
    if llm_result is not None:
        return ParseResult(
            problem=llm_result.problem,
            source=f"llm:{llm_result.model}",
            notes=llm_result.raw_tool_input.get("notes"),
        )

    if not llm_classifier.is_available():
        raise ParseError(
            "No reconozco esta formulación con las plantillas deterministas, "
            "y no hay API key de Anthropic configurada para el clasificador "
            "LLM. Reformula el problema usando frases canónicas (p.ej. "
            "'ecuación del calor en una barra de longitud L con extremos a "
            "temperatura cero'), o configura ANTHROPIC_API_KEY."
        )
    raise ParseError(
        "El clasificador LLM no logró estructurar el problema. Intenta "
        "reformularlo con más detalle, especificando el dominio, las "
        "condiciones de contorno y las iniciales."
    )


# ---------------------------------------------------------------------------
# Deterministic patterns
# ---------------------------------------------------------------------------

def _deterministic_parse(text: str) -> ParseResult | None:
    """Try each pattern in order. First match wins."""
    lower = text.lower()
    for pattern_fn in _PATTERNS:
        result = pattern_fn(text, lower)
        if result is not None:
            return ParseResult(problem=result, source="deterministic")
    return None


# Each pattern is a function (text_original, text_lower) -> PDEProblem | None.
# Add the most specific patterns FIRST so they take precedence over
# generic ones.

def _pattern_heat_1d_bar(text: str, lower: str) -> PDEProblem | None:
    """Heat equation in a 1D bar / interval, Dirichlet 0.

    Recognises:
    - "calor en una barra de longitud L"
    - "heat equation on a bar / interval [0, L]"
    - "...con extremos a (temperatura) cero"
    - "...perfil inicial f(x) = <expr>"
    """
    heat_words = ("calor", "heat equation", "ecuación del calor", "diffusion")
    if not any(w in lower for w in heat_words):
        return None
    # Need a length / interval mention.
    if not _mentions_finite_interval(lower):
        return None
    if not _mentions_zero_boundary(lower):
        return None

    ic = _extract_initial_profile(text)
    return PDEProblem(
        equation_latex="u_t = alpha^2 * u_{xx}",
        equation_kind="heat",
        domain=Domain(x=["0", "L"], t=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=L", value="0"),
        ],
        initial_conditions=[InitialCondition(order=0, value=ic or "f(x)")],
        parameters={"alpha": "positive", "L": "positive"},
        notes=None if ic else "El usuario no especificó f(x) explícitamente.",
    )


def _pattern_wave_1d_bounded(text: str, lower: str) -> PDEProblem | None:
    """Wave equation: string of length L, fixed ends, two ICs."""
    wave_words = ("cuerda", "string", "ecuación de onda", "wave equation")
    if not any(w in lower for w in wave_words):
        return None
    if "tambor" in lower or "drum" in lower or "disco" in lower or "disk" in lower:
        # The drum is the disk problem; let that pattern catch it.
        return None
    if not _mentions_finite_interval(lower):
        return None
    if not _mentions_zero_boundary(lower):
        return None

    f = _extract_initial_profile(text)
    g = _extract_initial_velocity(text)

    return PDEProblem(
        equation_latex="u_{tt} = c^2 * u_{xx}",
        equation_kind="wave",
        domain=Domain(x=["0", "L"], t=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=L", value="0"),
        ],
        initial_conditions=[
            InitialCondition(order=0, value=f or "f(x)"),
            InitialCondition(order=1, value=g or "0"),
        ],
        parameters={"c": "positive", "L": "positive"},
    )


def _pattern_wave_unbounded(text: str, lower: str) -> PDEProblem | None:
    """D'Alembert on the infinite line."""
    if "onda" not in lower and "wave" not in lower:
        return None
    if not (
        "infinit" in lower
        or "recta entera" in lower
        or "real line" in lower
        or "all of r" in lower
    ):
        return None

    f = _extract_initial_profile(text)
    g = _extract_initial_velocity(text)
    return PDEProblem(
        equation_latex="u_{tt} = c^2 * u_{xx}",
        equation_kind="wave",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],
        initial_conditions=[
            InitialCondition(order=0, value=f or "f(x)"),
            InitialCondition(order=1, value=g or "0"),
        ],
        parameters={"c": "positive"},
    )


def _pattern_laplace_rectangle(text: str, lower: str) -> PDEProblem | None:
    """Laplace on a rectangle with Dirichlet boundary data on the top."""
    if "laplace" not in lower:
        return None
    if "rectángulo" not in lower and "rectangle" not in lower:
        return None
    # Top-boundary data:
    f_top = _extract_top_boundary(text) or "f(x)"
    return PDEProblem(
        equation_latex="u_{xx} + u_{yy} = 0",
        equation_kind="laplace",
        domain=Domain(x=["0", "a"], y=["0", "b"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=a", value="0"),
            BoundaryCondition(type="dirichlet", where="y=0", value="0"),
            BoundaryCondition(type="dirichlet", where="y=b", value=f_top),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"a": "positive", "b": "positive"},
    )


def _pattern_laplace_disk(text: str, lower: str) -> PDEProblem | None:
    """Laplace on a disk with Dirichlet data f(theta) on r=R."""
    if "laplace" not in lower:
        return None
    if "disco" not in lower and "disk" not in lower:
        return None
    f_bd = _extract_disk_boundary(text) or "f(theta)"
    return PDEProblem(
        equation_latex=r"u_{rr} + (1/r)*u_r + (1/r^2)*u_{\theta\theta} = 0",
        equation_kind="laplace",
        geometry="disk",
        domain=Domain(x=["0", "R"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="r=R", value=f_bd),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={"R": "positive"},
    )


def _pattern_drum(text: str, lower: str) -> PDEProblem | None:
    """Vibrating drum: wave on a circular membrane, axisymmetric."""
    if not ("tambor" in lower or "drum" in lower):
        return None
    f = _extract_initial_profile(text) or "1 - (r/R)^2"
    g = _extract_initial_velocity(text) or "0"
    return PDEProblem(
        equation_latex="u_{tt} = c^2 * (u_{rr} + u_r/r)",
        equation_kind="wave",
        geometry="disk",
        domain=Domain(x=["0", "R"], t=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="r=R", value="0"),
        ],
        initial_conditions=[
            InitialCondition(order=0, value=f),
            InitialCondition(order=1, value=g),
        ],
        parameters={"R": "positive", "c": "positive"},
    )


def _pattern_schrodinger_well(text: str, lower: str) -> PDEProblem | None:
    """Particle in a 1D infinite well."""
    if not ("schrödinger" in lower or "schrodinger" in lower or "pozo" in lower or "particle in a box" in lower or "infinite well" in lower):
        return None
    ic = _extract_initial_profile(text) or "sqrt(2/L)*sin(pi*x/L)"
    return PDEProblem(
        equation_latex="i*hbar*u_t = -hbar^2/(2*m) * u_{xx}",
        equation_kind="schrodinger",
        domain=Domain(x=["0", "L"], t=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="x=0", value="0"),
            BoundaryCondition(type="dirichlet", where="x=L", value="0"),
        ],
        initial_conditions=[InitialCondition(order=0, value=ic)],
        parameters={"L": "positive", "hbar": "positive", "m": "positive"},
    )


def _pattern_transport(text: str, lower: str) -> PDEProblem | None:
    """Linear transport u_t + c u_x = 0."""
    if not ("transporte" in lower or "transport" in lower or "advección" in lower or "advection" in lower):
        return None
    f = _extract_initial_profile(text) or "exp(-x^2)"
    return PDEProblem(
        equation_latex="u_t + c*u_x = 0",
        equation_kind="general",
        domain=Domain(x=["-infty", "infty"], t=["0", "infty"]),
        boundary_conditions=[],
        initial_conditions=[InitialCondition(order=0, value=f)],
        parameters={"c": "positive"},
    )


_PATTERNS = (
    _pattern_drum,             # before wave_1d_bounded (drum mentions wave/tambor)
    _pattern_wave_unbounded,   # before wave_1d_bounded
    _pattern_wave_1d_bounded,
    _pattern_heat_1d_bar,
    _pattern_laplace_disk,     # before laplace_rectangle (more specific)
    _pattern_laplace_rectangle,
    _pattern_schrodinger_well,
    _pattern_transport,
)


# ---------------------------------------------------------------------------
# Small extractors
# ---------------------------------------------------------------------------

_FINITE_INTERVAL_HINTS = (
    "longitud l",
    "length l",
    "barra",
    "bar of",
    "interval",
    "intervalo",
    "[0, l]",
    "[0,l]",
    "0 < x < l",
    "0<x<l",
)


def _mentions_finite_interval(lower: str) -> bool:
    return any(h in lower for h in _FINITE_INTERVAL_HINTS)


_ZERO_BC_HINTS = (
    "extremos a temperatura cero",
    "extremos a cero",
    "extremos fijos",
    "cuerda fija",
    "string fixed",
    "fija de",
    "fixed ends",
    "fixed at both ends",
    "ends at zero",
    "zero at the boundary",
    "dirichlet cero",
    "dirichlet zero",
    "u(0,t) = u(l,t) = 0",
    "u(0)=u(l)=0",
)


def _mentions_zero_boundary(lower: str) -> bool:
    return any(h in lower for h in _ZERO_BC_HINTS)


_PROFILE_RE = re.compile(
    r"(?:perfil\s+inicial|condici[óo]n\s+inicial|initial\s+profile|"
    r"initial\s+condition|f\s*\(\s*x\s*\)\s*=|u\s*\(\s*x\s*,\s*0\s*\)\s*=)"
    r"\s*([^,.;]+)",
    re.IGNORECASE,
)


def _extract_initial_profile(text: str) -> str | None:
    """Pull the RHS of `f(x) = ...` / `u(x, 0) = ...` from the prose."""
    m = _PROFILE_RE.search(text)
    if not m:
        return None
    raw = m.group(1).strip().rstrip(".")
    raw = _strip_function_prefix(raw)
    # Normalize trailing words like "y" / "and".
    raw = re.sub(r"\s+(y|and)\s*$", "", raw, flags=re.IGNORECASE)
    return raw or None


_FN_PREFIX_RE = re.compile(
    r"^\s*(?:f|g|u|psi|\\psi|phi|\\phi|u_t)\s*\([^)]*\)\s*=\s*",
    re.IGNORECASE,
)


def _strip_function_prefix(value: str) -> str:
    """Remove a leading `f(x) =` / `u(x, 0) =` / `g(x) =` etc.

    The prose regex matches the noun phrase ("perfil inicial",
    "initial profile") and captures everything that follows. Users
    often then write `f(x) = sin(...)`, which leaves the `f(x) =`
    inside our capture. Strip it.
    """
    return _FN_PREFIX_RE.sub("", value).strip()


_VELOCITY_RE = re.compile(
    r"(?:velocidad\s+inicial|initial\s+velocity|g\s*\(\s*x\s*\)\s*=|"
    r"u_t\s*\(\s*x\s*,\s*0\s*\)\s*=)"
    r"\s*([^,.;]+)",
    re.IGNORECASE,
)


def _extract_initial_velocity(text: str) -> str | None:
    m = _VELOCITY_RE.search(text)
    if not m:
        return None
    raw = m.group(1).strip().rstrip(".")
    return _strip_function_prefix(raw) or None


_TOP_BC_RE = re.compile(
    r"(?:lado\s+superior|top\s+side|y\s*=\s*b\s*[:=]?)\s*([^,.;]+)",
    re.IGNORECASE,
)


def _extract_top_boundary(text: str) -> str | None:
    m = _TOP_BC_RE.search(text)
    if not m:
        return None
    return _strip_function_prefix(m.group(1).strip().rstrip(".")) or None


_DISK_BC_RE = re.compile(
    r"(?:en\s+el\s+borde|en\s+la\s+circunferencia|on\s+the\s+boundary|"
    r"r\s*=\s*R\s*[:=]?)\s*([^,.;]+)",
    re.IGNORECASE,
)


def _extract_disk_boundary(text: str) -> str | None:
    m = _DISK_BC_RE.search(text)
    if not m:
        return None
    return _strip_function_prefix(m.group(1).strip().rstrip(".")) or None
