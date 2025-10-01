"""Utilities for working with Tableau calculations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Set


KNOWN_FUNCTIONS: Set[str] = {
    "sum",
    "avg",
    "min",
    "max",
    "lookup",
    "running_sum",
    "zn",
    "if",
    "then",
    "else",
    "elseif",
    "end",
}


@dataclass
class CalculationLintResult:
    ok: bool
    message: str = ""


def lint_calculation(formula: str) -> CalculationLintResult:
    stack = []
    for char in formula:
        if char in "(":
            stack.append(char)
        elif char == ")":
            if not stack:
                return CalculationLintResult(False, "Unbalanced parentheses")
            stack.pop()
    if stack:
        return CalculationLintResult(False, "Unbalanced parentheses")
    bracket_stack = 0
    escaped = False
    for char in formula:
        if char == "'" and not escaped:
            escaped = True
        elif char == "'" and escaped:
            escaped = False
        elif char == "[" and not escaped:
            bracket_stack += 1
        elif char == "]" and not escaped:
            bracket_stack -= 1
            if bracket_stack < 0:
                return CalculationLintResult(False, "Unbalanced field brackets")
    if bracket_stack != 0:
        return CalculationLintResult(False, "Unbalanced field brackets")
    return CalculationLintResult(True, "")
