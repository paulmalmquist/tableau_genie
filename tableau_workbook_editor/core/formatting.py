"""Formatting helpers."""
from __future__ import annotations

from typing import Dict

from .xml_utils import Element


def set_number_format(column: Element, format_string: str) -> None:
    column.set("format", format_string)


def set_alias(column: Element, alias: str) -> None:
    column.set("alias", alias)
