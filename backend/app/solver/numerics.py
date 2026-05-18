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


# ===========================================================================
# Plot shapes for non-(x,t) methods
# ===========================================================================
#
# Each helper below returns a dict with a `kind` discriminator. The
# frontend dispatches on `kind` to pick a Plotly component:
#
#   kind = "surface_xt"   →  u(x, t) heatmap or surface  (heat/wave 1D)
#   kind = "surface_xy"   →  u(x, y) in some Cartesian patch (Laplace
#                            rectangle, polar→Cartesian disc, meridional
#                            slice of a ball, …)
#   kind = "line"         →  u(x) 1D plot (Poisson 1D, beam, …)
#
# The legacy heat/wave plot dicts (no `kind` field) are still emitted
# untagged and the frontend treats them as `surface_xt`.

# ---------------------------------------------------------------------------
# 1D line plots
# ---------------------------------------------------------------------------


def sample_line(
    expr: sp.Basic,
    *,
    x_sym: sp.Symbol,
    x_range: tuple[float, float],
    parameter_values: dict[sp.Symbol, float] | None = None,
    nx: int = 200,
    x_label: str = "x",
    y_label: str = "u",
) -> dict:
    """Sample a closed-form `u(x)` on a 1D grid."""
    parameter_values = parameter_values or {}
    # Free parameters of `expr` minus the independent variable.
    param_syms = sorted(
        (s for s in expr.free_symbols if s != x_sym),
        key=lambda s: s.name,
    )
    missing = [s for s in param_syms if s not in parameter_values]
    if missing:
        raise ValueError(f"Missing concrete values for: {missing}")

    f = sp.lambdify((x_sym, *param_syms), expr, modules="numpy")
    xs = np.linspace(*x_range, nx)
    values = [float(parameter_values[s]) for s in param_syms]
    ys = np.asarray(f(xs, *values), dtype=float)
    return {
        "kind": "line",
        "x": xs.tolist(),
        "u": ys.tolist(),
        "x_label": x_label,
        "y_label": y_label,
    }


# ---------------------------------------------------------------------------
# Polar → Cartesian disk plot
# ---------------------------------------------------------------------------


def sample_polar_disk(
    expr: sp.Basic,
    *,
    r_sym: sp.Symbol,
    theta_sym: sp.Symbol | None,
    R_value: float,
    parameter_values: dict[sp.Symbol, float] | None = None,
    extra_subs: dict[sp.Symbol, float] | None = None,
    n_grid: int = 70,
    n_terms: int = 40,
) -> dict:
    """Render `u(r, θ)` (possibly a Sum) on a Cartesian patch covering the disc.

    `extra_subs` is for things like "evaluate u at this fixed time"
    (substitute `t → t_value` before lambdifying).

    Outside the disc we emit `None` (renders as a hole in Plotly).
    """
    parameter_values = parameter_values or {}
    extra_subs = extra_subs or {}

    # Build Cartesian grid.
    xs = np.linspace(-R_value, R_value, n_grid)
    ys = np.linspace(-R_value, R_value, n_grid)
    X, Y = np.meshgrid(xs, ys, indexing="xy")
    rr = np.sqrt(X**2 + Y**2)
    tt = np.arctan2(Y, X)
    inside = rr <= R_value * 0.999

    # Evaluate. We may have a Sum, an Add(constant + Sum), or a plain expr.
    U = _evaluate_radial(
        expr,
        r_sym=r_sym,
        theta_sym=theta_sym,
        rr=rr,
        tt=tt,
        parameter_values=parameter_values,
        extra_subs=extra_subs,
        n_terms=n_terms,
    )

    # Mask outside.
    U_out = np.where(inside, U, np.nan).tolist()
    # Replace NaNs with None for clean JSON.
    U_clean = [[None if (v != v) else float(v) for v in row] for row in U_out]
    return {
        "kind": "surface_xy",
        "x": xs.tolist(),
        "y": ys.tolist(),
        "u": U_clean,
        "x_label": "x",
        "y_label": "y",
    }


