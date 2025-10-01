"""Layout helpers."""
from __future__ import annotations

from typing import List

from .xml_utils import Element


def list_layout_zones(dashboard: Element) -> List[Element]:
    zones = dashboard.find("zones")
    if zones is None:
        return []
    return list(zones)
