"""Datasource helpers."""
from __future__ import annotations

from typing import Iterable, List, Optional

from .xml_utils import Element, etree, xpath


DATASOURCES_XPATH = "./datasources/datasource"


def list_datasource_names(root: Element) -> List[str]:
    return [ds.get("name") or ds.get("caption") or "" for ds in xpath(root, DATASOURCES_XPATH)]


def find_datasource(root: Element, name: str) -> Optional[Element]:
    for ds in xpath(root, DATASOURCES_XPATH):
        if ds.get("name") == name or ds.get("caption") == name:
            return ds
    return None


def list_columns(datasource: Element) -> List[Element]:
    return list(xpath(datasource, "./column"))


def find_column(datasource: Element, name: str) -> Optional[Element]:
    for column in list_columns(datasource):
        if column.get("caption") == name or column.get("name") == name or column.get("name") == f"[{name}]":
            return column
        if column.get("caption") == f"[{name}]":
            return column
    return None


def ensure_column_name(column: Element) -> str:
    name = column.get("name")
    if name:
        return name
    caption = column.get("caption") or "Unnamed"
    formatted = caption if caption.startswith("[") else f"[{caption}]"
    column.set("name", formatted)
    return formatted


def update_connection(connection: Element, **attrs: str) -> None:
    for key, value in attrs.items():
        if value is None:
            continue
        connection.set(key.replace("_", "-"), value)
