"""Pedagogical content — the part that makes this app a tutor and not a calculator.

The text in this package is **deterministic** and **hand-curated**. We
deliberately avoid LLM-generated prose at runtime: a confident-sounding
explanation that's mathematically wrong would be worse than no
explanation at all. Each piece of text here was written with a specific
algebraic situation in mind and is plugged in only when that situation
arises.
"""

from . import observations, templates  # noqa: F401
