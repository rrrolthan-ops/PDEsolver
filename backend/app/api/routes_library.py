"""HTTP endpoints for the saved-problem library.

Four operations:

    POST   /library          — save a solved problem
    GET    /library          — list saved problems (optional filter)
    GET    /library/{id}     — retrieve a full record (problem + steps)
    DELETE /library/{id}     — remove an entry

The library is single-user and stores everything as JSON in SQLite.
Authentication is intentionally absent; this app runs locally.
"""

from __future__ import annotations

import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_session
from app.schemas import (
    LibraryItem,
    LibraryListItem,
    LibrarySaveRequest,
)

router = APIRouter(prefix="/library", tags=["library"])

# Human-friendly Spanish labels for the auto-generated entry name.
_KIND_LABELS = {
    "heat": "Calor",
    "wave": "Onda",
    "laplace": "Laplace",
    "poisson": "Poisson",
    "helmholtz": "Helmholtz",
    "schrodinger": "Schrödinger",
    "telegraph": "Telégrafo",
    "biharmonic": "Biarmónica",
    "general": "EDP",
}


@router.post("", response_model=LibraryItem)
def save_entry(
    req: LibrarySaveRequest,
    db: Annotated[Session, Depends(get_session)],
) -> LibraryItem:
    """Save a solved problem. Returns the persisted record."""
    now = dt.datetime.now(dt.UTC).replace(tzinfo=None)
    name = req.name or _default_name(req, now)
    entry = models.LibraryEntry(
        name=name,
        problem_json=req.problem.model_dump_json(),
        solution_json=req.solution.model_dump_json(),
        equation_kind=req.problem.equation_kind,
        method_slug=req.solution.method,
        source=req.source,
        image_data_url=req.image_data_url,
        created_at=now,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _to_full_item(entry)


@router.get("", response_model=list[LibraryListItem])
def list_entries(
    db: Annotated[Session, Depends(get_session)],
    equation_kind: str | None = Query(default=None, description="Filter by EDP kind."),
    method: str | None = Query(default=None, description="Filter by method slug."),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[LibraryListItem]:
    """List saved problems, newest first."""
    q = db.query(models.LibraryEntry).order_by(models.LibraryEntry.created_at.desc())
    if equation_kind:
        q = q.filter(models.LibraryEntry.equation_kind == equation_kind)
    if method:
        q = q.filter(models.LibraryEntry.method_slug == method)
    rows = q.limit(limit).all()
    return [_to_list_item(r) for r in rows]


@router.get("/{entry_id}", response_model=LibraryItem)
def get_entry(
    entry_id: str,
    db: Annotated[Session, Depends(get_session)],
) -> LibraryItem:
    entry = db.query(models.LibraryEntry).filter_by(id=entry_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Entrada no encontrada.")
    return _to_full_item(entry)


@router.delete("/{entry_id}", status_code=204)
def delete_entry(
    entry_id: str,
    db: Annotated[Session, Depends(get_session)],
) -> None:
    entry = db.query(models.LibraryEntry).filter_by(id=entry_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Entrada no encontrada.")
    db.delete(entry)
    db.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _default_name(req: LibrarySaveRequest, when: dt.datetime) -> str:
    """Generate a human-readable name when the user didn't supply one.

    Format: "<KindLabel> — <YYYY-MM-DD HH:MM>". Predictable enough to
    sort, descriptive enough to scan in a list view.
    """
    kind_label = _KIND_LABELS.get(req.problem.equation_kind, "EDP")
    return f"{kind_label} — {when.strftime('%Y-%m-%d %H:%M')}"


def _to_list_item(entry: models.LibraryEntry) -> LibraryListItem:
    return LibraryListItem(
        id=entry.id,
        name=entry.name,
        equation_kind=entry.equation_kind,
        method_slug=entry.method_slug,
        source=entry.source,  # type: ignore[arg-type]
        image_data_url=entry.image_data_url,
        created_at=entry.created_at,
    )


def _to_full_item(entry: models.LibraryEntry) -> LibraryItem:
    # The JSON columns are stored as text; Pydantic re-validates on load.
    from app.schemas import PDEProblem, SolutionResponse

    return LibraryItem(
        id=entry.id,
        name=entry.name,
        problem=PDEProblem.model_validate_json(entry.problem_json),
        solution=SolutionResponse.model_validate_json(entry.solution_json),
        equation_kind=entry.equation_kind,
        method_slug=entry.method_slug,
        source=entry.source,  # type: ignore[arg-type]
        image_data_url=entry.image_data_url,
        created_at=entry.created_at,
    )
