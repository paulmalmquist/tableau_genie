"""Helpers for writing Tableau workbooks."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from . import twbx_utils, xml_utils

if TYPE_CHECKING:  # pragma: no cover
    from .reader import WorkbookSource


class WorkbookWriter:
    """Persist a workbook to disk with atomic semantics."""

    def __init__(self, source: "WorkbookSource") -> None:
        self.source = source

    def write(self, target: Optional[Path], xml_bytes: bytes, package_assets: bool) -> Path:
        target_path = (target or self.source.path).expanduser().resolve()
        if package_assets or self.source.is_twbx or (target and target.suffix.lower() == ".twbx"):
            return self._write_twbx(target_path, xml_bytes)
        return self._write_twb(target_path, xml_bytes)

    def _write_twb(self, target: Path, xml_bytes: bytes) -> Path:
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=str(target.parent)) as tmp:
            tmp.write(xml_bytes)
            temp_path = Path(tmp.name)
        temp_path.replace(target)
        return target

    def _write_twbx(self, target: Path, xml_bytes: bytes) -> Path:
        if self.source.packaged is None:
            package = twbx_utils.PackagedWorkbook(workbook_xml=xml_bytes, inner_path=f"{target.stem}.twb", other_files={})
        else:
            package = self.source.packaged
            package = twbx_utils.PackagedWorkbook(workbook_xml=xml_bytes, inner_path=package.inner_path, other_files=package.other_files)
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=str(target.parent)) as tmp:
            temp_path = Path(tmp.name)
        twbx_utils.pack_twbx(temp_path, package)
        temp_path.replace(target)
        return target
