from __future__ import annotations

from pathlib import Path

from tableau_workbook_editor import open_workbook
from tableau_workbook_editor.core.xml_utils import xpath


FIXTURE = Path(__file__).parent / "fixtures" / "sample_workbook.twb"


def test_add_filter_action_appends_action() -> None:
    wb = open_workbook(FIXTURE)
    wb.add_filter_action(source="Executive", target="Detail", mapping={"Region": "Region", "Category": "Category"})
    actions = xpath(wb.root, "./actions/action")
    assert len(actions) == 2
    new_action = actions[-1]
    assert new_action.get("mapping") == "Region=Region; Category=Category"
