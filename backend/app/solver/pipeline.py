"""Top-level `solve(problem) -> SolutionResponse` pipeline.

Glue between the method picker, the chosen method's `solve`, and the
numerical sampling for the frontend. Each method has slightly different
plot conventions (heat / wave plot u vs (x, t); Laplace plots vs (x, y);
D'Alembert is a closed form, not a series), so the dispatch lives here.
"""

from __future__ import annotations

import sympy as sp

from app.schemas import PDEProblem, SolutionResponse
from app.solver.core.method_picker import pick_method
from app.solver.methods.biharmonic_beam import BiharmonicBeam
from app.solver.methods.burgers import BurgersInviscid
from app.solver.methods.characteristics import CharacteristicsTransport1D
from app.solver.methods.dalembert import DAlembertWave1D
from app.solver.methods.duhamel_heat import DuhamelHeat
from app.solver.methods.fourier_heat_line import FourierHeatLine
from app.solver.methods.general_second_order import GeneralSecondOrder
from app.solver.methods.green_1d import GreensFunction1D
from app.solver.methods.images_halfplane import ImagesHalfPlane
from app.solver.methods.laplace_heat_halfline import LaplaceHeatHalfLine
from app.solver.methods.schrodinger_free import SchrodingerFreeLine
from app.solver.methods.schrodinger_oscillator import SchrodingerHarmonicOscillator
from app.solver.methods.schrodinger_well import SchrodingerInfiniteWell
from app.solver.methods.separation_of_variables import SeparationOfVariablesHeat1D
from app.solver.methods.sov_heat_disk import HeatDisk
from app.solver.methods.sov_helmholtz_rect import HelmholtzRect
from app.solver.methods.sov_laplace import SeparationOfVariablesLaplaceRect
from app.solver.methods.sov_laplace_ball import LaplaceBall
from app.solver.methods.sov_laplace_disk import SeparationOfVariablesLaplaceDisk
from app.solver.methods.sov_telegraph import TelegraphSOV
from app.solver.methods.sov_wave import SeparationOfVariablesWave1D
from app.solver.methods.sov_wave_disk import WaveDisk
from app.solver.methods.sov_wave_rect import WaveRect2D
from app.solver.numerics import (
    convergence_snapshots,
    sample_2d,
    sample_halfplane_poisson,
    sample_helmholtz_rect,
    sample_line,
    sample_meridional_slice,
    sample_polar_disk,
)

# Registry mapping slug → instance. Methods are stateless.
_METHODS = {
    "separation_of_variables": SeparationOfVariablesHeat1D(),
    "sov_wave_1d": SeparationOfVariablesWave1D(),
    "dalembert_wave_1d": DAlembertWave1D(),
    "fourier_heat_line": FourierHeatLine(),
    "duhamel_heat": DuhamelHeat(),
    "laplace_heat_halfline": LaplaceHeatHalfLine(),
    "sov_laplace_rect": SeparationOfVariablesLaplaceRect(),
    "sov_laplace_disk": SeparationOfVariablesLaplaceDisk(),
    "greens_function_1d": GreensFunction1D(),
    "helmholtz_rect": HelmholtzRect(),
    "telegraph_sov": TelegraphSOV(),
    "schrodinger_well": SchrodingerInfiniteWell(),
    "characteristics_transport_1d": CharacteristicsTransport1D(),
    "burgers_inviscid": BurgersInviscid(),
    "biharmonic_beam": BiharmonicBeam(),
    "images_halfplane": ImagesHalfPlane(),
    "sov_wave_disk": WaveDisk(),
    "sov_wave_rect": WaveRect2D(),
    "sov_heat_disk": HeatDisk(),
    "sov_laplace_ball": LaplaceBall(),
    "schrodinger_oscillator": SchrodingerHarmonicOscillator(),
    "schrodinger_free": SchrodingerFreeLine(),
    "general_second_order": GeneralSecondOrder(),
}


def solve(problem: PDEProblem) -> SolutionResponse:
    """Run the full solve pipeline and return the API response."""
    choice = pick_method(problem)
    method = _METHODS[choice.method_slug]
    steps, artifacts = method.solve(problem)

    plot_data: dict | None = None
    convergence_data: dict | None = None
    try:
        plot_data, convergence_data = _sample_for(choice.method_slug, artifacts.solution_expr)
    except Exception:
        # Plot is "nice-to-have"; never let a sampling glitch break /solve.
        plot_data = None
        convergence_data = None

    return SolutionResponse(
        method=choice.method_slug,
        steps=steps,
        solution_latex=artifacts.solution_latex,
        solution_sympy_repr=sp.srepr(artifacts.solution_expr),
        plot_data=plot_data,
        convergence_data=convergence_data,
        verified=True,
    )


# ---------------------------------------------------------------------------
# Per-method sampling. Default parameter values are chosen to make the
# plots visually informative (small L, modest t window, etc.).
# ---------------------------------------------------------------------------


