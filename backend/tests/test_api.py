"""Smoke tests for the FastAPI endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_solve_sin1():
    payload = {
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
    r = client.post("/solve", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["method"] == "separation_of_variables"
    assert data["verified"] is True
    assert len(data["steps"]) >= 15
    # Final solution LaTeX should mention sin and exp.
    assert "sin" in data["solution_latex"].lower()
    assert "e^" in data["solution_latex"] or "exp" in data["solution_latex"].lower()


def test_solve_unsupported_returns_422():
    """A problem we don't yet handle should fail clearly, not 500."""
    payload = {
        "equation_latex": "u_{tt} = c^2 * u_{xx}",   # wave eq, not in Phase 1
        "domain": {"x": ["0", "L"], "t": ["0", "infty"]},
        "boundary_conditions": [
            {"type": "dirichlet", "where": "x=0", "value": "0"},
            {"type": "dirichlet", "where": "x=L", "value": "0"},
        ],
        "initial_conditions": [{"order": 0, "value": "sin(pi*x/L)"}],
        "parameters": {"c": "positive", "L": "positive"},
    }
    r = client.post("/solve", json=payload)
    assert r.status_code == 422
