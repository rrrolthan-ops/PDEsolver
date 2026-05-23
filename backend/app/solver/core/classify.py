"""Classification of second-order linear PDEs by their discriminant.

The discriminant `B^2 - 4AC` (where the PDE has the canonical form
`A u_xx + B u_xy + C u_yy + ... = 0`) determines the qualitative
behaviour of solutions:

- `< 0`  → elliptic   (Laplace, Helmholtz)
- `= 0`  → parabolic  (heat)
- `> 0`  → hyperbolic (wave)

For evolution equations like `u_t = α² u_xx` we adapt the formalism
slightly: the principal part is `−α² u_xx` (the time derivative
contributes a first-order term in the space–time hypersurface, which is
what makes the equation parabolic).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import sympy as sp

PDEType = Literal["elliptic", "parabolic", "hyperbolic", "unknown"]


@dataclass
class Classification:
    A: sp.Basic
    B: sp.Basic
    C: sp.Basic
    discriminant: sp.Basic
    type: PDEType
    rationale_md: str


def classify_second_order(
    expr: sp.Basic,
    space_var: sp.Symbol,
    other_var: sp.Symbol,
) -> Classification:
    """Classify a second-order linear PDE.

    `expr` must be in the form `F = 0` — i.e. we are given the
    expression that equals zero. We pull out the coefficients of
    `u_{xx}` (A), `u_{xy}` (B), and `u_{yy}` (C) using SymPy's
    `coeff` after substituting placeholder symbols for each derivative.

    The classification is exact when `A`, `B`, `C` are constants and
    symbolic when they involve parameters with sign assumptions.

    Parameters
    ----------
    expr
        The PDE expression equal to zero.
    space_var
        The "x-like" spatial variable.
    other_var
        Either another spatial variable (for Laplace-like) or the time
        variable `t` (for heat / wave). The discriminant is interpreted
        accordingly.
    """
    # Replace each second derivative with a tagged dummy so that
    # SymPy's coefficient extraction works without confusing one
    # derivative for a multiple of another.
    u = sp.Function("u")
    a_sym, b_sym, c_sym = sp.symbols("__A __B __C")

    u_xx = sp.Derivative(u(space_var, other_var), space_var, 2)
    u_yy = sp.Derivative(u(space_var, other_var), other_var, 2)
    u_xy = sp.Derivative(u(space_var, other_var), space_var, other_var)

    probe = expr.subs({u_xx: a_sym, u_yy: c_sym, u_xy: b_sym})
    A = probe.coeff(a_sym)
    B = probe.coeff(b_sym)
    C = probe.coeff(c_sym)

    disc = sp.simplify(B**2 - 4 * A * C)

    # Decide sign of the discriminant when possible.
    pde_type: PDEType
    rationale: str
    sign = _sign_of(disc)
    if sign == 0:
        pde_type = "parabolic"
        rationale = (
            "Como B² − 4AC = 0, la EDP es **parabólica**. "
            "Las parabólicas son ecuaciones de evolución (una variable "
            "actúa como tiempo) que **suavizan** condiciones iniciales: "
            "ejemplo paradigmático, la ecuación del calor."
        )
    elif sign < 0:
        pde_type = "elliptic"
        rationale = (
            "Como B² − 4AC < 0, la EDP es **elíptica**. "
            "Las elípticas describen estados de equilibrio (sin tiempo) "
            "y sus soluciones son tan suaves como permiten los datos en "
            "la frontera; ejemplo paradigmático, la ecuación de Laplace."
        )
    elif sign > 0:
        pde_type = "hyperbolic"
        rationale = (
            "Como B² − 4AC > 0, la EDP es **hiperbólica**. "
            "Las hiperbólicas describen propagación: la información "
            "viaja a velocidad finita a lo largo de curvas características. "
            "Ejemplo paradigmático, la ecuación de onda."
        )
    else:
        pde_type = "unknown"
        rationale = (
            "El signo del discriminante depende de parámetros sin asumir. "
            "Para clasificar deberíamos fijar el signo de los parámetros."
        )

    return Classification(
        A=A,
        B=B,
        C=C,
        discriminant=disc,
        type=pde_type,
        rationale_md=rationale,
    )


def _sign_of(expr: sp.Basic) -> int | None:
    """Return -1, 0, or 1 if SymPy can decide the sign; else None."""
    if expr.is_zero:
        return 0
    if expr.is_positive:
        return 1
    if expr.is_negative:
        return -1
    # Try a numerical evaluation as a last resort (works when only
    # positive-assumed symbols appear).
    try:
        evaluated = sp.simplify(expr)
        if evaluated.is_positive:
            return 1
        if evaluated.is_negative:
            return -1
        if evaluated.is_zero:
            return 0
    except Exception:
        pass
    return None