def _sample_for(slug: str, expr: sp.Basic) -> tuple[dict | None, dict | None]:
    x = sp.Symbol("x", real=True)
    t = sp.Symbol("t", real=True, nonnegative=True)

    if slug == "separation_of_variables":
        L, alpha = sp.Symbol("L", positive=True), sp.Symbol("alpha", positive=True)
        params = {L: 1.0, alpha: 1.0}
        plot = sample_2d(
            expr, var1=x, var2=t, var1_range=(0.0, 1.0), var2_range=(0.0, 0.5),
            parameter_values=params,
        )
        plot = {
            "kind": "surface_xt",
            "x": plot["var1"],
            "t": plot["var2"],
            "u": plot["u"],
        }
        conv = convergence_snapshots(
            expr, var1=x, var2=t, parameter_values=params,
            var1_range=(0.0, 1.0), var2_eval=0.0,
        )
        return plot, conv

    if slug == "sov_wave_1d":
        L, c = sp.Symbol("L", positive=True), sp.Symbol("c", positive=True)
        params = {L: 1.0, c: 1.0}
        plot = sample_2d(
            expr, var1=x, var2=t, var1_range=(0.0, 1.0), var2_range=(0.0, 2.0),
            parameter_values=params,
        )
        plot = {
            "kind": "surface_xt",
            "x": plot["var1"],
            "t": plot["var2"],
            "u": plot["u"],
        }
        conv = convergence_snapshots(
            expr, var1=x, var2=t, parameter_values=params,
            var1_range=(0.0, 1.0), var2_eval=0.0,
        )
        return plot, conv

    if slug == "laplace_heat_halfline":
        # Closed form involves `erfc`, which lives in scipy, not numpy —
        # so we can't use the generic `sample_2d` here (it pins
        # `modules="numpy"`). Inline sampler with scipy+numpy modules.
        plot = _sample_laplace_heat_halfline(expr)
        return plot, None

    if slug == "duhamel_heat":
        # Sampling the double-convolution numerically is expensive; we
        # provide a reasonable plot only when the expression is concrete
        # (substituting α=1) and the integral has separable structure.
        # Otherwise we return None and the front-end omits the surface.
        try:
            plot = _sample_duhamel_heat(expr)
        except Exception:
            plot = None
        return plot, None

    if slug == "fourier_heat_line":
        alpha = sp.Symbol("alpha", positive=True)
        plot = _sample_fourier_heat_line(
            expr,
            x_sym=x,
            t_sym=t,
            parameter_values={alpha: 1.0},
        )
        return plot, None

    if slug == "dalembert_wave_1d":
        c = sp.Symbol("c", positive=True)
        params = {c: 1.0}
        plot = sample_2d(
            expr, var1=x, var2=t, var1_range=(-3.0, 3.0), var2_range=(0.0, 2.0),
            parameter_values=params,
        )
        plot = {
            "kind": "surface_xt",
            "x": plot["var1"],
            "t": plot["var2"],
            "u": plot["u"],
        }
        return plot, None  # closed form → no convergence study

    if slug == "sov_laplace_rect":
        y = sp.Symbol("y", real=True)
        a, b = sp.Symbol("a", positive=True), sp.Symbol("b", positive=True)
        params = {a: 1.0, b: 1.0}
        plot = sample_2d(
            expr, var1=x, var2=y, var1_range=(0.0, 1.0), var2_range=(0.0, 1.0),
            parameter_values=params,
        )
        plot = {
            "kind": "surface_xt",
            "x": plot["var1"],
            "t": plot["var2"],
            "u": plot["u"],
        }
        conv = convergence_snapshots(
            expr, var1=x, var2=y, parameter_values=params,
            var1_range=(0.0, 1.0), var2_eval=1.0,  # snapshot at y = b
        )
        return plot, conv

    if slug == "telegraph_sov":
        L = sp.Symbol("L", positive=True)
        c = sp.Symbol("c", positive=True)
        alpha = sp.Symbol("alpha", positive=True)
        beta = sp.Symbol("beta", nonnegative=True)
        params = {L: 1.0, c: 1.0, alpha: 0.2, beta: 0.0}
        plot = sample_2d(
            expr, var1=x, var2=t, var1_range=(0.0, 1.0), var2_range=(0.0, 4.0),
            parameter_values=params,
        )
        plot = {
            "kind": "surface_xt",
            "x": plot["var1"],
            "t": plot["var2"],
            "u": plot["u"],
        }
        # Convergence at t = 0 (just the position profile).
        conv = convergence_snapshots(
            expr, var1=x, var2=t, parameter_values=params,
            var1_range=(0.0, 1.0), var2_eval=0.0,
        )
        return plot, conv

    # ---- 1D line plots ----------------------------------------------------

    if slug == "greens_function_1d":
        L = sp.Symbol("L", positive=True)
        plot = sample_line(
            expr,
            x_sym=x,
            x_range=(0.0, 1.0),
            parameter_values={L: 1.0},
            x_label="x",
            y_label="u(x)",
        )
        return plot, None

    if slug == "biharmonic_beam":
        L = sp.Symbol("L", positive=True)
        EI = sp.Symbol("EI", positive=True)
        # The series truncates fast (1/n^4), so 30 terms is plenty.
        plot = _sample_beam_line(expr, x_sym=x, params={L: 1.0, EI: 1.0})
        return plot, None

    # ---- Polar disc plots (Bessel-series methods) -------------------------

    if slug == "sov_laplace_disk":
        r = sp.Symbol("r", nonnegative=True)
        theta = sp.Symbol("theta", real=True)
        R = sp.Symbol("R", positive=True)
        plot = sample_polar_disk(
            expr,
            r_sym=r,
            theta_sym=theta,
            R_value=1.0,
            parameter_values={R: 1.0},
            n_terms=20,
        )
        return plot, None

    if slug == "sov_heat_disk":
        r = sp.Symbol("r", nonnegative=True)
        R = sp.Symbol("R", positive=True)
        alpha = sp.Symbol("alpha", positive=True)
        # Show u(x, y) at a fixed early time so the initial profile is visible
        # but some decay is also apparent.
        plot = sample_polar_disk(
            expr,
            r_sym=r,
            theta_sym=None,
            R_value=1.0,
            parameter_values={R: 1.0, alpha: 1.0},
            extra_subs={t: 0.02},
            n_terms=12,
        )
        return plot, None

    if slug == "sov_wave_rect":
        plot = _sample_wave_rect(expr, x_sym=x, t_sym=t)
        return plot, None

    if slug == "sov_wave_disk":
        r = sp.Symbol("r", nonnegative=True)
        R = sp.Symbol("R", positive=True)
        c = sp.Symbol("c", positive=True)
        plot = sample_polar_disk(
            expr,
            r_sym=r,
            theta_sym=None,
            R_value=1.0,
            parameter_values={R: 1.0, c: 1.0},
            extra_subs={t: 0.0},  # initial profile snapshot
            n_terms=12,
        )
        return plot, None

    # ---- Meridional slice of the ball -------------------------------------

    if slug == "sov_laplace_ball":
        r = sp.Symbol("r", nonnegative=True)
        theta = sp.Symbol("theta", real=True)
        R = sp.Symbol("R", positive=True)
        plot = sample_meridional_slice(
            expr,
            r_sym=r,
            theta_sym=theta,
            R_value=1.0,
            parameter_values={R: 1.0},
            n_terms=8,  # Legendre series; ell=0..7 is plenty
        )
        return plot, None

    # ---- Half-plane: numerical Poisson convolution ----------------------

    if slug == "images_halfplane":
        y_sym = sp.Symbol("y", positive=True)
        # Half-plane has no extra parameters that need numerical defaults
        # (geometry is the upper half plane; user-supplied `f(x)` may
        # carry its own constants but those land in `expr.free_symbols`
        # and the user's parameter map ought to define them — we don't
        # auto-fill them here).
        plot = sample_halfplane_poisson(
            expr,
            x_sym=x,
            y_sym=y_sym,
        )
        return plot, None

    # ---- Helmholtz on a rectangle ---------------------------------------

    if slug == "helmholtz_rect":
        y_sym = sp.Symbol("y", real=True)
        a_sym, b_sym = sp.Symbol("a", positive=True), sp.Symbol("b", positive=True)
        k_sym = sp.Symbol("k", positive=True)
        plot = sample_helmholtz_rect(
            expr,
            x_sym=x,
            y_sym=y_sym,
            a_sym=a_sym,
            b_sym=b_sym,
            k_sym=k_sym,
        )
        return plot, None

    # ---- Quantum harmonic oscillator: |ψ|² as a function of (x, t) -------

    if slug == "burgers_inviscid":
        # The artifact is u - u_0(x - u·t) = 0 (implicit). We sample by
        # numerical inversion at each grid point, stopping early if the
        # method fails to converge (likely past the breaking time).
        plot = _sample_burgers(expr, x_sym=x, t_sym=t)
        return plot, None

    if slug == "schrodinger_oscillator":
        plot = _sample_oscillator_density(expr, x_sym=x, t_sym=t)
        return plot, None

    if slug == "schrodinger_free":
        plot = _sample_schrodinger_free_density(expr, x_sym=x, t_sym=t)
        return plot, None

    return None, None


