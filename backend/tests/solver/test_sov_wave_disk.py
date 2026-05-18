"""Tests for the axisymmetric wave equation on a disk."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _wave_disk_problem(f: str, g: str = "0") -> PDEProblem:
    return PDEProblem(
        equation_latex="u_{tt} = c^2*(u_{rr} + u_r/r)",
        equation_kind="wave",
        geometry="disk",
        domain=Domain(x=["0", "R"], t=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="r=R", value="0"),
        ],
        initial_conditions=[
            InitialCondition(order=0, value=f),
            InitialCondition(order=1, value=g),
        ],
        parameters={"R": "positive", "c": "positive"},
    )


def test_routes_to_wave_disk():
    resp = solve(_wave_disk_problem("1"))
    assert resp.method == "sov_wave_disk"


def test_response_has_bessel_steps():
    resp = solve(_wave_disk_problem("1"))
    titles = " ".join(s.title.lower() for s in resp.steps)
    assert "bessel" in titles


def test_inharmonic_drum_observation():
    resp = solve(_wave_disk_problem("1"))
    obs_md = " ".join(o.text_md for s in resp.steps for o in s.observations).lower()
    assert "inarmónic" in obs_md or "tambor" in obs_md


def test_solution_uses_besselj():
    resp = solve(_wave_disk_problem("1"))
    final = next(s for s in resp.steps if s.kind == "final")
    assert "besselj" in final.sympy_repr.lower() or "J_{0}" in final.latex


def test_weighted_orthogonality_observation():
    resp = solve(_wave_disk_problem("1"))
    obs_md = " ".join(o.text_md for s in resp.steps for o in s.observations).lower()
    assert "peso" in obs_md and "r" in obs_md