def _evaluate_radial(
    expr: sp.Basic,
    *,
    r_sym: sp.Symbol,
    theta_sym: sp.Symbol | None,
    rr: np.ndarray,
    tt: np.ndarray,
    parameter_values: dict[sp.Symbol, float],
    extra_subs: dict[sp.Symbol, float],
    n_terms: int,
) -> np.ndarray:
    """Evaluate an expression involving (r, θ) on numpy grids.

    Handles three shapes:
    - plain `expr` (no Sum): lambdify and call.
    - `Add(constant, Sum(...))`: split, evaluate each, add.
    - `Sum(...)`: truncate to `n_terms` and accumulate.

    Inside the Sum, special handling for `IndexedBase("mu")[n]` (Bessel
    zeros): substitute with `scipy.special.jn_zeros(0, k)[k-1]`.
    """
    constant_part, sum_part = _split_sum(expr)

    out = np.zeros_like(rr, dtype=float)
    if constant_part is not None:
        const_val = _eval_closed_form(
            constant_part, r_sym, theta_sym, rr, tt, parameter_values, extra_subs
        )
        out = out + const_val

    if sum_part is not None:
        out = out + _eval_truncated_sum(
            sum_part, r_sym, theta_sym, rr, tt, parameter_values, extra_subs, n_terms
        )

    return out


def _split_sum(expr: sp.Basic) -> tuple[sp.Basic | None, sp.Sum | None]:
    """Return (constant_part, sum_part). Either may be None."""
    if isinstance(expr, sp.Sum):
        return None, expr
    if isinstance(expr, sp.Add):
        sums = [a for a in expr.args if isinstance(a, sp.Sum)]
        rest = [a for a in expr.args if not isinstance(a, sp.Sum)]
        if len(sums) == 1:
            return (sp.Add(*rest) if rest else None), sums[0]
        # No sum or multiple sums — treat as closed form.
        return expr, None
    return expr, None


def _eval_closed_form(
    expr: sp.Basic,
    r_sym: sp.Symbol,
    theta_sym: sp.Symbol | None,
    rr: np.ndarray,
    tt: np.ndarray,
    parameter_values: dict[sp.Symbol, float],
    extra_subs: dict[sp.Symbol, float],
) -> np.ndarray:
    expr2 = expr.subs(extra_subs).subs(parameter_values)
    expr2 = _normalize_bessel_placeholders(expr2)
    free = list(expr2.free_symbols)
    args = [r_sym] + ([theta_sym] if theta_sym is not None else [])
    args = [a for a in args if a in free]
    # Use scipy for besselj / besselj-y; fall back to numpy for the rest.
    modules = ["scipy", "numpy"]
    if not args:
        # Lambdify with no args still works and gives us scipy support.
        f = sp.lambdify((), expr2, modules=modules)
        return np.full_like(rr, float(f()))
    if theta_sym in args:
        f = sp.lambdify(args, expr2, modules=modules)
        if args[0] == r_sym:
            return np.asarray(f(rr, tt), dtype=float)
        return np.asarray(f(tt, rr), dtype=float)
    # Only r.
    f = sp.lambdify(args, expr2, modules=modules)
    return np.asarray(f(rr), dtype=float)


def _normalize_bessel_placeholders(expr: sp.Basic) -> sp.Basic:
    """Rewrite the solver's placeholder `J_1(x)` as `sp.besselj(1, x)`.

    `sov_wave_disk` and `sov_heat_disk` carry the Bessel-norm factor as
    a generic `sp.Function("J_1")` to keep the displayed LaTeX clean.
    For numerical evaluation we need the real Bessel function, which
    SymPy exposes as `sp.besselj` and which lambdify-with-scipy maps
    to `scipy.special.jv`.
    """
    J1 = sp.Function("J_1")
    return expr.replace(
        lambda e: isinstance(e, sp.Function) and e.func == J1,
        lambda e: sp.besselj(1, *e.args),
    )