def _sample_oscillator_density(
    expr: sp.Basic,
    *,
    x_sym: sp.Symbol,
    t_sym: sp.Symbol,
    n_terms: int = 8,
    n_grid: tuple[int, int] = (60, 40),
    x_range: tuple[float, float] = (-4.0, 4.0),
    t_max: float = 6.28,
) -> dict:
    """Render the probability density `|ψ(x, t)|²` for the oscillator.

    Why density and not `ψ`
    -----------------------
    The wavefunction is complex-valued, so plotting it directly would
    require either the real part, the imaginary part, or both. The
    physically meaningful observable is the **probability density**
    `|ψ|²`, which is what students see in QM textbooks. For a single
    eigenstate it's time-independent (the eigenfunction's gaussian-
    times-Hermite shape); for a superposition it oscillates back and
    forth with frequency `(E_n − E_m)/ℏ`.

    Default constants
    -----------------
    Set `ℏ = m = ω = 1`. The natural length scale is then
    `ℓ = √(ℏ/(mω)) = 1`, so `x ∈ [-4, 4]` is comfortable for any
    eigenstate up to `n ≈ 6`. The time range covers one classical
    period `2π/ω = 2π ≈ 6.28`, which lets a superposition oscillate
    back to its starting density once.
    """
    import numpy as np

    hbar = sp.Symbol("hbar", positive=True)
    m = sp.Symbol("m", positive=True)
    omega = sp.Symbol("omega", positive=True)
    param_subs = {hbar: 1.0, m: 1.0, omega: 1.0}

    if not isinstance(expr, sp.Sum):
        return None  # unexpected shape — defer to the empty-plot fallback

    dummies, body = _flatten_sum(expr)
    # We truncate to the first `n_terms` eigenstates. For a Gaussian
    # initial condition centered at the origin, most of the weight is in
    # the first few modes.
    syms = [d for d, _ in dummies]
    ranges = [range(lo, lo + n_terms) for _, lo in dummies]

    import itertools

    total = sp.S.Zero
    for vals in itertools.product(*ranges):
        term_k = body.subs(dict(zip(syms, vals, strict=True)))
        if term_k.has(sp.Integral):
            term_k = term_k.doit()
        total = total + term_k

    total = total.subs(param_subs)
    # `lambdify` returns complex values; we square-modulus on the
    # numpy side.
    f = sp.lambdify((x_sym, t_sym), total, modules=["scipy", "numpy"])

    xs = np.linspace(*x_range, n_grid[0])
    ts = np.linspace(0.0, t_max, n_grid[1])
    X, Tt = np.meshgrid(xs, ts, indexing="xy")

    psi = np.asarray(f(X, Tt), dtype=complex)
    density = np.abs(psi) ** 2

    return {
        "kind": "surface_xt",
        "x": xs.tolist(),
        "t": ts.tolist(),
        "u": density.tolist(),
    }


