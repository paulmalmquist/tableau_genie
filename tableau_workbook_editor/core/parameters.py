"""Parameter helpers."""
from __future__ import annotations

from typing import List, Optional

from .xml_utils import Element, etree, xpath


PARAMETERS_XPATH = "./parameters/parameter"


def list_parameters(root: Element) -> List[str]:
    return [param.get("name") or "" for param in xpath(root, PARAMETERS_XPATH)]


def find_parameter(root: Element, name: str) -> Optional[Element]:
    for param in xpath(root, PARAMETERS_XPATH):
        if param.get("name") == name:
            return param
    return None


def ensure_parameters_parent(root: Element) -> Element:
    parent = root.find("parameters")
    if parent is None:
        parent = etree.Element("parameters")
        root.append(parent)
    return parent


def create_parameter(root: Element, name: str, data_type: str, value: str) -> Element:
    parent = ensure_parameters_parent(root)
    param = etree.Element("parameter")
    param.set("name", name)
    param.set("datatype", data_type)
    param.set("current-value", value)
    parent.append(param)
    return param
