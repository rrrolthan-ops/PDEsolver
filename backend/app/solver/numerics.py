"""Numerical sampling for plotting and convergence study.

Each method has slightly different signature requirements:

- heat 1D:     u(x, t),   parameters L, alpha
- wave 1D:     u(x, t),   parameters L, c, plus two ICs
- Laplace:     u(x, y),   parameters a, b
- D'Alembert:  u(x, t),   parameter  c   (closed form, not a Sum)

We expose a single `sample_2d` that handles all of them by letting
the caller pass the symbols and concrete parameter values explicitly.
For series solutions we also expose `convergence_snapshots` that
returns partial sums at N = 1, 5, 20, 100.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import sympy as sp


def sample_2d(
    expr: sp.Basic,
    *,
    var1: sp.Symbol,
    var2: sp.Symbol,
    var1_range: tuple[float, float],
    var2_range: tuple[float, float],
    parameter_values: dict[sp.Symbol, float] | None = None,
    n_grid: tuple[int, int] = (60, 40),
    n_terms: int = 50,
) -> dict:
    """Sample a 2-variable solution on a grid.

    If `expr` is a `sp.Sum`, we sum the first `n_terms` terms. Otherwise
    we lambdify the closed-form expression directly.

    Returns a dict with `{"var1": [...], "var2": [...], "u": [[...]]}`.
    """
    parameter_values = parameter_values or {}
    n_sym = sp.Symbol("n", integer=True, positive=True)

    if isinstance(expr, sp.Sum):
        term = expr.function
        # Free symbols in `term` minus var1, var2, n, give us the parameters.
        param_syms = sorted(
            (s for s in term.free_symbols if s not in {var1, var2, n_sym}),
            key=lambda s: s.name,
        )
        f = sp.lambdify((var1, var2, n_sym, *param_syms), term, modules="numpy")

        v1 = np.linspace(*var1_range, n_grid[0])
        v2 = np.linspace(*var2_range, n_grid[1])
        V1, V2 = np.meshgrid(v1, v2, indexing="xy")
        U = np.zeros_like(V1)
        param_vals = [float(parameter_values[s]) for s in param_syms]
        for k in range(1, n_terms + 1):
            U = U + np.asarray(f(V1, V2, k, *param_vals), dtype=float)
        return {"var1": v1.tolist(), "var2": v2.tolist(), "u": U.tolist()}

    # Closed-form (D'Alembert and friends).
    param_syms = sorted(
        (s for s in expr.free_symbols if s not in {var1, var2}),
        key=lambda s: s.name,
    )
    f = sp.lambdify((var1, var2, *param_syms), expr, modules="numpy")
    v1 = np.linspace(*var1_range, n_grid[0])
    v2 = np.linspace(*var2_range, n_grid[1])
    V1, V2 = np.meshgrid(v1, v2, indexing="xy")
    param_vals = [float(parameter_values[s]) for s in param_syms]
    U = np.asarray(f(V1, V2, *param_vals), dtype=float)
    return {"var1": v1.tolist(), "var2": v2.tolist(), "u": U.tolist()}


def convergence_snapshots(
    solution_sum: sp.Basic,
    *,
    var1: sp.Symbol,
    var2: sp.Symbol,
    parameter_values: dict[sp.Symbol, float],
    var1_range: tuple[float, float],
    var2_eval: float = 0.0,
    nx: int = 120,
    Ns: Iterable[int] = (1, 5, 20, 100),
) -> dict | None:
    """Show how the partial sum at fixed `var2 = var2_eval` builds up.

    Only meaningful for series solutions; returns None for closed-form.
    """
    if not isinstance(solution_sum, sp.Sum):
        return None
    n_sym = sp.Symbol("n", integer=True, positive=True)
    term = solution_sum.function
    param_syms = sorted(
        (s for s in term.free_symbols if s not in {var1, var2, n_sym}),
        key=lambda s: s.name,
    )
    f = sp.lambdify((var1, var2, n_sym, *param_syms), term, modules="numpy")
    xs = np.linspace(*var1_range, nx)
    Ns_sorted = sorted(set(Ns))
    target = set(Ns_sorted)
    running = np.zeros_like(xs)
    param_vals = [float(parameter_values[s]) for s in param_syms]
    snapshots = {}
    for k in range(1, max(Ns_sorted) + 1):
        running = running + np.asarray(
            f(xs, var2_eval, k, *param_vals), dtype=float
        )
        if k in target:
            snapshots[str(k)] = running.tolist()
    return {"x": xs.tolist(), "t_eval": var2_eval, "snapshots": snapshots}


# ---------------------------------------------------------------------------
# Back-compat wrappers used by the original heat-1D pipeline call.
# These keep older code working without touching it.
# ---------------------------------------------------------------------------


def sample_series_solution(
    solution_sum: sp.Basic,
    *,
    x: sp.Symbol,
    t: sp.Symbol,
    L: sp.Symbol,
    alpha: sp.Symbol,
    L_value: float = 1.0,
    alpha_value: float = 1.0,
    nx: int = 60,
    nt: int = 40,
    t_max: float = 0.5,
    n_terms: int = 50,
) -> dict:
    """Heat-specific wrapper around `sample_2d` for backward compatibility."""
    data = sample_2d(
        solution_sum,
        var1=x,
        var2=t,
        var1_range=(0.0, L_value),
        var2_range=(0.0, t_max),
        parameter_values={L: L_value, alpha: alpha_value},
        n_grid=(nx, nt),
        n_terms=n_terms,
    )
    # Rename keys to the legacy names the frontend already speaks.
    return {"x": data["var1"], "t": data["var2"], "u": data["u"]}
