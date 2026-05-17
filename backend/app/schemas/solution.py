"""Solution schemas: the structured step-by-step output the API returns.

The whole pedagogical contract lives in `Step`. Every solver method
produces a list of these and nothing else — that way the frontend
renders them uniformly regardless of which method was used.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


DetailLevel = Literal["basic", "intermediate", "exhaustive"]


StepKind = Literal[
    "statement",          # Paso 0 — restatement of the problem
    "classification",     # Paso 1 — discriminant, type
    "method_choice",      # Paso 2 — why this method
    "development",        # Paso 3 — main symbolic work
    "boundary",           # Paso 4 — apply BCs
    "initial",            # Paso 5 — apply ICs (Fourier coefficients)
    "final",              # Paso 6 — closed form / series
    "verification",       # Paso 7 — substitute back and check
    "visualization",      # Paso 8 — plots + convergence
    "interpretation",     # Paso 9 — physical meaning
    "observation",        # standalone didactic note (rare; usually attached to a step)
]


class DidacticObservation(BaseModel):
    """A marginal note pointing at something that typically confuses students.

    `kind` lets the frontend style them differently
    ("watch out" vs "intuition" vs "theorem statement").
    """

    kind: Literal["pitfall", "intuition", "theorem", "alternative"] = "intuition"
    text_md: str


class Step(BaseModel):
    """One pedagogical step.

    Attributes
    ----------
    kind
        Coarse category — see `StepKind`. Used by the frontend to assign
        a chapter heading ("Paso 3 — Desarrollo") and an icon.
    title
        Short title shown on the card header.
    explanation_md
        Plain prose in Markdown explaining *why* this step happens.
        Pure narrative — no algebra here, algebra goes in `latex`.
    latex
        The mathematics for this step, ready to feed into KaTeX.
        Multi-line content uses `\\\\` separators inside an `align*`
        environment built by the frontend, but we emit the raw lines.
    sympy_repr
        `srepr` (or `str`) of the SymPy object that produced this step.
        Useful for debugging and for tests that want to inspect the
        algebraic state without re-parsing LaTeX.
    observations
        Didactic notes attached to this step (the famous "Observación
        didáctica" boxes).
    level
        The lowest detail level at which this step should be shown:
        - "basic":        always shown
        - "intermediate": shown on intermediate and exhaustive
        - "exhaustive":   shown only on exhaustive
        The frontend filters by `level <= user_choice`.
    """

    kind: StepKind
    title: str
    explanation_md: str = ""
    latex: str = ""
    sympy_repr: str | None = None
    observations: list[DidacticObservation] = Field(default_factory=list)
    level: DetailLevel = "basic"


class SolutionResponse(BaseModel):
    """What the `/solve` endpoint returns.

    Includes both the pedagogical steps and the raw data needed by the
    frontend to render plots without re-querying the backend.
    """

    method: str = Field(description="Slug of the method that produced the solution.")
    steps: list[Step]

    # Final closed-form (or series-truncated) solution as a LaTeX string,
    # repeated outside the step list for easy access from the UI.
    solution_latex: str

    # Symbolic representation of the solution for downstream tools.
    solution_sympy_repr: str | None = None

    # Optional numerical sampling used by the frontend's Plotly chart.
    # Filled in by `solver.numerics`.
    plot_data: dict | None = None

    # Convergence study: how the partial sum looks with N = 1, 5, 20, 100 terms.
    convergence_data: dict | None = None

    # `True` if symbolic verification confirmed the solution satisfies
    # the PDE and all conditions. `False` otherwise; details live in the
    # relevant verification steps.
    verified: bool = False
