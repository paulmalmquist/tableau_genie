"""Worksheet helpers."""
from __future__ import annotations

from typing import List, Optional

from .xml_utils import Element, xpath


WORKSHEETS_XPATH = "./worksheets/worksheet"


def list_worksheets(root: Element) -> List[str]:
    return [ws.get("name") or "" for ws in xpath(root, WORKSHEETS_XPATH)]


def find_worksheet(root: Element, name: str) -> Optional[Element]:
    for worksheet in xpath(root, WORKSHEETS_XPATH):
        if worksheet.get("name") == name:
            return worksheet
    return None


def update_field_reference(worksheet: Element, *, old: str, new: str) -> int:
    changed = 0
    for node in xpath(worksheet, ".//*[@ref]"):
        if node.get("ref") == old:
            node.set("ref", new)
            changed += 1
    for node in xpath(worksheet, ".//*[@column]"):
        if node.get("column") == old:
            node.set("column", new)
            changed += 1
    return changed
