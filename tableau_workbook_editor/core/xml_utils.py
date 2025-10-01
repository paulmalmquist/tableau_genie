"""Utilities for working with Tableau XML documents."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Optional

try:  # pragma: no cover - optional dependency
    from defusedxml.lxml import fromstring  # type: ignore
    from lxml import etree  # type: ignore
    LXML_AVAILABLE = True
except Exception:  # pragma: no cover - fallback path
    try:
        from defusedxml.ElementTree import fromstring  # type: ignore
    except Exception:  # pragma: no cover - final fallback
        from xml.etree.ElementTree import fromstring  # type: ignore
    from xml.etree import ElementTree as etree  # type: ignore
    LXML_AVAILABLE = False

__all__ = [
    "load_xml",
    "dump_xml",
    "Element",
    "ensure_unique_id",
    "IdRegistry",
    "deep_copy_element",
    "iter_elements",
    "etree",
    "xpath",
]

try:  # pragma: no cover - optional attribute when lxml is present
    Element = etree._Element  # type: ignore[attr-defined]
except AttributeError:  # pragma: no cover - ElementTree fallback
    Element = etree.Element  # type: ignore[assignment]


def load_xml(data: bytes) -> Element:
    """Return the root XML element from *data*.

    The XML is parsed using :mod:`defusedxml` to guard against common XML parser
    exploits. All whitespace is preserved because Tableau workbooks are
    whitespace sensitive in a few places (notably formula definitions).
    """

    if LXML_AVAILABLE:
        parser = etree.XMLParser(remove_blank_text=False, resolve_entities=False)
        return fromstring(data, parser=parser)
    return fromstring(data)


def dump_xml(root: Element) -> bytes:
    """Serialise *root* into UTF-8 encoded bytes."""

    if LXML_AVAILABLE:
        return etree.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True)  # type: ignore[arg-type]
    return etree.tostring(root, encoding="utf-8")  # type: ignore[arg-type]


def deep_copy_element(element: Element) -> Element:
    """Return a deep copy of *element* preserving all sub-tree data."""

    return fromstring(etree.tostring(element))


@dataclass
class IdRegistry:
    """Track identifiers that appear in the workbook.

    Tableau mixes GUID like identifiers with simple string identifiers. The
    registry keeps a set of all identifiers that have been observed and can
    generate a new identifier based on a preferred prefix.
    """

    known_ids: set[str]

    def __init__(self, elements: Iterable[Element]) -> None:
        self.known_ids = set()
        for element in elements:
            self._register_element(element)

    def _register_element(self, element: Element) -> None:
        id_attr = element.get("id")
        if id_attr:
            self.known_ids.add(id_attr)
        for child in element:
            self._register_element(child)

    def reserve(self, identifier: str) -> None:
        self.known_ids.add(identifier)

    def ensure(self, identifier: str, prefix: str = "z") -> str:
        if identifier in self.known_ids:
            return self.new(prefix)
        self.known_ids.add(identifier)
        return identifier

    def new(self, prefix: str = "z") -> str:
        index = 1
        candidate = f"{prefix}{index}"
        while candidate in self.known_ids:
            index += 1
            candidate = f"{prefix}{index}"
        self.known_ids.add(candidate)
        return candidate


def ensure_unique_id(element: Element, registry: IdRegistry, prefix: str = "z") -> str:
    current = element.get("id")
    if current:
        unique = registry.ensure(current, prefix=prefix)
        element.set("id", unique)
        return unique
    new_value = registry.new(prefix=prefix)
    element.set("id", new_value)
    return new_value


def iter_elements(root: Element, tag: Optional[str] = None) -> Iterator[Element]:
    for element in root.iter(tag):
        yield element


def xpath(element: Element, expression: str):
    if LXML_AVAILABLE:
        return element.xpath(expression)  # type: ignore[attr-defined]
    return element.findall(expression)
