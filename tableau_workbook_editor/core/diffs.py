"""Diff helpers for workbook changes."""
from __future__ import annotations

from typing import List

from .xml_utils import Element, etree


def element_to_string(element: Element) -> str:
    return etree.tostring(element, encoding="unicode")


def diff_elements(before: Element, after: Element) -> List[str]:
    before_str = element_to_string(before).splitlines()
    after_str = element_to_string(after).splitlines()
    diff: List[str] = []
    for line in before_str:
        if line not in after_str:
            diff.append(f"- {line}")
    for line in after_str:
        if line not in before_str:
            diff.append(f"+ {line}")
    return diff
