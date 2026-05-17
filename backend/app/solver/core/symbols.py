"""Shared SymPy symbol factory.

Symbols are declared with assumptions matching the physical meaning of
the parameter (e.g. lengths and diffusivities are positive reals,
indices are positive integers). Reusing these symbols across the
codebase ensures that simplifications are consistent.
"""

from __future__ import annotations

import sympy as sp

# Independent variables.
x, y, z = sp.symbols("x y z", real=True)
t = sp.symbols("t", real=True, nonnegative=True)

# Common physical parameters with positivity assumptions.
L = sp.symbols("L", positive=True)
alpha = sp.symbols("alpha", positive=True)
c = sp.symbols("c", positive=True)
k = sp.symbols("k", positive=True)
hbar = sp.symbols("hbar", positive=True)
m = sp.symbols("m", positive=True)

# Separation constant and Sturm-Liouville integer index.
lam = sp.symbols("lambda", real=True)
n = sp.symbols("n", integer=True, positive=True)

# The unknown function and its separated factors.
u = sp.Function("u")
X = sp.Function("X")
T = sp.Function("T")


# A registry of well-known parameter names → SymPy symbols, so that the
# parser can resolve them quickly without re-declaring assumptions.
KNOWN: dict[str, sp.Symbol] = {
    "x": x,
    "y": y,
    "z": z,
    "t": t,
    "L": L,
    "alpha": alpha,
    "c": c,
    "k": k,
    "hbar": hbar,
    "m": m,
    "lambda": lam,
    "n": n,
    "pi": sp.pi,
    "e": sp.E,
    "infty": sp.oo,
    "inf": sp.oo,
    "oo": sp.oo,
}


def symbol_for(name: str, assumption: str | None = None) -> sp.Symbol:
    """Return the canonical SymPy symbol for `name`, applying assumption.

    `assumption` is a string from the user's `PDEProblem.parameters`
    dict — e.g. "positive", "real", "integer". Unknown names create a
    fresh real symbol with that assumption applied.
    """
    if name in KNOWN:
        return KNOWN[name]
    kwargs: dict[str, bool] = {}
    if assumption == "positive":
        kwargs["positive"] = True
    elif assumption == "nonnegative":
        kwargs["nonnegative"] = True
    elif assumption == "integer":
        kwargs["integer"] = True
    elif assumption == "real" or assumption is None:
        kwargs["real"] = True
    return sp.symbols(name, **kwargs)