def _flatten_sum(expr: sp.Basic) -> tuple[list[tuple[sp.Symbol, int]], sp.Basic]:
    """Mirror of `numerics._flatten_sum_limits`, kept private here so
    pipeline.py doesn't need to import that helper."""
    if not isinstance(expr, sp.Sum):
        return [], expr
    dummies = [(L[0], int(L[1])) for L in expr.limits]
    inner_dummies, body = _flatten_sum(expr.function)
    return dummies + inner_dummies, body


# ---------------------------------------------------------------------------
# Helpers used only by `_sample_for`
# ---------------------------------------------------------------------------


def _sample_wave_rect(
    expr: sp.Basic,
    *,
    x_sym: sp.Symbol,
    t_sym: sp.Symbol,
    n_terms: int = 6,
    n_grid: tuple[int, int] = (40, 40),
) -> dict:
    """Render the initial-profile snapshot of u(x, y, 0) for the rectangular drum.

    The artifact is a double Sum whose general term contains an
    Integral (the coefficient A_{mn}). We truncate the sum to
    n_terms × n_terms, evaluate each integral symbolically (most are
    zero by orthogonality except for the modes present in f), and
    lambdify the resulting closed-form expression at t = 0.
    """
    import itertools

    import numpy as np

    y_sym = sp.Symbol("y", real=True)
    a = sp.Symbol("a", positive=True)
    b = sp.Symbol("b", positive=True)
    c = sp.Symbol("c", positive=True)
    params = {a: 1.0, b: 1.0, c: 1.0}

    # Snapshot at t = 0.
    snapshot = expr.subs(t_sym, 0)
    # Peel the nested Sum to find dummies + body.
    dummies: list[tuple[sp.Symbol, int]] = []
    body = snapshot
    while isinstance(body, sp.Sum):
        for d in body.limits:
            dummies.append((d[0], int(d[1])))
        body = body.function

    syms = [d for d, _ in dummies]
    ranges = [range(lo, lo + n_terms) for _, lo in dummies]

    total = sp.S.Zero
    for vals in itertools.product(*ranges):
        term = body.subs(dict(zip(syms, vals, strict=True)))
        if term.has(sp.Integral):
            term = term.doit()
        total = total + term

    total = sp.simplify(total.subs(params))

    free = total.free_symbols
    bound = tuple(s for s in (x_sym, y_sym) if s in free)
    if not bound:
        U = np.full((n_grid[1], n_grid[0]), float(total))
        xs = np.linspace(0.0, 1.0, n_grid[0])
        ys = np.linspace(0.0, 1.0, n_grid[1])
        return {
            "kind": "surface_xy",
            "x": xs.tolist(),
            "y": ys.tolist(),
            "u": U.tolist(),
            "x_label": "x",
            "y_label": "y",
        }
    f_num = sp.lambdify(bound, total, modules=["scipy", "numpy"])
    xs = np.linspace(0.0, 1.0, n_grid[0])
    ys = np.linspace(0.0, 1.0, n_grid[1])
    X, Y = np.meshgrid(xs, ys, indexing="xy")
    if bound == (x_sym, y_sym):
        U = np.asarray(f_num(X, Y), dtype=float)
    elif bound == (x_sym,):
        U = np.asarray(f_num(X), dtype=float)
    else:
        U = np.asarray(f_num(Y), dtype=float)
    return {
        "kind": "surface_xy",
        "x": xs.tolist(),
        "y": ys.tolist(),
        "u": U.tolist(),
        "x_label": "x",
        "y_label": "y",
    }


