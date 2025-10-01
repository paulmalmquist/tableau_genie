from __future__ import annotations

from pathlib import Path

from tableau_workbook_editor import open_workbook
from tableau_workbook_editor.core.xml_utils import xpath


FIXTURE = Path(__file__).parent / "fixtures" / "sample_workbook.twb"


def test_set_parameter_updates_values() -> None:
    wb = open_workbook(FIXTURE)
    wb.set_parameter(name="RegionParam", data_type="string", value="Central", allowable_values=["Central", "East"], display_format="string")
    parameter = xpath(wb.root, "./parameters/parameter[@name='RegionParam']")[0]
    assert parameter.get("current-value") == "Central"
    assert parameter.get("display-format") == "string"
    values = [v.text for v in xpath(parameter, "./values/value")]
    assert values == ["Central", "East"]


def test_create_parameter_when_missing() -> None:
    wb = open_workbook(FIXTURE)
    wb.set_parameter(name="Threshold", data_type="integer", value="5")
    param = xpath(wb.root, "./parameters/parameter[@name='Threshold']")
    assert param
