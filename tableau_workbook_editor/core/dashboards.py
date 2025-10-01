"""Dashboard helpers."""
from __future__ import annotations

from typing import List, Optional

from .xml_utils import Element, IdRegistry, etree, xpath


DASHBOARDS_XPATH = "./dashboards/dashboard"


def list_dashboards(root: Element) -> List[str]:
    return [db.get("name") or "" for db in xpath(root, DASHBOARDS_XPATH)]


def find_dashboard(root: Element, name: str) -> Optional[Element]:
    for dashboard in xpath(root, DASHBOARDS_XPATH):
        if dashboard.get("name") == name:
            return dashboard
    return None


def list_dashboard_zones(dashboard: Element) -> List[Element]:
    zones_parent = dashboard.find("zones")
    if zones_parent is None:
        return []
    return list(zones_parent)


def ensure_zones_parent(dashboard: Element) -> Element:
    zones_parent = dashboard.find("zones")
    if zones_parent is None:
        zones_parent = etree.Element("zones")
        dashboard.append(zones_parent)
    return zones_parent


def append_sheet_zone(dashboard: Element, sheet_name: str, registry: IdRegistry, *, floating: bool, container: str, index: int) -> Element:
    zones_parent = ensure_zones_parent(dashboard)
    zone = etree.Element("zone")
    zone.set("type", "worksheet")
    zone.set("worksheet", sheet_name)
    zone_id = registry.new("z")
    zone.set("id", zone_id)
    if floating:
        zone.set("floating", "true")
    if container:
        zone.set("container", container)
    zone.set("x", "0")
    zone.set("y", "0")
    zone.set("w", "400")
    zone.set("h", "300")
    children = list(zones_parent)
    if index < 0 or index >= len(children):
        zones_parent.append(zone)
    else:
        zones_parent.insert(index, zone)
    return zone


def update_zone_geometry(zone: Element, *, x: Optional[int] = None, y: Optional[int] = None, w: Optional[int] = None, h: Optional[int] = None) -> None:
    if x is not None:
        zone.set("x", str(x))
    if y is not None:
        zone.set("y", str(y))
    if w is not None:
        zone.set("w", str(w))
    if h is not None:
        zone.set("h", str(h))
