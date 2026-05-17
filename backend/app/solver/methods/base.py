"""Common interface every solution method must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import sympy as sp

from app.schemas import PDEProblem, Step


@dataclass
class SolutionArtifacts:
    """Auxiliary data a method exposes alongside the step list.

    `solution_expr` is the final SymPy expression for `u(x, t)`. The
    pipeline uses it for verification, numeric sampling, and plotting.
    """

    solution_expr: sp.Basic
    solution_latex: str


class Method(ABC):
    """Base class for solution methods.

    Subclasses produce a list of `Step` objects plus the SymPy
    expression of the final solution.
    """

    #: Short slug, used for routing and for the `SolutionResponse.method` field.
    slug: str = ""

    @abstractmethod
    def solve(self, problem: PDEProblem) -> tuple[list[Step], SolutionArtifacts]:
        """Run the method and return (steps, artifacts)."""
        raise NotImplementedError
