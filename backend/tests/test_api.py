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


def test_solve_wave_bounded():
    """Wave 1D on a bounded interval routes to the SOV-wave method."""
    payload = {
        "equation_latex": "u_{tt} = c^2 * u_{xx}",
        "equation_kind": "wave",
        "domain": {"x": ["0", "L"], "t": ["0", "infty"]},
        "boundary_conditions": [
            {"type": "dirichlet", "where": "x=0", "value": "0"},
            {"type": "dirichlet", "where": "x=L", "value": "0"},
        ],
        "initial_conditions": [
            {"order": 0, "value": "sin(pi*x/L)"},
            {"order": 1, "value": "0"},
        ],
        "parameters": {"c": "positive", "L": "positive"},
    }
    r = client.post("/solve", json=payload)
    assert r.status_code == 200, r.text
    assert r.json()["method"] == "sov_wave_1d"


def test_solve_dalembert():
    payload = {
        "equation_latex": "u_{tt} = c^2 * u_{xx}",
        "equation_kind": "wave",
        "domain": {"x": ["-infty", "infty"], "t": ["0", "infty"]},
        "boundary_conditions": [],
        "initial_conditions": [
            {"order": 0, "value": "exp(-x^2)"},
            {"order": 1, "value": "0"},
        ],
        "parameters": {"c": "positive"},
    }
    r = client.post("/solve", json=payload)
    assert r.status_code == 200, r.text
    assert r.json()["method"] == "dalembert_wave_1d"


def test_solve_laplace_rect():
    payload = {
        "equation_latex": "u_{xx} + u_{yy} = 0",
        "equation_kind": "laplace",
        "domain": {"x": ["0", "a"], "y": ["0", "b"]},
        "boundary_conditions": [
            {"type": "dirichlet", "where": "x=0", "value": "0"},
            {"type": "dirichlet", "where": "x=a", "value": "0"},
            {"type": "dirichlet", "where": "y=0", "value": "0"},
            {"type": "dirichlet", "where": "y=b", "value": "sin(pi*x/a)"},
        ],
        "initial_conditions": [{"order": 0, "value": "0"}],
        "parameters": {"a": "positive", "b": "positive"},
    }
    r = client.post("/solve", json=payload)
    assert r.status_code == 200, r.text
    assert r.json()["method"] == "sov_laplace_rect"


def test_solve_truly_unsupported_returns_422():
    """A problem still outside the repertoire should fail clearly, not 500."""
    payload = {
        "equation_latex": "u_t + u * u_x = 0",   # Burgers — nonlinear, not yet
        "domain": {"x": ["0", "1"], "t": ["0", "infty"]},
        "boundary_conditions": [],
        "initial_conditions": [{"order": 0, "value": "sin(pi*x)"}],
        "parameters": {},
    }
    r = client.post("/solve", json=payload)
    assert r.status_code == 422
