from __future__ import annotations

from pathlib import Path

from tableau_workbook_editor import open_workbook
from tableau_workbook_editor.core.xml_utils import xpath


FIXTURE = Path(__file__).parent / "fixtures" / "sample_workbook.twb"


def test_move_zone_updates_geometry() -> None:
    wb = open_workbook(FIXTURE)
    wb.move_zone(dashboard="Executive", zone_id="z1", x=40, y=80, w=600, h=300)
    zone = xpath(wb.root, "./dashboards/dashboard[@name='Executive']/zones/zone[@id='z1']")[0]
    assert zone.get("x") == "40"
    assert zone.get("y") == "80"
    assert zone.get("w") == "600"
    assert zone.get("h") == "300"


def test_add_sheet_creates_new_zone() -> None:
    wb = open_workbook(FIXTURE)
    wb.add_sheet_to_dashboard(dashboard="Executive", sheet="Detail", floating=True, container="root", index=10)
    zones = xpath(wb.root, "./dashboards/dashboard[@name='Executive']/zones/zone[@worksheet='Detail']")
    assert zones
