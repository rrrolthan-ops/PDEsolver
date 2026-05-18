"""Symbolic PDE solver — the pedagogical core of the app.

We deliberately keep this `__init__` minimal: importing the solver
package must NOT eagerly drag the whole pipeline + methods chain in,
because the parser (which the methods themselves use) imports symbols
from `solver.core.symbols`, and a circular import would block startup.

Use `from app.solver.pipeline import solve` for the public entry point.
The `solve` symbol is also re-exported here lazily for convenience.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.schemas import PDEProblem, SolutionResponse, Step

if TYPE_CHECKING:
    from .pipeline import solve  # noqa: F401  (typing only)


def solve(problem: "PDEProblem") -> "SolutionResponse":  # type: ignore[no-redef]
    """Lazy facade over `app.solver.pipeline.solve` to avoid circular imports."""
    from .pipeline import solve as _solve  # local import breaks the cycle
    return _solve(problem)


__all__ = ["PDEProblem", "SolutionResponse", "Step", "solve"]