def _sample_duhamel_heat(
    expr: sp.Basic,
    *,
    x_range: tuple[float, float] = (-3.0, 3.0),
    t_range: tuple[float, float] = (0.05, 1.5),
    n_grid: tuple[int, int] = (40, 25),
    quad_limit: float = 12.0,
) -> dict:
    """Sample u(x, t) for the Duhamel heat formula.

    The artifact is one or two unevaluated Integrals (homogeneous +
    forcing). We split the expression into addends and numerically
    integrate each via ``scipy.integrate.nquad`` after substituting
    α → 1 and lambdifying the integrand. Single (y) integrals come
    from the homogeneous part; double (y, s) integrals from the
    forcing.
    """
    import numpy as np
    from scipy.integrate import quad

    alpha = sp.Symbol("alpha", positive=True)
    x_sym = sp.Symbol("x", real=True)
    t_sym = sp.Symbol("t", real=True, nonnegative=True)

    expr_concrete = expr.subs(alpha, 1.0)

    # Decompose into a list of terms (each term carries its own integral).
    if isinstance(expr_concrete, sp.Add):
        terms = list(expr_concrete.args)
    else:
        terms = [expr_concrete]

    integral_terms: list[sp.Integral] = []
    constant_terms: list[sp.Basic] = []
    for term in terms:
        if isinstance(term, sp.Integral):
            integral_terms.append(term)
        else:
            constant_terms.append(term)

    xs = np.linspace(*x_range, n_grid[0])
    ts = np.linspace(*t_range, n_grid[1])
    U = np.zeros((len(ts), len(xs)), dtype=float)

    # Constant terms (no integration needed).
    if constant_terms:
        const_total = sum(constant_terms, sp.S.Zero)
        free = const_total.free_symbols
        bound = tuple(s for s in (x_sym, t_sym) if s in free)
        if bound:
            f = sp.lambdify(bound, const_total, modules=["scipy", "numpy"])
            X, Tt = np.meshgrid(xs, ts, indexing="xy")
            if bound == (x_sym, t_sym):
                U += np.asarray(f(X, Tt), dtype=float)
            elif bound == (x_sym,):
                U += np.asarray(f(X), dtype=float)
            elif bound == (t_sym,):
                U += np.asarray(f(Tt), dtype=float)
        else:
            U += float(const_total)

    # Each integral term: single (y) or double (y, s).
    for integral in integral_terms:
        integrand = integral.function
        limits = integral.limits  # tuple of (var, lower, upper) tuples
        if len(limits) == 1:
            y_var, lo, hi = limits[0]
            g = sp.lambdify(
                (x_sym, t_sym, y_var), integrand, modules=["scipy", "numpy"]
            )
            lo_v = float(lo) if lo not in (-sp.oo, sp.oo) else -quad_limit
            hi_v = float(hi) if hi not in (-sp.oo, sp.oo) else quad_limit
            for i, tv in enumerate(ts):
                for j, xv in enumerate(xs):
                    try:
                        val, _ = quad(
                            lambda yv, xv=xv, tv=tv: g(xv, tv, yv),
                            lo_v,
                            hi_v,
                            limit=60,
                        )
                        U[i, j] += val
                    except Exception:
                        continue
        elif len(limits) == 2:
            # Outer limit listed first by SymPy's Integral; in our
            # construction we pass (y, ±∞) then (s, 0, t).
            inner_var, inner_lo, inner_hi = limits[0]
            outer_var, outer_lo, outer_hi = limits[1]
            g = sp.lambdify(
                (x_sym, t_sym, inner_var, outer_var),
                integrand,
                modules=["scipy", "numpy"],
            )
            lo_in = (
                float(inner_lo) if inner_lo not in (-sp.oo, sp.oo) else -quad_limit
            )
            hi_in = (
                float(inner_hi) if inner_hi not in (-sp.oo, sp.oo) else quad_limit
            )
            for i, tv in enumerate(ts):
                # Outer integration in s ∈ [0, t]; here outer_hi is t (symbol).
                s_hi = (
                    float(tv)
                    if outer_hi == t_sym
                    else float(outer_hi)
                    if outer_hi not in (-sp.oo, sp.oo)
                    else quad_limit
                )
                s_lo = float(outer_lo) if outer_lo not in (-sp.oo, sp.oo) else 0.0
                if s_hi <= s_lo:
                    continue
                for j, xv in enumerate(xs):
                    def outer(sv, xv=xv, tv=tv):
                        try:
                            val, _ = quad(
                                lambda yv, sv=sv, xv=xv, tv=tv: g(xv, tv, yv, sv),
                                lo_in,
                                hi_in,
                                limit=40,
                            )
                            return val
                        except Exception:
                            return 0.0

                    try:
                        # Use a small δ before s = t to avoid the 1/√(t-s)
                        # singularity in G(·, t-s).
                        s_hi_safe = max(s_lo, s_hi - 1e-4)
                        val, _ = quad(outer, s_lo, s_hi_safe, limit=30)
                        U[i, j] += val
                    except Exception:
                        continue

    return {
        "kind": "surface_xt",
        "x": xs.tolist(),
        "t": ts.tolist(),
        "u": U.tolist(),
    }


