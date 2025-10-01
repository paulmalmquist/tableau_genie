from __future__ import annotations

import pytest

from tableau_workbook_editor import open_workbook
from tableau_workbook_editor.core.calc_utils import lint_calculation
from tableau_workbook_editor.core.xml_utils import xpath

from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "sample_workbook.twb"


def test_add_calculation_appends_column() -> None:
    wb = open_workbook(FIXTURE)
    wb.add_calculation(datasource="Orders", name="Margin", formula="SUM([Profit]) - SUM([Sales])", data_type="float")
    column = xpath(wb.root, "./datasources/datasource/column[@caption='Margin']")
    assert column


def test_lint_detects_unbalanced_parentheses() -> None:
    result = lint_calculation("SUM([Profit]")
    assert not result.ok
    assert "Unbalanced" in result.message


def test_add_calculation_rejects_invalid_formula() -> None:
    wb = open_workbook(FIXTURE)
    with pytest.raises(ValueError):
        wb.add_calculation(datasource="Orders", name="Broken", formula="SUM([Profit]")
