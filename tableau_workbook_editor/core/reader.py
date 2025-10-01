"""Workbook reader helpers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import twbx_utils, xml_utils
from .twb_model import Workbook


@dataclass
class WorkbookSource:
    path: Path
    is_twbx: bool
    packaged: Optional[twbx_utils.PackagedWorkbook]


def open_workbook(path: Path) -> Workbook:
    path = path.expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".twbx":
        package = twbx_utils.extract_twbx(path)
        root = xml_utils.load_xml(package.workbook_xml)
        source = WorkbookSource(path=path, is_twbx=True, packaged=package)
    elif path.suffix.lower() == ".twb":
        data = path.read_bytes()
        root = xml_utils.load_xml(data)
        source = WorkbookSource(path=path, is_twbx=False, packaged=None)
    else:
        raise ValueError("Unsupported workbook extension: expected .twb or .twbx")
    return Workbook(root=root, source=source)
