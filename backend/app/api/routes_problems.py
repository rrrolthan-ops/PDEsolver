"""HTTP endpoints for solving PDE problems."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas import PDEProblem, SolutionResponse
from app.solver import solve as solver_solve

router = APIRouter(prefix="", tags=["problems"])


@router.post("/solve", response_model=SolutionResponse)
def solve(problem: PDEProblem) -> SolutionResponse:
    """Solve a PDE problem and return the structured pedagogical output."""
    try:
        return solver_solve(problem)
    except NotImplementedError as exc:
        # The method picker couldn't match the problem to a method we know.
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        # Anything else: report it so the user understands the failure
        # rather than seeing a silent 500.
        raise HTTPException(status_code=500, detail=f"Solver error: {exc}") from exc
