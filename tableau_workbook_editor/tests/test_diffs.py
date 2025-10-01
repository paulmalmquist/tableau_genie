from __future__ import annotations

from pathlib import Path

from tableau_workbook_editor import open_workbook


FIXTURE = Path(__file__).parent / "fixtures" / "sample_workbook.twb"


def test_diff_reports_modifications() -> None:
    wb = open_workbook(FIXTURE)
    assert wb.diff() == []
    wb.rename_field(datasource="Orders", old="Profit", new="Net Profit")
    diff = wb.diff()
    assert diff == ["Workbook modified"]
