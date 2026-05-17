"""Symbolic PDE solver — the pedagogical core of the app.

The public surface is intentionally small:

- `solve(problem)`: top-level entry that picks a method and runs it.
- `Step`, `SolutionResponse`: the structured pedagogical output.

Everything else (method classes, pedagogy templates, verification)
is internal to this package.
"""

from app.schemas import PDEProblem, SolutionResponse, Step

from .pipeline import solve

__all__ = ["PDEProblem", "SolutionResponse", "Step", "solve"]
