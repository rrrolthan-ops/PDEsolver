"""HTTP endpoint for natural-language parsing.

POST /parse_natural turns a free-text problem statement into a
canonical `PDEProblem`. The frontend then shows the parsed problem to
the user for confirmation before invoking /solve. The LLM never solves
anything; it only classifies.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.parser import ParseError, parse_natural_language
from app.schemas import PDEProblem

router = APIRouter(prefix="", tags=["parse"])


class NaturalLanguageRequest(BaseModel):
    text: str


class NaturalLanguageResponse(BaseModel):
    problem: PDEProblem
    source: str  # "deterministic" | "llm:<model>"
    notes: str | None = None


@router.post("/parse_natural", response_model=NaturalLanguageResponse)
def parse_natural(req: NaturalLanguageRequest) -> NaturalLanguageResponse:
    """Parse natural-language input into a structured `PDEProblem`."""
    try:
        result = parse_natural_language(req.text)
    except ParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return NaturalLanguageResponse(
        problem=result.problem,
        source=result.source,
        notes=result.notes,
    )
