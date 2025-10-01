# Tableau Workbook Editor

`tableau_workbook_editor` is a Python package that can open, inspect and modify Tableau workbooks (`.twb`) or packaged workbooks (`.twbx`).  It focuses on safe round-tripping – any nodes that are not touched are preserved exactly as Tableau generated them.

## Features

- Parse `.twb` XML and `.twbx` zip archives with automatic detection.
- Rich in-memory API for listing worksheets, dashboards, datasources and parameters.
- Convenience helpers for common authoring tasks such as renaming fields, adding calculated fields, updating parameters and editing dashboard layouts.
- Optional CLI (`tbe`) powered by `click` and `rich` for quick inspection and edits from the terminal.
- Lightweight validation, diffing and device layout helpers.

## Installing

The project uses a standard `pyproject.toml`. Install the package in editable mode during development:

```bash
pip install -e .
```

## CLI Usage

```
tbe inspect workbook.twbx

# rename a field
tbe rename-field workbook.twb --datasource Orders --from Profit --to "Net Profit"

# add a calculation
tbe add-calc workbook.twb --datasource Orders --name "Profit Ratio" --formula "SUM([Profit])/SUM([Sales])" --type float

# update a parameter
tbe set-parameter workbook.twb --name RegionParam --type string --value West --allow East --allow West

# add a sheet to a dashboard
tbe add-sheet-to-dashboard workbook.twb --dashboard Executive --sheet "Detail" --floating false --container root --index 1
```

Each mutating command accepts `--dry-run`, `--backup` and `--as` options. Use `--dry-run` to preview changes without writing files and `--backup` to create a `*.bak` copy of the original workbook before saving.

## Python API

```python
from tableau_workbook_editor import open_workbook

wb = open_workbook("Sales.twbx")
wb.rename_field(datasource="Orders", old="Profit", new="Net Profit")
wb.add_calculation(
    datasource="Orders",
    name="Profit Ratio",
    formula="SUM([Profit])/SUM([Sales])",
    data_type="float",
)
wb.save_as("Sales_Modified.twbx", package_assets=True)
```

## Running Tests

```bash
pytest
```

The test suite uses synthetic `.twb` fixtures to ensure round-tripping behaviour and exercises all public helpers.
