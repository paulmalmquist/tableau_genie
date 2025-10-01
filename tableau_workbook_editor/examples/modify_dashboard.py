"""Example script showing how to edit a workbook."""
from __future__ import annotations

from pathlib import Path

from tableau_workbook_editor import open_workbook


def main(path: str) -> None:
    workbook = open_workbook(Path(path))
    workbook.rename_field(datasource="Orders", old="Profit", new="Net Profit")
    workbook.add_calculation(
        datasource="Orders",
        name="Profit Ratio",
        formula="SUM([Profit])/SUM([Sales])",
        data_type="float",
    )
    workbook.save()


if __name__ == "__main__":  # pragma: no cover
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python modify_dashboard.py <workbook>")
    main(sys.argv[1])
