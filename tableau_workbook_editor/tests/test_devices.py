from __future__ import annotations

from pathlib import Path

from tableau_workbook_editor import open_workbook
from tableau_workbook_editor.core import dashboards, devices


FIXTURE = Path(__file__).parent / "fixtures" / "sample_workbook.twb"


def test_list_device_layouts_handles_missing_nodes() -> None:
    wb = open_workbook(FIXTURE)
    dashboard = dashboards.find_dashboard(wb.root, "Executive")
    assert dashboard is not None
    layouts = devices.list_device_layouts(dashboard)
    assert layouts == []
