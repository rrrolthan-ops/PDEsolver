"""Canonical PDE problem schema.

This is the *single* internal representation that every input mode
(direct LaTeX, natural language, image OCR) must eventually produce
before being handed to the solver. Keeping it strict and explicit is
what lets us swap input modes without rewriting the solver.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Domain
# ---------------------------------------------------------------------------

class Domain(BaseModel):
    """Spatial and temporal extent of the problem.

    Each axis maps to a `[lower, upper]` pair. Bounds can be numeric
    strings or symbolic expressions ("L", "infty"). We keep them as raw
    strings here because they may reference parameters declared
    separately in `PDEProblem.parameters`.
    """

    x: list[str] | None = Field(
        default=None,
        description="Spatial bounds along x, e.g. ['0', 'L'].",
    )
    y: list[str] | None = None
    z: list[str] | None = None
    t: list[str] | None = Field(
        default=None,
        description="Time bounds, typically ['0', 'infty'].",
    )

    @field_validator("x", "y", "z", "t")
    @classmethod
    def _check_pair(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        if len(v) != 2:
            raise ValueError("Each axis must be exactly [lower, upper].")
        return v


# ---------------------------------------------------------------------------
# Boundary / initial conditions
# ---------------------------------------------------------------------------

BCType = Literal["dirichlet", "neumann", "robin", "periodic"]


class BoundaryCondition(BaseModel):
    """One boundary condition.

    Examples
    --------
    Dirichlet at x = 0:
        BoundaryCondition(type="dirichlet", where="x=0", value="0")

    Neumann at x = L (zero flux):
        BoundaryCondition(type="neumann", where="x=L", value="0")

    Robin at x = L:
        BoundaryCondition(type="robin", where="x=L",
                          value="0", coefficients={"a": "1", "b": "h"})
    """

    type: BCType
    where: str = Field(description='Locus, e.g. "x=0", "x=L", "boundary".')
    value: str = Field(description="RHS of the condition as a string.")
    coefficients: dict[str, str] | None = Field(
        default=None,
        description="For Robin: a*u + b*u_n = value, store a and b here.",
    )


class InitialCondition(BaseModel):
    """One initial condition, given as the time-derivative `order` evaluated at t=0.

    - order=0 → u(x, 0) = value
    - order=1 → u_t(x, 0) = value   (used by the wave equation)
    """

    order: int = Field(ge=0, le=2, default=0)
    value: str


# ---------------------------------------------------------------------------
# Top-level problem
# ---------------------------------------------------------------------------

EquationKind = Literal[
    "heat",
    "wave",
    "laplace",
    "poisson",
    "helmholtz",
    "schrodinger",
    "telegraph",
    "biharmonic",
    "general",
]


Geometry = Literal[
    "interval",
    "rectangle",
    "disk",
    "halfplane",
    "line",
    "halfline",
    "box",
    "cylinder",
    "sphere",
]


class PDEProblem(BaseModel):
    """A fully specified PDE problem.

    `equation_latex` is the human-facing string; the solver re-parses it
    through `app.parser.latex_to_sympy` to obtain a SymPy expression.

    `equation_kind` is a hint for the method picker. If the user does
    not provide it, the classifier in `solver.core.classify` will fill
    it in by inspecting the parsed expression.
    """

    equation_latex: str = Field(description="LHS - RHS = 0 form or LHS = RHS form.")
    equation_kind: EquationKind = "general"

    #: Optional explicit source term for non-homogeneous problems
    #: (Poisson `∇²u = f`, forced wave/heat, etc.). When given as a
    #: separate field the method picker can route to Green-function or
    #: variation-of-parameters approaches without having to back out the
    #: RHS from `equation_latex`.
    source_term: str | None = None

    #: Optional geometry hint. Lets the picker distinguish e.g. Laplace
    #: on a rectangle (separation of variables in Cartesian) from
    #: Laplace on a disk (separation in polar). When `None`, the picker
    #: tries to infer geometry from the shape of `domain`.
    geometry: Geometry | None = None

    domain: Domain
    boundary_conditions: list[BoundaryCondition] = Field(default_factory=list)
    initial_conditions: list[InitialCondition] = Field(default_factory=list)

    # Symbol assumptions, e.g. {"alpha": "positive", "L": "positive", "n": "integer"}.
    parameters: dict[str, str] = Field(default_factory=dict)

    # Free-text notes captured from the original input (useful for image mode).
    notes: str | None = None
