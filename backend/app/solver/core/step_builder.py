"""Small helpers to assemble `Step` objects without boilerplate.

The solver code constructs *many* steps. Without these helpers the
method modules drown in `Step(kind=..., title=..., explanation_md=...,
latex=..., level=...)` calls and the pedagogical intent gets lost in
the noise. These helpers make each step a one-liner whose pedagogical
purpose is visible at a glance.
"""

from __future__ import annotations

from collections.abc import Iterable

import sympy as sp

from app.schemas import DetailLevel, Step, StepKind
from app.schemas.solution import DidacticObservation


def step(
    kind: StepKind,
    title: str,
    *,
    md: str = "",
    latex: str | sp.Basic | None = None,
    sympy_expr: sp.Basic | None = None,
    level: DetailLevel = "basic",
    observations: Iterable[DidacticObservation] = (),
) -> Step:
    """Build a `Step` with sensible defaults.

    Either `latex` (string or SymPy expression) or `sympy_expr` may be
    supplied. If `sympy_expr` is given and `latex` is not, we render
    the SymPy expression to LaTeX automatically. If both are given the
    string `latex` wins (useful when we want a multi-line `aligned`
    block that SymPy's renderer cannot produce on its own).
    """
    latex_str: str = ""
    if isinstance(latex, str):
        latex_str = latex
    elif isinstance(latex, sp.Basic):
        latex_str = sp.latex(latex)
    elif sympy_expr is not None:
        latex_str = sp.latex(sympy_expr)

    return Step(
        kind=kind,
        title=title,
        explanation_md=md,
        latex=latex_str,
        sympy_repr=sp.srepr(sympy_expr) if sympy_expr is not None else None,
        observations=list(observations),
        level=level,
    )


def observation(text_md: str, kind: str = "intuition") -> DidacticObservation:
    """Shorthand for a didactic observation attached to a step."""
    return DidacticObservation(kind=kind, text_md=text_md)


def equation_chain(lines: list[str]) -> str:
    r"""Format a list of LaTeX lines as an `aligned` environment.

    Each line should already include an alignment marker (`&`) or be a
    plain expression. We wrap them in `\begin{aligned}...\end{aligned}`
    so the frontend can render them inside a display block with
    `\\\\` separators. This is the workhorse for "show every algebraic
    intermediate" — pass the chain of manipulations as a list.
    """
    body = " \\\\\n".join(lines)
    return r"\begin{aligned}" + "\n" + body + "\n" + r"\end{aligned}"