def _eval_truncated_sum(
    sum_expr: sp.Sum,
    r_sym: sp.Symbol,
    theta_sym: sp.Symbol | None,
    rr: np.ndarray,
    tt: np.ndarray,
    parameter_values: dict[sp.Symbol, float],
    extra_subs: dict[sp.Symbol, float],
    n_terms: int,
) -> np.ndarray:
    """Truncate the Sum to `n_terms` terms and evaluate on the (rr, tt) grid.

    The dummy index is the first limit variable. If `IndexedBase("mu")[n]`
    appears (Bessel methods), substitute with `scipy.special.jn_zeros`.
    """
    term = sum_expr.function
    # `Sum.limits` is a tuple of (sym, lower, upper) tuples.
    dummy, lower, _upper = sum_expr.limits[0]
    start = int(lower)

    # Pre-fetch Bessel zeros if the term references `mu[n]`.
    mu_zeros = _maybe_bessel_zeros(term, n_terms + start)
    mu = sp.IndexedBase("mu")

    out = np.zeros_like(rr, dtype=float)
    for k in range(start, start + n_terms):
        t_k = term.subs(dummy, k)
        if mu_zeros is not None:
            t_k = t_k.subs(mu[k], float(mu_zeros[k - 1]))
        t_k = t_k.subs(extra_subs).subs(parameter_values)
        # Coefficient integrals (Bessel-Fourier `B_n` for disk methods,
        # Legendre `A_ell` for the ball) are kept symbolic in the
        # solver output — they need a concrete `n` / `ell` to collapse.
        # Now that we've substituted, force evaluation. If the integral
        # still won't close in elementary form, `doit()` returns the
        # integral untouched and we'll surface that as a lambdify error
        # caught higher up.
        if t_k.has(sp.Integral):
            t_k = t_k.doit()
        out = out + _eval_closed_form(
            t_k, r_sym, theta_sym, rr, tt, parameter_values, extra_subs
        )
    return out


def _maybe_bessel_zeros(term: sp.Basic, n_needed: int) -> np.ndarray | None:
    """Return the first n_needed positive zeros of J_0 if `term` mentions mu[n].

    We detect by looking for any `sp.Indexed` whose base is named `mu`.
    """
    has_mu = any(
        getattr(node, "base", None) is not None and str(node.base) == "mu"
        for node in sp.preorder_traversal(term)
        if isinstance(node, sp.Indexed)
    )
    if not has_mu:
        return None
    try:
        from scipy.special import jn_zeros
    except ImportError:
        return None
    return jn_zeros(0, n_needed)


# ---------------------------------------------------------------------------
# Axisymmetric ball: meridional slice u(r, θ) on (x, z)
# ---------------------------------------------------------------------------


def sample_meridional_slice(
    expr: sp.Basic,
    *,
    r_sym: sp.Symbol,
    theta_sym: sp.Symbol,
    R_value: float,
    parameter_values: dict[sp.Symbol, float] | None = None,
    n_grid: int = 70,
    n_terms: int = 20,
) -> dict:
    """Render `u(r, θ)` in a meridional half-disc slice of the ball.

    Convention: x = r sin θ (horizontal, 0 ≤ θ ≤ π → 0 ≤ x ≤ R),
                z = r cos θ (vertical, north pole at z = +R).

    The slice covers the full meridional disc x ∈ [-R, R], z ∈ [-R, R]
    (we use the symmetry of axisymmetric problems: extend by reflection).
    """
    parameter_values = parameter_values or {}
    xs = np.linspace(-R_value, R_value, n_grid)
    zs = np.linspace(-R_value, R_value, n_grid)
    X, Z = np.meshgrid(xs, zs, indexing="xy")
    rr = np.sqrt(X**2 + Z**2)
    # θ from the +z axis; arccos handles full meridional plane.
    # `np.arccos` returns values in [0, π], which is correct for colatitude.
    safe_rr = np.where(rr > 0, rr, 1.0)  # avoid /0 at the origin
    tt = np.arccos(np.clip(Z / safe_rr, -1.0, 1.0))
    inside = rr <= R_value * 0.999

    U = _evaluate_radial(
        expr,
        r_sym=r_sym,
        theta_sym=theta_sym,
        rr=rr,
        tt=tt,
        parameter_values=parameter_values,
        extra_subs={},
        n_terms=n_terms,
    )

    U_out = np.where(inside, U, np.nan).tolist()
    U_clean = [[None if (v != v) else float(v) for v in row] for row in U_out]
    return {
        "kind": "surface_xy",
        "x": xs.tolist(),
        "y": zs.tolist(),
        "u": U_clean,
        "x_label": "x",
        "y_label": "z",
    }


