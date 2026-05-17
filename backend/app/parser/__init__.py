"""Input parsing: convert user-facing strings into SymPy expressions."""

from .latex_to_sympy import parse_pde_latex, parse_scalar_latex

__all__ = ["parse_pde_latex", "parse_scalar_latex"]
