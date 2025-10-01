"""Action helpers."""
from __future__ import annotations

from typing import Dict, List

from .xml_utils import Element, etree, xpath


ACTIONS_XPATH = "./actions/action"


def list_actions(root: Element) -> List[Element]:
    return list(xpath(root, ACTIONS_XPATH))


def ensure_actions_parent(root: Element) -> Element:
    actions_parent = root.find("actions")
    if actions_parent is None:
        actions_parent = etree.Element("actions")
        root.append(actions_parent)
    return actions_parent


def create_filter_action(root: Element, source: str, target: str, mapping: Dict[str, str]) -> Element:
    actions_parent = ensure_actions_parent(root)
    action = etree.Element("action")
    action.set("type", "filter")
    action.set("source", source)
    action.set("target", target)
    if mapping:
        pairs = [f"{src}={dst}" for src, dst in mapping.items()]
        action.set("mapping", "; ".join(pairs))
    actions_parent.append(action)
    return action
