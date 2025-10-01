from __future__ import annotations

from pathlib import Path

from tableau_workbook_editor import open_workbook
from tableau_workbook_editor.core.xml_utils import xpath


FIXTURE = Path(__file__).parent / "fixtures" / "sample_workbook.twb"


def test_roundtrip(tmp_path: Path) -> None:
    wb = open_workbook(FIXTURE)
    wb.rename_field(datasource="Orders", old="Profit", new="Net Profit")
    wb.add_calculation(datasource="Orders", name="Profit Ratio", formula="SUM([Profit])/SUM([Sales])", data_type="float")
    wb.set_parameter(
        name="RegionParam",
        data_type="string",
        value="West",
        allowable_values=["East", "West", "Central"],
    )
    wb.add_sheet_to_dashboard(dashboard="Executive", sheet="Detail", floating=False, container="root", index=1)
    wb.add_filter_action(source="Executive", target="Detail", mapping={"Region": "Region"})
    wb.set_connection(datasource="Orders", server="analytics.example.com", db="sales", schema="public", table="orders")

    output = tmp_path / "modified.twb"
    wb.save(path=output)

    reopened = open_workbook(output)
    columns = xpath(reopened.root, "./datasources/datasource/column[@caption='Net Profit']")
    assert columns
    parameter = xpath(reopened.root, "./parameters/parameter[@name='RegionParam']")[0]
    values = [v.text for v in xpath(parameter, "./values/value")]
    assert values == ["East", "West", "Central"]
    action = xpath(reopened.root, "./actions/action[@type='filter']")
    assert len(action) == 2