def _sample_burgers(
    expr: sp.Basic,
    *,
    x_sym: sp.Symbol,
    t_sym: sp.Symbol,
    x_range: tuple[float, float] = (-3.0, 3.0),
    t_range: tuple[float, float] = (0.0, 1.5),
    n_grid: tuple[int, int] = (60, 30),
) -> dict:
    """Sample u(x, t) for Burgers by numerically inverting u = u_0(x - u t).

    The artifact ``expr`` is ``u - u_0(x - u t)``; we extract ``u_0`` by
    substituting back and use ``scipy.optimize.brentq`` to find a root in
    a wide bracket [u_min, u_max] estimated from the range of u_0 over a
    coarse sweep. When the bracket fails (typically past the breaking
    time), we leave NaN — but the plot library will smooth or omit those
    cells. As a safety, NaN cells get the value of the last valid time
    slice for plotting continuity.
    """
    import numpy as np
    from scipy.optimize import brentq

    # Recover u_0 by substituting (x_sym, t_sym) -> (z, 0) into
    # u - u_0(x - u t). With t = 0 the implicit equation becomes
    # u = u_0(x), so u_0(z) = -expr_at_t0(u=0, x=z) evaluated as a function.
    u_sym = sp.Symbol("u")
    # expr = u - u_0(x - u t). At t = 0: expr = u - u_0(x).
    # So u_0(x) = u - expr|_{t=0} when u = anything; cleaner: u_0(x) = -expr|_{t=0, u=0}.
    u0_expr = sp.simplify(-expr.subs({t_sym: 0, u_sym: 0}))
    u0 = sp.lambdify(x_sym, u0_expr, modules=["scipy", "numpy"])

    xs = np.linspace(*x_range, n_grid[0])
    ts = np.linspace(*t_range, n_grid[1])

    # Estimate amplitude of u_0 to fix the brentq bracket.
    sweep = np.linspace(x_range[0] - 2.0, x_range[1] + 2.0, 200)
    u0_sweep = np.asarray(u0(sweep), dtype=float)
    u_lo, u_hi = float(np.nanmin(u0_sweep)), float(np.nanmax(u0_sweep))
    margin = max(0.5, (u_hi - u_lo) * 0.5)
    bracket = (u_lo - margin, u_hi + margin)

    U = np.full((len(ts), len(xs)), np.nan, dtype=float)
    for i, tv in enumerate(ts):
        for j, xv in enumerate(xs):
            # Solve g(u) = u - u_0(xv - u*tv) = 0.
            def g(u_val, xv=xv, tv=tv):
                return float(u_val - u0(xv - u_val * tv))

            try:
                if abs(tv) < 1e-12:
                    val = float(u0(xv))
                else:
                    g_lo, g_hi = g(bracket[0]), g(bracket[1])
                    if g_lo * g_hi > 0:
                        # No sign change — most likely past breaking
                        # time or outside the valid range. Skip.
                        continue
                    val = brentq(g, bracket[0], bracket[1])
                U[i, j] = val
            except (ValueError, RuntimeError):
                continue

    # Fill any remaining NaNs with the value from the previous t slice
    # (so the surface stays continuous past the breaking point).
    for i in range(1, len(ts)):
        mask = np.isnan(U[i])
        U[i, mask] = U[i - 1, mask]
    # Any remaining NaNs at t=0 fill with 0 (shouldn't happen for sane u_0).
    U[np.isnan(U)] = 0.0

    return {
        "kind": "surface_xt",
        "x": xs.tolist(),
        "t": ts.tolist(),
        "u": U.tolist(),
    }


def _sample_laplace_heat_halfline(
    expr: sp.Basic,
    *,
    x_range: tuple[float, float] = (0.0, 4.0),
    t_range: tuple[float, float] = (0.02, 1.5),
    n_grid: tuple[int, int] = (60, 40),
) -> dict:
    """Sample u(x, t) = h · erfc(x/(2 α √t)) on a Cartesian grid.

    Standalone because ``sample_2d`` pins lambdify to ``modules="numpy"``
    and ``erfc`` lives in ``scipy.special``. We default any free
    parameter (typically α and h) to 1.0.
    """
    import numpy as np

    x_nn = sp.Symbol("x", real=True, nonnegative=True)
    t_nn = sp.Symbol("t", real=True, nonnegative=True)
    param_syms = sorted(
        (s for s in expr.free_symbols if s.name not in {"x", "t"}),
        key=lambda s: s.name,
    )
    f = sp.lambdify(
        (x_nn, t_nn, *param_syms), expr, modules=["scipy", "numpy"]
    )
    xs = np.linspace(*x_range, n_grid[0])
    ts = np.linspace(*t_range, n_grid[1])
    X, Tt = np.meshgrid(xs, ts, indexing="xy")
    U = np.asarray(f(X, Tt, *(1.0 for _ in param_syms)), dtype=float)
    return {
        "kind": "surface_xt",
        "x": xs.tolist(),
        "t": ts.tolist(),
        "u": U.tolist(),
    }


