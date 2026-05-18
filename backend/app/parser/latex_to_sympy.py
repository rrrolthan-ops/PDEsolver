"""LaTeX (and physicist shorthand) → SymPy.

Goals
-----
SymPy's `parse_latex` exists but it has gaps with physics notation
(subscripts as derivatives, `∂u/∂x`, `u_{xx}`, `u_t`) and is sensitive
to whitespace. We don't need a full LaTeX engine here, only:

- Recognise the common derivative shorthands used in physics:
    u_t, u_x, u_{xx}, u_{xy}, u_xx (loose), ∂u/∂x, ∂²u/∂x², u^{(2)}
- Recognise the common scalar-function strings used in initial
  conditions: ``sin(pi*x/L)``, ``x*(L-x)``, ``exp(-x^2)``…

Strategy
--------
1. Run a small pre-processor that rewrites physicist shorthand into a
   neutral form that SymPy's `sympify` can swallow: replace
   ``u_{xx}`` with ``__d2u_xx__``, etc., then once parsed, substitute
   the placeholders back to `Derivative(u(x, t), x, 2)`.
2. For scalar (non-PDE) expressions, just normalise `^` → `**`,
   `pi` → `sp.pi`, and `sympify` with our known symbols as locals.

Notes
-----
This is intentionally NOT a general LaTeX parser. The set of patterns
we handle is exactly the set that the Phase 1 piloting needs. The list
grows in lockstep with the methods we add in later phases.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import sympy as sp

from app.solver.core.symbols import KNOWN, symbol_for


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass
class ParsedPDE:
    """Result of parsing a PDE string.

    Attributes
    ----------
    expr
        SymPy expression that equals zero, i.e. LHS - RHS.
    u
        The unknown function (a `sp.Function`).
    spatial_vars
        The spatial variables detected, in order.
    time_var
        The time variable, if detected.
    """

    expr: sp.Basic
    u: sp.Function
    spatial_vars: list[sp.Symbol]
    time_var: sp.Symbol | None


def parse_pde_latex(latex: str, parameters: dict[str, str] | None = None) -> ParsedPDE:
    """Parse a PDE written in LaTeX or physicist shorthand."""
    parameters = parameters or {}
    locals_dict = _build_locals(parameters)
    u = sp.Function("u")
    locals_dict["u"] = u

    # Split into LHS = RHS if present, otherwise treat as = 0.
    if "=" in latex:
        lhs, rhs = latex.split("=", 1)
    else:
        lhs, rhs = latex, "0"

    lhs_norm, vars_lhs = _normalise(lhs)
    rhs_norm, vars_rhs = _normalise(rhs)

    detected = vars_lhs | vars_rhs
    spatial = [v for v in ("x", "y", "z") if v in detected]
    time_var = "t" if "t" in detected else None

    # Compose arguments for u(...).
    args_in_order = spatial + ([time_var] if time_var else [])
    if not args_in_order:
        # Fallback: assume u(x, t) — the most common shape.
        args_in_order = ["x", "t"]
    u_args = tuple(symbol_for(v) for v in args_in_order)
    u_call = u(*u_args)

    # Replace the placeholder derivative tokens by real `Derivative(u, ...)`.
    lhs_expr = _sympify_with_placeholders(lhs_norm, u_call, locals_dict)
    rhs_expr = _sympify_with_placeholders(rhs_norm, u_call, locals_dict)

    expr = sp.expand(lhs_expr - rhs_expr)

    return ParsedPDE(
        expr=expr,
        u=u,
        spatial_vars=[symbol_for(v) for v in spatial],
        time_var=symbol_for(time_var) if time_var else None,
    )


def parse_scalar_latex(latex: str, parameters: dict[str, str] | None = None) -> sp.Basic:
    """Parse a scalar (non-PDE) expression like an initial profile.

    Accepts physics-flavoured notation: `pi`, `^` for powers, `sin`,
    `cos`, etc.
    """
    parameters = parameters or {}
    locals_dict = _build_locals(parameters)

    normalised = _normalise_scalar(latex)
    return sp.sympify(normalised, locals=locals_dict)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _build_locals(parameters: dict[str, str]) -> dict[str, sp.Basic]:
    """Build the locals dict used by `sympify`.

    Pre-loads our well-known symbols (x, t, L, alpha, …) and any
    user-declared parameters with their assumptions.
    """
    locals_dict: dict[str, sp.Basic] = dict(KNOWN)
    for name, assumption in parameters.items():
        locals_dict[name] = symbol_for(name, assumption=assumption)
    return locals_dict


# Regexes for physicist derivative shorthand.
# Order matters: longer / more specific patterns first.

_PARTIAL_FRACTION = re.compile(
    r"""
    \\?frac\s*\{\s*\\?partial\s*(?:\^\s*(?P<num_order>\d+))?\s*u\s*\}
    \s*\{\s*\\?partial\s*(?P<var1>[xyzt])\s*(?:\^\s*(?P<den_order1>\d+))?
    (?:\s*\\?partial\s*(?P<var2>[xyzt])\s*(?:\^\s*(?P<den_order2>\d+))?)?
    \s*\}
    """,
    re.VERBOSE,
)

# Matches u_{xx}, u_{xy}, u_{xxx}, u_{tt}, etc.
_BRACED_SUB = re.compile(r"u_\{\s*([xyzt]+)\s*\}")

# Matches u_x, u_t (no braces). Single letter only.
_BARE_SUB = re.compile(r"u_([xyzt])(?![A-Za-z0-9_])")


def _normalise(text: str) -> tuple[str, set[str]]:
    """Turn physicist LaTeX into a SymPy-friendly string with placeholders.

    Returns the normalised text *and* the set of independent variables
    we saw mentioned (e.g. {"x", "t"}).
    """
    text = text.strip()
    text = text.replace("∂", r"\partial")
    text = text.replace("·", "*")
    text = text.replace("⋅", "*")

    seen: set[str] = set()

    # 1. \frac{\partial^k u}{\partial x^p ...} → __DERIV_x_p_y_q__
    def _frac_repl(m: re.Match) -> str:
        v1 = m.group("var1")
        o1 = int(m.group("den_order1") or 1)
        v2 = m.group("var2")
        o2 = int(m.group("den_order2") or 1) if v2 else 0
        seen.add(v1)
        if v2:
            seen.add(v2)
            return _deriv_token([(v1, o1), (v2, o2)])
        return _deriv_token([(v1, o1)])

    text = _PARTIAL_FRACTION.sub(_frac_repl, text)

    # 2. u_{xx}, u_{xy}, u_{xxx}, u_{tt} → __DERIV_x_n_..._n__
    def _braced_repl(m: re.Match) -> str:
        letters = list(m.group(1))
        # Count consecutive repetitions per variable: 'xx' -> [(x, 2)],
        # 'xy' -> [(x, 1), (y, 1)], 'xxy' -> [(x, 2), (y, 1)].
        counts: list[tuple[str, int]] = []
        for ch in letters:
            seen.add(ch)
            if counts and counts[-1][0] == ch:
                counts[-1] = (ch, counts[-1][1] + 1)
            else:
                counts.append((ch, 1))
        return _deriv_token(counts)

    text = _BRACED_SUB.sub(_braced_repl, text)

    # 3. u_x, u_t → __DERIV_x_1__
    def _bare_repl(m: re.Match) -> str:
        v = m.group(1)
        seen.add(v)
        return _deriv_token([(v, 1)])

    text = _BARE_SUB.sub(_bare_repl, text)

    # Also detect free occurrences of `x` and `t` so that even `u_xx`
    # implicitly tells us the independent variables — already covered.
    # But if the equation mentions `t` only via `u_t`, we already added it.

    # 4. Power: `^` → `**`. Do AFTER derivative handling so `u^{(2)}`
    # tricks don't interfere.
    text = text.replace("^", "**")

    return text, seen


_GREEK_BACKSLASH = (
    ("\\theta", "theta"),
    ("\\phi", "phi"),
    ("\\rho", "rho"),
    ("\\xi", "xi"),
    ("\\eta", "eta"),
    ("\\alpha", "alpha"),
    ("\\beta", "beta"),
    ("\\gamma", "gamma"),
    ("\\delta", "delta"),
    ("\\lambda", "lambda"),
    ("\\mu", "mu"),
    ("\\sigma", "sigma"),
    ("\\omega", "omega"),
    ("\\pi", "pi"),
    ("\\tau", "tau"),
)


def _normalise_scalar(text: str) -> str:
    text = text.strip()
    text = text.replace("·", "*").replace("⋅", "*")
    # Strip LaTeX backslashes from common Greek letters so that
    # sympify gets a plain identifier matching a symbol in KNOWN.
    for tex, plain in _GREEK_BACKSLASH:
        text = text.replace(tex, plain)
    text = text.replace("^", "**")
    return text


def _deriv_token(pairs: list[tuple[str, int]]) -> str:
    """Build a unique placeholder string for a derivative.

    The placeholder has the shape ``__DERIV_x_2_y_1__`` which encodes
    a second derivative in x and a first in y. We later substitute
    each unique placeholder with the corresponding
    ``Derivative(u(...), x, 2, y, 1)``.
    """
    parts = []
    for v, o in pairs:
        parts.append(f"{v}_{o}")
    return f"DERIV_{'_'.join(parts)}"


def _sympify_with_placeholders(
    text: str,
    u_call: sp.Expr,
    locals_dict: dict[str, sp.Basic],
) -> sp.Basic:
    """Sympify text containing `DERIV_x_2_y_1` placeholders.

    We register each placeholder as a `sp.Symbol` for parsing, then
    substitute it by the corresponding `sp.Derivative` after.
    """
    placeholder_re = re.compile(r"DERIV(?:_[xyzt]_\d+)+")
    found = set(placeholder_re.findall(text))

    local = dict(locals_dict)
    subs_map: dict[sp.Symbol, sp.Basic] = {}
    for name in found:
        sym = sp.Symbol(name)
        local[name] = sym
        # Decode the placeholder.
        # Strip leading "DERIV_" then split into (var, order) pairs.
        inner = name[len("DERIV_"):]
        tokens = inner.split("_")
        deriv_args: list[sp.Basic | int] = []
        for i in range(0, len(tokens), 2):
            v = tokens[i]
            o = int(tokens[i + 1])
            deriv_args.append(symbol_for(v))
            deriv_args.append(o)
        subs_map[sym] = sp.Derivative(u_call, *deriv_args)

    expr = sp.sympify(text, locals=local)
    return expr.subs(subs_map, simultaneous=True)
