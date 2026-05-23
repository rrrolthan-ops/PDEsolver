"""Schemas for the problem-library API."""

from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

from .problem import PDEProblem
from .solution import SolutionResponse

LibrarySource = Literal["manual", "natural", "vision"]


class LibrarySaveRequest(BaseModel):
    """Body for POST /library."""

    name: str | None = Field(
        default=None,
        max_length=256,
        description=(
            "Display name. If omitted, the server generates one from the "
            "equation kind and timestamp (e.g. 'Calor 1D — 2026-05-18 14:32')."
        ),
    )
    problem: PDEProblem
    solution: SolutionResponse
    source: LibrarySource = "manual"
    image_data_url: str | None = Field(
        default=None,
        description=(
            "Optional preview of the original image (only relevant when "
            "source == 'vision'). Base64 data URL — typically what "
            "/vision/extract already returned."
        ),
    )


class LibraryListItem(BaseModel):
    """Compact row for the library list view.

    Excludes the full `solution_json` to keep the listing endpoint
    fast — fetching a single item via `/library/{id}` returns the
    full record.
    """

    id: str
    name: str
    equation_kind: str
    method_slug: str
    source: LibrarySource
    image_data_url: str | None = None
    created_at: dt.datetime


class LibraryItem(BaseModel):
    """Full library record (returned by GET /library/{id})."""

    id: str
    name: str
    problem: PDEProblem
    solution: SolutionResponse
    equation_kind: str
    method_slug: str
    source: LibrarySource
    image_data_url: str | None = None
    created_at: dt.datetime