# ---------------------------------------------------------------------------
# Half-plane Poisson kernel (numerical convolution)
# ---------------------------------------------------------------------------


def sample_halfplane_poisson(
    expr: sp.Basic,
    *,
    x_sym: sp.Symbol,
    y_sym: sp.Symbol,
    parameter_values: dict[sp.Symbol, float] | None = None,
    x_range: tuple[float, float] = (-3.0, 3.0),
    y_range: tuple[float, float] = (0.05, 2.0),
    n_grid: tuple[int, int] = (50, 35),
    quad_limit: float = 30.0,
) -> dict:
    """Render `u(x, y)` for the half-plane Dirichlet problem.

    For most boundary data `f`, the solution is

        u(x, y) = (y / π) ∫_{-∞}^{∞} f(x') / ((x - x')² + y²) dx',

    which the `images_halfplane` solver returns as an unevaluated
    `sp.Integral`. We handle both shapes that solver can emit:

    - **Constant fast-path** (when `f` had no `xp` dependence — the
      Poisson kernel integrates to `f` itself). Lambdify and render
      as a flat surface.
    - **Integral form**: lambdify the integrand over `(x, y, xp)` and
      run `scipy.integrate.quad` for every grid point. The Poisson
      integrand decays like `1/xp²` so truncating at `±quad_limit`
      is fine for the boundary profiles in our examples (Gaussian,
      Lorentzian, etc.).
    """
    parameter_values = parameter_values or {}
    xs = np.linspace(*x_range, n_grid[0])
    ys = np.linspace(*y_range, n_grid[1])

    expr_concrete = expr.subs(parameter_values)

    if not expr_concrete.has(sp.Integral):
        # Closed-form case (f was constant or otherwise free of xp).
        free = expr_concrete.free_symbols
        bound_args = tuple(s for s in (x_sym, y_sym) if s in free)
        f = sp.lambdify(bound_args, expr_concrete, modules=["scipy", "numpy"])
        X, Y = np.meshgrid(xs, ys, indexing="xy")
        if len(bound_args) == 0:
            U = np.full_like(X, float(expr_concrete))
        elif bound_args == (x_sym,):
            U = np.asarray(f(X), dtype=float)
        elif bound_args == (y_sym,):
            U = np.asarray(f(Y), dtype=float)
        else:
            U = np.asarray(f(X, Y), dtype=float)
        return _wrap_xy(U, xs, ys)

    integral = _find_integral(expr_concrete)
    if integral is None:
        raise ValueError("expected an sp.Integral somewhere in the expression")

    integrand = integral.function
    xp_var = integral.limits[0][0]
    g = sp.lambdify(
        (x_sym, y_sym, xp_var), integrand, modules=["scipy", "numpy"]
    )

    from scipy.integrate import quad

    U = np.zeros((len(ys), len(xs)), dtype=float)
    for i, yv in enumerate(ys):
        for j, xv in enumerate(xs):
            val, _err = quad(
                lambda xp_val: g(xv, yv, xp_val),
                -quad_limit,
                quad_limit,
                limit=80,
            )
            U[i, j] = val
    return _wrap_xy(U, xs, ys)


def _find_integral(expr: sp.Basic) -> sp.Integral | None:
    """First `sp.Integral` found anywhere in `expr`, or None."""
    if isinstance(expr, sp.Integral):
        return expr
    for arg in sp.preorder_traversal(expr):
        if isinstance(arg, sp.Integral):
            return arg
    return None


# ---------------------------------------------------------------------------
# Helmholtz on a rectangle (modal expansion at concrete k)
# ---------------------------------------------------------------------------


