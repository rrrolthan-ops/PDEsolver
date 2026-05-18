"""SQLAlchemy session + engine.

SQLite is the default; the file lives under `backend/data/`. The path
comes from `DATABASE_URL` so tests can swap it for `sqlite:///:memory:`.

Why SQLite (and not e.g. Postgres)
----------------------------------
This is an educational app run by one student at a time. SQLite is:
- Zero-configuration (no daemon, no auth, no schema migration tooling
  required for a single-user load).
- Embeddable — works in the Docker container with no extra service.
- Plenty fast for the read pattern (open library page, view item).

If the project ever grows multi-user, swapping to Postgres is a one-line
change in `DATABASE_URL`; the SQLAlchemy code path is identical.
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


def _build_engine_url() -> str:
    url = settings.database_url
    # Ensure the parent directory exists for file-based SQLite.
    if url.startswith("sqlite:///") and not url.endswith(":memory:"):
        # Path after "sqlite:///" is filesystem-relative.
        path = url.replace("sqlite:///", "", 1)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    return url


_ENGINE = create_engine(
    _build_engine_url(),
    # SQLite needs check_same_thread=False to let FastAPI's worker
    # threads share the connection (each request still has its own
    # Session via `get_session`).
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE)
Base = declarative_base()


def get_session():
    """FastAPI dependency that yields a transactional `Session`.

    The session is closed at the end of the request, regardless of
    whether the route raised or succeeded.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Create any missing tables. Called at app startup."""
    # Import models to register them with `Base.metadata`. The import has
    # the side-effect of registering tables; the symbols are unused here.
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=_ENGINE)
