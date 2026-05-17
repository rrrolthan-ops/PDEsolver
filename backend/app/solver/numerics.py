"""Numerical sampling for plotting and convergence study.

The frontend doesn't evaluate SymPy series; the backend hands it raw
NumPy arrays. This module:

1. Lambdifies the n-th term of the series.
2. Sums N terms over a (x, t) grid.
3. Returns the result for `plot_data` (surface) and `convergence_data`
   (snapshots at N = 1, 5, 20, 100).

We deliberately keep the grid small (60×40 by default). The point is
to *show* convergence and shape, not to compete with a numerical PDE
solver.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import sympy as sp


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
    """Sample `u(x, t)` on a grid by summing `n_terms` terms.

    Returns
    -------
    dict
        Keys: x_grid, t_grid, u_grid (list of lists).
    """
    if not isinstance(solution_sum, sp.Sum):
        raise TypeError("Expected a sp.Sum series solution.")

    n = sp.Symbol("n", integer=True, positive=True)
    term = solution_sum.function

    # Lambdify the n-th term as a fast NumPy function.
    f_term = sp.lambdify((x, t, n, L, alpha), term, modules="numpy")

    xs = np.linspace(0.0, L_value, nx)
    ts = np.linspace(0.0, t_max, nt)
    X, Tt = np.meshgrid(xs, ts, indexing="xy")

    U = np.zeros_like(X)
    for k in range(1, n_terms + 1):
        U = U + np.asarray(f_term(X, Tt, k, L_value, alpha_value), dtype=float)

    return {
        "x": xs.tolist(),
        "t": ts.tolist(),
        "u": U.tolist(),
    }


def convergence_snapshots(
    solution_sum: sp.Basic,
    *,
    x: sp.Symbol,
    t: sp.Symbol,
    L: sp.Symbol,
    alpha: sp.Symbol,
    L_value: float = 1.0,
    alpha_value: float = 1.0,
    nx: int = 120,
    Ns: Iterable[int] = (1, 5, 20, 100),
    t_eval: float = 0.0,
) -> dict:
    """Compute the partial sum at `t = t_eval` for several truncations N.

    Used to show how the series approximates the initial profile (when
    `t_eval = 0`) or how the smoothing has progressed (`t_eval > 0`).
    """
    n = sp.Symbol("n", integer=True, positive=True)
    if not isinstance(solution_sum, sp.Sum):
        raise TypeError("Expected a sp.Sum series solution.")
    term = solution_sum.function

    f_term = sp.lambdify((x, t, n, L, alpha), term, modules="numpy")
    xs = np.linspace(0.0, L_value, nx)

    snapshots = {}
    running = np.zeros_like(xs)
    Ns_sorted = sorted(set(Ns))
    target_set = set(Ns_sorted)
    max_N = max(Ns_sorted)

    for k in range(1, max_N + 1):
        running = running + np.asarray(f_term(xs, t_eval, k, L_value, alpha_value), dtype=float)
        if k in target_set:
            snapshots[str(k)] = running.tolist()

    return {
        "x": xs.tolist(),
        "t_eval": t_eval,
        "snapshots": snapshots,
    }
