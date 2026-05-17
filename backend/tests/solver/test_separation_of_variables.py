"""Tests for the heat-1D separation-of-variables method.

References
----------
- Haberman, "Applied Partial Differential Equations" (5th ed.), §2.3–§2.5.
- Tijonov & Samarsky, "Equations of Mathematical Physics" (Dover), ch. III.

Each test checks two things in parallel:

1. **Structural**: the returned `SolutionResponse` has the expected
   pedagogical shape — every step kind appears, the three λ-cases are
   covered, didactic observations are attached, etc.
2. **Symbolic**: the final `solution_expr` is algebraically equal to
   the closed-form answer from the reference.
"""

from __future__ import annotations

import sympy as sp

from app.schemas import StepKind
from app.solver import solve


# ---------------------------------------------------------------------------
# Symbolic helpers for assertions
# ---------------------------------------------------------------------------

X, T_VAR = sp.Symbol("x", real=True), sp.Symbol("t", real=True, nonnegative=True)
L_SYM = sp.Symbol("L", positive=True)
ALPHA_SYM = sp.Symbol("alpha", positive=True)
N = sp.Symbol("n", integer=True, positive=True)


def _truncated(expr: sp.Basic, n_max: int) -> sp.Basic:
    """Materialise the first `n_max` terms of a sp.Sum solution."""
    if not isinstance(expr, sp.Sum):
        return expr
    return sum(expr.function.subs(N, k) for k in range(1, n_max + 1))


def _eigen_term(k: int, Bn_val) -> sp.Basic:
    """Build the k-th term `B_k sin(kπx/L) exp(−α² (kπ/L)² t)`."""
    return (
        Bn_val
        * sp.sin(k * sp.pi * X / L_SYM)
        * sp.exp(-(ALPHA_SYM**2) * (k * sp.pi / L_SYM) ** 2 * T_VAR)
    )


# ---------------------------------------------------------------------------
# Structural tests — same for every problem
# ---------------------------------------------------------------------------

REQUIRED_KINDS: tuple[StepKind, ...] = (
    "statement",
    "classification",
    "method_choice",
    "development",
    "boundary",
    "initial",
    "final",
    "verification",
    "visualization",
    "interpretation",
)


def test_response_shape(problem_sin1):
    resp = solve(problem_sin1)

    # Method slug and verification flag.
    assert resp.method == "separation_of_variables"
    assert resp.verified is True

    # All step kinds must appear at least once — that's how we know the
    # tutor covered every section of the explanation.
    present = {s.kind for s in resp.steps}
    for kind in REQUIRED_KINDS:
        assert kind in present, f"Missing pedagogical step: {kind}"

    # The three λ-case headings must literally appear in the development
    # section. This is the most important pedagogical invariant of the
    # whole module: if any case is missing the explanation is broken.
    titles_lower = " ".join(s.title.lower() for s in resp.steps)
    assert "caso 1" in titles_lower
    assert "caso 2" in titles_lower
    assert "caso 3" in titles_lower


def test_didactic_observations_attached(problem_parabolic):
    resp = solve(problem_parabolic)
    all_obs = [o for s in resp.steps for o in s.observations]
    assert len(all_obs) >= 3, "Expected at least three didactic observations"
    kinds = {o.kind for o in all_obs}
    # We should see both intuition and a theorem-statement box.
    assert "intuition" in kinds
    assert "theorem" in kinds


def test_plot_data_present(problem_sin1):
    resp = solve(problem_sin1)
    assert resp.plot_data is not None
    assert "u" in resp.plot_data and len(resp.plot_data["u"]) > 0
    assert resp.convergence_data is not None
    assert "snapshots" in resp.convergence_data
    # The convergence study should evaluate at N = 1, 5, 20, 100.
    assert set(resp.convergence_data["snapshots"].keys()) == {"1", "5", "20", "100"}


# ---------------------------------------------------------------------------
# Symbolic tests — solution equals the closed form
# ---------------------------------------------------------------------------

def _solution_expr_from(resp) -> sp.Basic:
    """Recover the SymPy expression from `solution_sympy_repr`."""
    # We could re-import via sp.sympify(srepr) but sp.sympify of srepr
    # requires the same locals; the steps themselves carry the expr.
    final_step = next(s for s in resp.steps if s.kind == "final")
    assert final_step.sympy_repr is not None
    return sp.sympify(final_step.sympy_repr)