def _sample_schrodinger_free_density(
    expr: sp.Basic,
    *,
    x_sym: sp.Symbol,
    t_sym: sp.Symbol,
    x_range: tuple[float, float] = (-6.0, 6.0),
    t_range: tuple[float, float] = (0.05, 2.0),
    n_grid: tuple[int, int] = (60, 40),
    quad_limit: float = 30.0,
) -> dict:
    """Render the probability density ``|ψ(x, t)|²`` for free Schrödinger.

    Two cases:

    - **Closed-form** ψ (SymPy evaluated the complex Gaussian
      convolution): lambdify, square modulus on the numpy side.
    - **Unevaluated integral**: numerically convolve via scipy ``quad``,
      separately for the real and imaginary parts of the integrand.

    Defaults: ``ℏ = m = 1``, density window ``[-6, 6]`` and ``t ∈ [0.05,
    2.0]`` to show wave-packet spreading over a couple of natural time
    scales (with ``ψ_0 = exp(-x²)`` the natural width doubles around
    ``t ≈ 1``).
    """
    import numpy as np

    hbar = sp.Symbol("hbar", positive=True)
    m_sym = sp.Symbol("m", positive=True)
    param_subs = {hbar: 1.0, m_sym: 1.0}

    expr_concrete = expr.subs(param_subs)

    xs = np.linspace(*x_range, n_grid[0])
    ts = np.linspace(*t_range, n_grid[1])

    if not expr_concrete.has(sp.Integral):
        # Closed-form complex ψ. lambdify with scipy/numpy so that
        # sqrt of negative arguments returns the principal complex
        # branch.
        free = expr_concrete.free_symbols
        bound_args = tuple(s for s in (x_sym, t_sym) if s in free)
        if not bound_args:
            psi = np.full((len(ts), len(xs)), complex(expr_concrete))
            U = np.abs(psi) ** 2
            return {
                "kind": "surface_xt",
                "x": xs.tolist(),
                "t": ts.tolist(),
                "u": U.tolist(),
            }
        f = sp.lambdify(bound_args, expr_concrete, modules=["scipy", "numpy"])
        X, Tt = np.meshgrid(xs, ts, indexing="xy")
        if bound_args == (x_sym, t_sym):
            psi = np.asarray(f(X, Tt), dtype=complex)
        elif bound_args == (x_sym,):
            psi = np.asarray(f(X), dtype=complex)
        elif bound_args == (t_sym,):
            psi = np.asarray(f(Tt), dtype=complex)
        else:
            psi = np.full_like(X, complex(expr_concrete))
        U = np.abs(psi) ** 2
        return {
            "kind": "surface_xt",
            "x": xs.tolist(),
            "t": ts.tolist(),
            "u": U.tolist(),
        }

    # Unevaluated integral case: numerically compute ψ as
    # prefactor(t) · ∫ kernel(x, t, y) ψ_0(y) dy.
    integral = None
    for arg in sp.preorder_traversal(expr_concrete):
        if isinstance(arg, sp.Integral):
            integral = arg
            break
    if integral is None:
        return {
            "kind": "surface_xt",
            "x": xs.tolist(),
            "t": ts.tolist(),
            "u": [[0.0] * len(xs) for _ in ts],
        }

    prefactor = sp.simplify(expr_concrete / integral)
    integrand = integral.function
    y_var = integral.limits[0][0]

    pre = sp.lambdify((t_sym,), prefactor, modules=["scipy", "numpy"])
    g_re = sp.lambdify(
        (x_sym, t_sym, y_var), sp.re(integrand), modules=["scipy", "numpy"]
    )
    g_im = sp.lambdify(
        (x_sym, t_sym, y_var), sp.im(integrand), modules=["scipy", "numpy"]
    )

    from scipy.integrate import quad

    U = np.zeros((len(ts), len(xs)), dtype=float)
    for i, tv in enumerate(ts):
        pref = complex(pre(tv))
        for j, xv in enumerate(xs):
            re_val, _ = quad(
                lambda yv: g_re(xv, tv, yv),
                -quad_limit,
                quad_limit,
                limit=80,
            )
            im_val, _ = quad(
                lambda yv: g_im(xv, tv, yv),
                -quad_limit,
                quad_limit,
                limit=80,
            )
            psi_val = pref * complex(re_val, im_val)
            U[i, j] = abs(psi_val) ** 2
    return {
        "kind": "surface_xt",
        "x": xs.tolist(),
        "t": ts.tolist(),
        "u": U.tolist(),
    }


