"""Helpers for manipulating Tableau packaged workbooks (.twbx)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional
from zipfile import ZipFile


@dataclass
class PackagedWorkbook:
    """In-memory representation of a Tableau packaged workbook."""

    workbook_xml: bytes
    inner_path: str
    other_files: Dict[str, bytes]


def extract_twbx(path: Path) -> PackagedWorkbook:
    """Extract *path* and return a :class:`PackagedWorkbook` instance."""

    workbook_xml: Optional[bytes] = None
    inner_path = ""
    other_files: Dict[str, bytes] = {}
    with ZipFile(path, "r") as zf:
        for info in zf.infolist():
            data = zf.read(info)
            if info.filename.lower().endswith(".twb"):
                if workbook_xml is not None:
                    raise ValueError("Multiple .twb files found inside the package")
                workbook_xml = data
                inner_path = info.filename
            else:
                other_files[info.filename] = data
    if workbook_xml is None:
        raise ValueError("Packaged workbook does not contain a .twb file")
    return PackagedWorkbook(workbook_xml=workbook_xml, inner_path=inner_path, other_files=other_files)


def pack_twbx(target: Path, package: PackagedWorkbook) -> None:
    """Write *package* back to ``target`` preserving non-workbook files."""

    with ZipFile(target, "w") as zf:
        zf.writestr(package.inner_path, package.workbook_xml)
        for name, data in package.other_files.items():
            zf.writestr(name, data)
