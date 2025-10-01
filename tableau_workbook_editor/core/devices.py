"""Device layout helpers."""
from __future__ import annotations

from typing import List

from .xml_utils import Element


def list_device_layouts(dashboard: Element) -> List[Element]:
    devices = dashboard.find("device-layouts")
    if devices is None:
        return []
    return list(devices)
