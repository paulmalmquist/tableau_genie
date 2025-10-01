from __future__ import annotations

from pathlib import Path

from tableau_workbook_editor import open_workbook
from tableau_workbook_editor.core.xml_utils import xpath


FIXTURE = Path(__file__).parent / "fixtures" / "sample_workbook.twb"


def test_rename_field_updates_references(tmp_path: Path) -> None:
    wb = open_workbook(FIXTURE)
    wb.rename_field(datasource="Orders", old="Region", new="Geography")

    worksheet_refs = xpath(wb.root, ".//worksheet//column[@ref='[Geography]']")
    assert worksheet_refs
    action = xpath(wb.root, "./actions/action[@name='Action1']")[0]
    assert "Geography" in action.get("mapping", "")

    saved = tmp_path / "rename.twb"
    wb.save(path=saved)
    reopened = open_workbook(saved)
    assert xpath(reopened.root, ".//column[@caption='Geography']")


def test_set_connection_updates_connection_node() -> None:
    wb = open_workbook(FIXTURE)
    wb.set_connection(datasource="Orders", server="server", db="warehouse", schema="analytics", table="orders")
    connection = xpath(wb.root, "./datasources/datasource/connection")[0]
    assert connection.get("server") == "server"
    assert connection.get("dbname") == "warehouse"
    assert connection.get("schema") == "analytics"
    assert connection.get("table") == "orders"
