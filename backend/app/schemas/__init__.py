"""Pydantic schemas shared across the API and the solver."""

from .problem import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from .solution import DetailLevel, SolutionResponse, Step, StepKind

__all__ = [
    "BoundaryCondition",
    "DetailLevel",
    "Domain",
    "InitialCondition",
    "PDEProblem",
    "SolutionResponse",
    "Step",
    "StepKind",
]