def sample_helmholtz_rect(
    expr: sp.Basic,
    *,
    x_sym: sp.Symbol,
    y_sym: sp.Symbol,
    a_sym: sp.Symbol,
    b_sym: sp.Symbol,
    k_sym: sp.Symbol,
    a_value: float = 1.0,
    b_value: float = 1.0,
    k_squared_value: float = 30.0,
    n_terms: int = 5,
    n_grid: int = 50,
) -> dict:
    """Render the Helmholtz solution on `[0, a] × [0, b]`.

    Two shapes can arrive here:

    - **Eigenfunction**: when the user posed the homogeneous problem
      (`source_term` empty), the solver emits a single
      `sin(πx/a) sin(πy/b)` as the "fundamental mode" exemplar.
      We just lambdify it.
    - **Inhomogeneous double sum**: nested
      `Sum(Sum(c_mn φ_mn, n), m)`. We truncate both sums to
      `n_terms` and substitute `(a, b) → (1, 1)` and `k² → 30`.
      `k² = 30` lands safely between the first two rectangle
      eigenvalues (`k²_{11} ≈ 19.74`, `k²_{12} ≈ 49.35`), so no
      `1 / (k² − k²_{mn})` denominator gets pathologically small.
    """
    xs = np.linspace(0.0, a_value, n_grid)
    ys = np.linspace(0.0, b_value, n_grid)
    X, Y = np.meshgrid(xs, ys, indexing="xy")

    base_subs = {a_sym: a_value, b_sym: b_value}
    k_sub = {k_sym**2: k_squared_value, k_sym: float(np.sqrt(k_squared_value))}

    if not isinstance(expr, sp.Sum):
        # Eigenfunction path.
        e = expr.subs(base_subs).subs(k_sub)
        return _wrap_xy(_eval_xy(e, x_sym, y_sym, X, Y), xs, ys)

    # Inhomogeneous path. Two AST shapes can arrive here:
    #
    #   (a) Single `Sum(body, (n, 1, oo), (m, 1, oo))` — multi-limit Sum
    #       (this is what sympy's `c_mn * φ_mn` simplification produces
    #       for the Helmholtz solver).
    #   (b) Nested `Sum(Sum(body, (n, ...)), (m, ...))` — also valid
    #       sympy and semantically equivalent.
    #
    # We flatten both into the list of (dummy, lower) pairs and iterate
    # the Cartesian product.
    dummies, body = _flatten_sum_limits(expr)

    import itertools

    ranges = [range(lo, lo + n_terms) for _, lo in dummies]
    syms = [d for d, _ in dummies]
    total = sp.S.Zero
    for vals in itertools.product(*ranges):
        total = total + body.subs(dict(zip(syms, vals)))

    total = total.subs(base_subs).subs(k_sub)
    if total.has(sp.Integral):
        total = total.doit()
    return _wrap_xy(_eval_xy(total, x_sym, y_sym, X, Y), xs, ys)


def _flatten_sum_limits(expr: sp.Basic) -> tuple[list[tuple[sp.Symbol, int]], sp.Basic]:
    """Recursively peel a (possibly nested) Sum into (dummies, body).

    Returns `([(dummy, lower), ...], innermost_body)` for any combination
    of nested Sums and multi-limit Sums.
    """
    if not isinstance(expr, sp.Sum):
        return [], expr
    dummies = [(L[0], int(L[1])) for L in expr.limits]
    inner_dummies, body = _flatten_sum_limits(expr.function)
    return dummies + inner_dummies, body


def _truncate_sum(sum_expr: sp.Sum, n_terms: int) -> sp.Expr:
    dummy, lower, _ = sum_expr.limits[0]
    return sum(
        sum_expr.function.subs(dummy, k)
        for k in range(int(lower), int(lower) + n_terms)
    )


def _eval_xy(
    expr: sp.Basic,
    x_sym: sp.Symbol,
    y_sym: sp.Symbol,
    X: np.ndarray,
    Y: np.ndarray,
) -> np.ndarray:
    expr = _normalize_bessel_placeholders(expr)
    f = sp.lambdify((x_sym, y_sym), expr, modules=["scipy", "numpy"])
    return np.asarray(f(X, Y), dtype=float)


def _wrap_xy(U: np.ndarray, xs: np.ndarray, ys: np.ndarray) -> dict:
    return {
        "kind": "surface_xy",
        "x": xs.tolist(),
        "y": ys.tolist(),
        "u": U.tolist(),
        "x_label": "x",
        "y_label": "y",
    }