def _sample_fourier_heat_line(
    expr: sp.Basic,
    *,
    x_sym: sp.Symbol,
    t_sym: sp.Symbol,
    parameter_values: dict[sp.Symbol, float],
    x_range: tuple[float, float] = (-4.0, 4.0),
    t_range: tuple[float, float] = (0.02, 1.5),
    n_grid: tuple[int, int] = (60, 40),
    quad_limit: float = 30.0,
) -> dict:
    """Render ``u(x, t)`` for the heat equation on the real line.

    The solver may emit two shapes:

    - **Closed form** (when SymPy evaluated the convolution integral —
      e.g., for Gaussian or polynomial × Gaussian initial conditions):
      lambdify directly.
    - **Unevaluated** ``sp.Integral``: lambdify the integrand over
      ``(x, t, y)`` and run scipy ``quad`` for each grid point.

    We start ``t`` slightly above zero to avoid the singular factor
    ``1/√(4π α² t)`` at exactly ``t = 0``.
    """
    import numpy as np

    xs = np.linspace(*x_range, n_grid[0])
    ts = np.linspace(*t_range, n_grid[1])

    expr_concrete = expr.subs(parameter_values)

    if not expr_concrete.has(sp.Integral):
        free = expr_concrete.free_symbols
        bound_args = tuple(s for s in (x_sym, t_sym) if s in free)
        if not bound_args:
            U = np.full((len(ts), len(xs)), float(expr_concrete))
            return {
                "kind": "surface_xt",
                "x": xs.tolist(),
                "t": ts.tolist(),
                "u": U.tolist(),
            }
        f = sp.lambdify(bound_args, expr_concrete, modules=["scipy", "numpy"])
        X, Tt = np.meshgrid(xs, ts, indexing="xy")
        if bound_args == (x_sym, t_sym):
            U = np.asarray(f(X, Tt), dtype=float)
        elif bound_args == (x_sym,):
            U = np.asarray(f(X), dtype=float)
        elif bound_args == (t_sym,):
            U = np.asarray(f(Tt), dtype=float)
        else:
            U = np.full_like(X, float(expr_concrete))
        return {
            "kind": "surface_xt",
            "x": xs.tolist(),
            "t": ts.tolist(),
            "u": U.tolist(),
        }

    # Unevaluated integral: convolve numerically. We strip the prefactor
    # and integration explicitly to lambdify a clean (x, t, y) callable.
    integral = None
    for arg in sp.preorder_traversal(expr_concrete):
        if isinstance(arg, sp.Integral):
            integral = arg
            break
    if integral is None:
        return {
            "kind": "surface_xt",
            "x": xs.tolist(),
            "t": ts.tolist(),
            "u": [[0.0] * len(xs) for _ in ts],
        }

    prefactor = sp.simplify(expr_concrete / integral)
    integrand = integral.function
    y_var = integral.limits[0][0]

    pre = sp.lambdify((t_sym,), prefactor, modules=["scipy", "numpy"])
    g = sp.lambdify((x_sym, t_sym, y_var), integrand, modules=["scipy", "numpy"])

    from scipy.integrate import quad

    U = np.zeros((len(ts), len(xs)), dtype=float)
    for i, tv in enumerate(ts):
        pref_val = float(pre(tv))
        for j, xv in enumerate(xs):
            val, _err = quad(
                lambda yv: g(xv, tv, yv),
                -quad_limit,
                quad_limit,
                limit=80,
            )
            U[i, j] = pref_val * val
    return {
        "kind": "surface_xt",
        "x": xs.tolist(),
        "t": ts.tolist(),
        "u": U.tolist(),
    }


def _sample_beam_line(
    expr: sp.Basic,
    *,
    x_sym: sp.Symbol,
    params: dict[sp.Symbol, float],
    n_terms: int = 30,
    nx: int = 200,
) -> dict:
    """Sample the simply-supported-beam series on [0, L].

    The result is `u(x) = Σ A_n sin(nπx/L)` with A_n proportional to 1/n^4.
    We truncate to `n_terms` and use the existing _evaluate_radial logic
    to handle the Sum.

    For consistency with `sample_line`, the return value is tagged
    `kind: "line"` and exposes `x`, `u`, plus axis labels.
    """
    import numpy as np

    L_sym = next(s for s in params if s.name == "L")
    L_val = params[L_sym]

    # Truncate the Sum to n_terms.
    if isinstance(expr, sp.Sum):
        dummy, lower, _ = expr.limits[0]
        start = int(lower)
        # Build the truncated explicit sum.
        truncated = sum(expr.function.subs(dummy, k) for k in range(start, start + n_terms))
    else:
        truncated = expr
    truncated_concrete = truncated.subs(params)

    free = list(truncated_concrete.free_symbols)
    if x_sym not in free:
        # Constant — degenerate but possible.
        xs = np.linspace(0.0, L_val, nx)
        ys = np.full_like(xs, float(truncated_concrete))
    else:
        f = sp.lambdify(x_sym, truncated_concrete, modules="numpy")
        xs = np.linspace(0.0, L_val, nx)
        ys = np.asarray(f(xs), dtype=float)

    return {
        "kind": "line",
        "x": xs.tolist(),
        "u": ys.tolist(),
        "x_label": "x",
        "y_label": "u(x)",
    }
