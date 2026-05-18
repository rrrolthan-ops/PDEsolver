"""Tests for the /library endpoints.

Each test uses an isolated in-memory SQLite database by overriding the
`get_session` dependency. The shared `TestClient` import would otherwise
pin a single file-backed DB across the suite.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import models
from app.db.session import Base, get_session
from app.main import app


@pytest.fixture
def client():
    """Spin up an isolated in-memory SQLite for one test.

    `StaticPool` keeps one connection alive so every session opened
    via `TestingSession()` sees the same in-memory database. The
    default pool gives each connection its own fresh ":memory:" DB,
    which would make our `Base.metadata.create_all` invisible to the
    test's API calls.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_get_session():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_session, None)
        engine.dispose()


# ---------------------------------------------------------------------------
# Fixtures: a solved-heat payload to save
# ---------------------------------------------------------------------------

_PROBLEM = {
    "equation_latex": "u_t = alpha^2 * u_{xx}",
    "equation_kind": "heat",
    "domain": {"x": ["0", "L"], "t": ["0", "infty"]},
    "boundary_conditions": [
        {"type": "dirichlet", "where": "x=0", "value": "0"},
        {"type": "dirichlet", "where": "x=L", "value": "0"},
    ],
    "initial_conditions": [{"order": 0, "value": "sin(pi*x/L)"}],
    "parameters": {"alpha": "positive", "L": "positive"},
}


def _save_one(client: TestClient, *, name: str | None = None, source: str = "manual"):
    """Solve a heat problem, then save the response to /library."""
    solve_r = client.post("/solve", json=_PROBLEM)
    assert solve_r.status_code == 200, solve_r.text
    solution = solve_r.json()
    save_r = client.post(
        "/library",
        json={
            "name": name,
            "problem": _PROBLEM,
            "solution": solution,
            "source": source,
        },
    )
    assert save_r.status_code == 200, save_r.text
    return save_r.json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_save_and_list(client):
    saved = _save_one(client, name="Mi calor de prueba")
    assert saved["id"]
    assert saved["name"] == "Mi calor de prueba"
    assert saved["equation_kind"] == "heat"
    assert saved["method_slug"] == "separation_of_variables"
    assert saved["source"] == "manual"

    listing = client.get("/library")
    assert listing.status_code == 200
    items = listing.json()
    assert len(items) == 1
    assert items[0]["id"] == saved["id"]
    # List view excludes full solution payload to stay light.
    assert "solution" not in items[0]


def test_get_full_item_returns_solution(client):
    saved = _save_one(client)
    r = client.get(f"/library/{saved['id']}")
    assert r.status_code == 200
    body = r.json()
    assert body["solution"]["method"] == "separation_of_variables"
    assert body["solution"]["verified"] is True
    # Steps are preserved.
    assert len(body["solution"]["steps"]) > 5


def test_default_name_when_none_supplied(client):
    saved = _save_one(client, name=None)
    # Auto-name should be like "Calor — 2026-05-18 14:32"
    assert saved["name"].startswith("Calor")
    assert "—" in saved["name"]


def test_filter_by_equation_kind(client):
    _save_one(client, name="Heat 1")
    _save_one(client, name="Heat 2")
    r = client.get("/library?equation_kind=heat")
    assert r.status_code == 200
    assert len(r.json()) == 2
    r2 = client.get("/library?equation_kind=wave")
    assert r2.status_code == 200
    assert r2.json() == []


def test_delete_entry(client):
    saved = _save_one(client)
    r = client.delete(f"/library/{saved['id']}")
    assert r.status_code == 204
    r2 = client.get(f"/library/{saved['id']}")
    assert r2.status_code == 404


def test_get_nonexistent_returns_404(client):
    r = client.get("/library/does-not-exist")
    assert r.status_code == 404


def test_save_vision_source_with_image(client):
    """A library entry from a vision upload carries the image data URL."""
    solve_r = client.post("/solve", json=_PROBLEM)
    payload = {
        "name": "Foto del libro",
        "problem": _PROBLEM,
        "solution": solve_r.json(),
        "source": "vision",
        "image_data_url": "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
    }
    r = client.post("/library", json=payload)
    assert r.status_code == 200, r.text
    saved = r.json()
    assert saved["source"] == "vision"
    assert saved["image_data_url"].startswith("data:image/jpeg")

    # The list view also returns the data URL so miniatures can render.
    listing = client.get("/library").json()
    assert listing[0]["image_data_url"].startswith("data:image/jpeg")


def test_db_models_registered(client):
    """Smoke check: the LibraryEntry table exists and is queryable."""
    # The fixture has already created tables; verify by issuing a query.
    _save_one(client)
    # Direct ORM check via SQLAlchemy session would require pulling it
    # from the dependency override; the API list call is a cleaner proxy.
    assert client.get("/library").status_code == 200
    # Touch the model so the import isn't flagged as unused.
    assert models.LibraryEntry.__tablename__ == "library_entries"