def test_fundamental_mode_sin1(problem_sin1):
    """f = sin(πx/L) ⇒ B_1 = 1, all other B_n = 0."""
    resp = solve(problem_sin1)
    sol = _solution_expr_from(resp)
    # Only the first eigenmode contributes.
    expected = _eigen_term(1, 1)
    truncated = sp.simplify(_truncated(sol, 5))
    assert sp.simplify(truncated - expected) == 0


def test_second_mode_sin2(problem_sin2):
    """f = sin(2πx/L) ⇒ B_2 = 1, others 0."""
    resp = solve(problem_sin2)
    sol = _solution_expr_from(resp)
    expected = _eigen_term(2, 1)
    truncated = sp.simplify(_truncated(sol, 5))
    assert sp.simplify(truncated - expected) == 0


def test_mixed_modes(problem_mixed_modes):
    """f = 3 sin(πx/L) − sin(3πx/L) ⇒ B_1 = 3, B_3 = −1, others 0."""
    resp = solve(problem_mixed_modes)
    sol = _solution_expr_from(resp)
    expected = _eigen_term(1, 3) + _eigen_term(3, -1)
    truncated = sp.simplify(_truncated(sol, 5))
    assert sp.simplify(truncated - expected) == 0


def test_parabolic_profile_at_t_zero_first_term(problem_parabolic):
    """f = x(L − x): classic Haberman example.

    The Fourier coefficients are
        B_n = (8 L² / (n³ π³))  if n is odd, else 0.
    This test checks the first nonzero coefficient (n=1) equals the
    expected closed form, by comparing the series term at n=1 with
    the reference.
    """
    resp = solve(problem_parabolic)
    sol = _solution_expr_from(resp)
    assert isinstance(sol, sp.Sum)
    term = sol.function
    n1 = sp.simplify(term.subs(N, 1).subs(T_VAR, 0))
    expected_first = sp.Rational(8) * L_SYM**2 / sp.pi**3 * sp.sin(sp.pi * X / L_SYM)
    assert sp.simplify(n1 - expected_first) == 0


def test_constant_profile_odd_coefficients(problem_constant):
    """f = 1: B_n = (4 / (n π))  for n odd, else 0.

    We probe n = 1 and n = 2 to confirm odd/even pattern.
    """
    resp = solve(problem_constant)
    sol = _solution_expr_from(resp)
    assert isinstance(sol, sp.Sum)
    term = sol.function
    # At t = 0 the exponential is 1; isolate B_n sin(nπx/L).
    b1 = sp.simplify(term.subs(N, 1).subs(T_VAR, 0) / sp.sin(sp.pi * X / L_SYM))
    b2 = sp.simplify(term.subs(N, 2).subs(T_VAR, 0))
    assert sp.simplify(b1 - sp.Rational(4) / sp.pi) == 0
    assert b2 == 0


def test_linear_profile_first_coefficient(problem_linear):
    """f = x: B_n = 2L (−1)^(n+1) / (nπ).

    Probe n = 1 → B_1 = 2L/π, n = 2 → B_2 = −L/π.
    """
    resp = solve(problem_linear)
    sol = _solution_expr_from(resp)
    assert isinstance(sol, sp.Sum)
    term = sol.function
    b1 = sp.simplify(term.subs(N, 1).subs(T_VAR, 0) / sp.sin(sp.pi * X / L_SYM))
    b2 = sp.simplify(term.subs(N, 2).subs(T_VAR, 0) / sp.sin(2 * sp.pi * X / L_SYM))
    assert sp.simplify(b1 - sp.Rational(2) * L_SYM / sp.pi) == 0
    assert sp.simplify(b2 - sp.Rational(-1) * L_SYM / sp.pi) == 0


# ---------------------------------------------------------------------------
# Verification step actually carries the symbolic checks
# ---------------------------------------------------------------------------

def test_verification_step_has_pde_check(problem_sin1):
    resp = solve(problem_sin1)
    verif_steps = [s for s in resp.steps if s.kind == "verification"]
    # Intro + PDE + BC + IC = 4
    assert len(verif_steps) >= 4
    pde_step = next(s for s in verif_steps if "EDP" in s.title or "edp" in s.title.lower())
    # The residual u_t - α² u_xx should be displayed and equal 0.
    assert "= 0" in pde_step.latex or "0." in pde_step.latex
