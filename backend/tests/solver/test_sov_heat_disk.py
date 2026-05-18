"""Tests for the axisymmetric heat equation on a disk."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _heat_disk_problem(f: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="u_t = alpha^2*(u_{rr} + u_r/r)",
        equation_kind="heat",
        geometry="disk",
        domain=Domain(x=["0", "R"], t=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="r=R", value="0"),
        ],
        initial_conditions=[InitialCondition(order=0, value=f)],
        parameters={"R": "positive", "alpha": "positive"},
    )


def test_routes_to_heat_disk():
    resp = solve(_heat_disk_problem("1"))
    assert resp.method == "sov_heat_disk"


def test_response_has_exponential_decay():
    resp = solve(_heat_disk_problem("1"))
    final = next(s for s in resp.steps if s.kind == "final")
    # Should mention exp() in the LaTeX of the series.
    assert "e^{" in final.latex or "exp" in final.sympy_repr.lower()


def test_response_has_bessel_eigenvalues_step():
    resp = solve(_heat_disk_problem("1"))
    titles = " ".join(s.title.lower() for s in resp.steps)
    assert "bessel" in titles or "j_0" in titles or "ceros" in titles


def test_classification_is_parabolic():
    resp = solve(_heat_disk_problem("1"))
    cls = [s for s in resp.steps if s.kind == "classification"]
    text = " ".join(s.explanation_md.lower() for s in cls)
    assert "parabólica" in text or "parabolica" in text


def test_weighted_orthogonality_observation():
    resp = solve(_heat_disk_problem("1"))
    obs_md = " ".join(o.text_md for s in resp.steps for o in s.observations).lower()
    assert "peso" in obs_md
