"""Public API for :mod:`tableau_workbook_editor`."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .core.twb_model import Workbook

__all__ = ["Workbook", "open_workbook"]


def open_workbook(path: str | Path) -> Workbook:
    """Open *path* and return a :class:`Workbook` instance."""

    return Workbook.open(path)
