"""Tests for the half-plane Dirichlet problem via the method of images."""

from __future__ import annotations

import sympy as sp

from app.schemas import (
    BoundaryCondition,
    Domain,
    InitialCondition,
    PDEProblem,
)
from app.solver import solve


def _halfplane_problem(f: str) -> PDEProblem:
    return PDEProblem(
        equation_latex="u_{xx} + u_{yy} = 0",
        equation_kind="laplace",
        geometry="halfplane",
        domain=Domain(x=["-infty", "infty"], y=["0", "infty"]),
        boundary_conditions=[
            BoundaryCondition(type="dirichlet", where="y=0", value=f),
        ],
        initial_conditions=[InitialCondition(order=0, value="0")],
        parameters={},
    )


def test_routes_to_images():
    resp = solve(_halfplane_problem("1/(1 + x^2)"))
    assert resp.method == "images_halfplane"


def test_response_has_green_construction_step():
    resp = solve(_halfplane_problem("1/(1 + x^2)"))
    titles = " ".join(s.title.lower() for s in resp.steps)
    assert "función de green" in titles or "funcion de green" in titles


def test_mirror_trick_observation_present():
    resp = solve(_halfplane_problem("1/(1 + x^2)"))
    obs_md = " ".join(o.text_md for s in resp.steps for o in s.observations).lower()
    assert "espejo" in obs_md or "mirror" in obs_md or "imagen" in obs_md


def test_method_choice_is_images():
    resp = solve(_halfplane_problem("1/(1 + x^2)"))
    mc_step = next(s for s in resp.steps if s.kind == "method_choice")
    text = mc_step.title.lower() + " " + mc_step.explanation_md.lower()
    assert "imagen" in text or "image" in text


def test_classification_elliptic():
    resp = solve(_halfplane_problem("exp(-x^2)"))
    cls_steps = [s for s in resp.steps if s.kind == "classification"]
    text = " ".join(s.explanation_md.lower() for s in cls_steps)
    assert "elíptica" in text or "elliptica" in text or "elliptic" in text


def test_solution_step_has_poisson_integral_form():
    """Even if sympy can't close the integral, the final step shows it."""
    resp = solve(_halfplane_problem("1/(1 + x^2)"))
    final = next(s for s in resp.steps if s.kind == "final")
    # The boxed formula should mention either an Integral or the closed
    # Poisson formula.
    assert "int" in final.latex.lower() or "/" in final.latex
