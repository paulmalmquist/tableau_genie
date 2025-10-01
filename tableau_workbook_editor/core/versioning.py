"""Workbook version helpers."""
from __future__ import annotations

from typing import Optional

from .xml_utils import Element, etree


def get_workbook_version(root: Element) -> Optional[str]:
    version_node = root.find("version")
    if version_node is None:
        return None
    return version_node.get("value") or version_node.text


def ensure_target_version(root: Element, target_version: Optional[str]) -> None:
    if target_version is None:
        return
    version_node = root.find("version")
    if version_node is None:
        version_node = etree.Element("version")
        version_node.set("value", target_version)
        root.append(version_node)
    else:
        version_node.set("value", target_version)
