"""Tests for the LaTeX / physicist-notation parser."""

from __future__ import annotations

import sympy as sp

from app.parser import parse_pde_latex, parse_scalar_latex


def test_heat_equation_basic():
    parsed = parse_pde_latex("u_t = alpha^2 * u_{xx}", {"alpha": "positive"})
    # The equation is LHS - RHS = u_t - alpha^2 u_xx.
    x = sp.Symbol("x", real=True)
    t = sp.Symbol("t", real=True, nonnegative=True)
    u = parsed.u
    expected = sp.Derivative(u(x, t), t) - sp.Symbol("alpha", positive=True) ** 2 * sp.Derivative(
        u(x, t), x, 2
    )
    assert sp.simplify(parsed.expr - expected) == 0


def test_wave_equation_with_braces():
    parsed = parse_pde_latex("u_{tt} = c^2 * u_{xx}", {"c": "positive"})
    x = sp.Symbol("x", real=True)
    t = sp.Symbol("t", real=True, nonnegative=True)
    u = parsed.u
    expected = sp.Derivative(u(x, t), t, 2) - sp.Symbol("c", positive=True) ** 2 * sp.Derivative(
        u(x, t), x, 2
    )
    assert sp.simplify(parsed.expr - expected) == 0


def test_bare_subscripts():
    """Bare `u_x` and `u_t` notation."""
    parsed = parse_pde_latex("u_t - u_x = 0")
    x = sp.Symbol("x", real=True)
    t = sp.Symbol("t", real=True, nonnegative=True)
    u = parsed.u
    expected = sp.Derivative(u(x, t), t) - sp.Derivative(u(x, t), x)
    assert sp.simplify(parsed.expr - expected) == 0


def test_partial_fraction_notation():
    """LaTeX fraction with \\partial."""
    parsed = parse_pde_latex(r"\frac{\partial u}{\partial t} = \frac{\partial^2 u}{\partial x^2}")
    x = sp.Symbol("x", real=True)
    t = sp.Symbol("t", real=True, nonnegative=True)
    u = parsed.u
    expected = sp.Derivative(u(x, t), t) - sp.Derivative(u(x, t), x, 2)
    assert sp.simplify(parsed.expr - expected) == 0


def test_scalar_with_pi_and_caret():
    expr = parse_scalar_latex("sin(pi*x/L)", {"L": "positive"})
    x = sp.Symbol("x", real=True)
    L = sp.Symbol("L", positive=True)
    assert sp.simplify(expr - sp.sin(sp.pi * x / L)) == 0


def test_scalar_polynomial():
    expr = parse_scalar_latex("x*(L-x)", {"L": "positive"})
    x = sp.Symbol("x", real=True)
    L = sp.Symbol("L", positive=True)
    assert sp.simplify(expr - x * (L - x)) == 0
