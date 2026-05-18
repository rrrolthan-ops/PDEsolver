"""SQLAlchemy ORM models for the problem library."""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import Column, DateTime, String, Text

from .session import Base


def _new_id() -> str:
    """Short opaque ID for library entries (12 hex chars from a uuid4)."""
    return uuid.uuid4().hex[:12]


class LibraryEntry(Base):
    """A saved problem-and-solution pair.

    We store the full `PDEProblem` and `SolutionResponse` as JSON
    columns so the schema does not need to know about every solver
    output detail. The structured columns (`equation_kind`,
    `method_slug`, `source`) are denormalised from the JSON to make
    filtering cheap.

    `image_data_url` carries the (preprocessed) original image when
    the problem came from `/vision/extract`, so the library list can
    show miniatures. Stored as a base64 data URL string — convenient
    for SQLite (no blob handling) and trivially renderable in the
    frontend's `<img src>`.
    """

    __tablename__ = "library_entries"

    id = Column(String(32), primary_key=True, default=_new_id)
    name = Column(String(256), nullable=False)

    #: Full `PDEProblem` as JSON-serialised text.
    problem_json = Column(Text, nullable=False)

    #: Full `SolutionResponse` as JSON-serialised text.
    solution_json = Column(Text, nullable=False)

    #: Denormalised, indexable filters.
    equation_kind = Column(String(64), nullable=False, index=True)
    method_slug = Column(String(64), nullable=False, index=True)
    source = Column(String(32), nullable=False)  # manual | natural | vision

    #: Optional original-image preview (data URL). Only set for
    #: problems uploaded as photos.
    image_data_url = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=False),
        default=lambda: dt.datetime.now(dt.UTC).replace(tzinfo=None),
        nullable=False,
        index=True,
    )
