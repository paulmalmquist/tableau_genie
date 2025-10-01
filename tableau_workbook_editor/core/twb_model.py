"""High level workbook model."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

from . import actions, dashboards, datasources, parameters, validators, versioning, worksheets
from .calc_utils import lint_calculation
from .xml_utils import Element, IdRegistry, dump_xml, etree, load_xml, xpath
from .writer import WorkbookWriter

if TYPE_CHECKING:  # pragma: no cover
    from .reader import WorkbookSource


@dataclass
class DiffResult:
    description: str


class Workbook:
    """Representation of a Tableau workbook with convenience helpers."""

    def __init__(self, *, root: Element, source: "WorkbookSource") -> None:
        self.root = root
        self.source = source
        self._original = dump_xml(root)
        self.id_registry = IdRegistry([root])

    # ------------------------------------------------------------------
    # Creation helpers
    @classmethod
    def open(cls, path: str | Path) -> "Workbook":
        from .reader import open_workbook

        return open_workbook(Path(path))

    # ------------------------------------------------------------------
    # Inspection helpers
    def list_worksheets(self) -> List[str]:
        return worksheets.list_worksheets(self.root)

    def list_dashboards(self) -> List[str]:
        return dashboards.list_dashboards(self.root)

    def list_datasources(self) -> List[str]:
        return datasources.list_datasource_names(self.root)

    def list_parameters(self) -> List[str]:
        return parameters.list_parameters(self.root)

    # ------------------------------------------------------------------
    # Modification helpers
    def rename_field(self, *, datasource: str, old: str, new: str) -> None:
        ds = datasources.find_datasource(self.root, datasource)
        if ds is None:
            raise ValueError(f"Datasource '{datasource}' not found")
        column = datasources.find_column(ds, old)
        if column is None:
            raise ValueError(f"Field '{old}' not found in datasource '{datasource}'")
        old_name = datasources.ensure_column_name(column)
        old_caption = column.get("caption") or old_name.strip("[]")
        new_ref = new if new.startswith("[") else f"[{new}]"
        column.set("name", new_ref)
        column.set("caption", new)
        # Update dependencies in datasource
        for dep in xpath(ds, ".//*[@ref]"):
            if dep.get("ref") == old_name:
                dep.set("ref", new_ref)
        # Update worksheets
        for worksheet_name in self.list_worksheets():
            worksheet = worksheets.find_worksheet(self.root, worksheet_name)
            if worksheet is None:
                continue
            worksheets.update_field_reference(worksheet, old=old_name, new=new_ref)
            for node in xpath(worksheet, ".//*[@formula]"):
                formula = node.get("formula")
                if formula and old_name in formula:
                    node.set("formula", formula.replace(old_name, new_ref))
        # Update actions mapping text
        for action in actions.list_actions(self.root):
            mapping = action.get("mapping")
            if mapping and old_caption in mapping:
                action.set("mapping", mapping.replace(old_caption, new))

    def add_calculation(self, *, datasource: str, name: str, formula: str, data_type: str = "string") -> None:
        lint = lint_calculation(formula)
        if not lint.ok:
            raise ValueError(f"Calculation is invalid: {lint.message}")
        ds = datasources.find_datasource(self.root, datasource)
        if ds is None:
            raise ValueError(f"Datasource '{datasource}' not found")
        column = etree.Element("column")
        ref_name = name if name.startswith("[") else f"[{name}]"
        column.set("name", ref_name)
        column.set("caption", name)
        column.set("datatype", data_type)
        calc = etree.Element("calculation")
        calc.set("class", "tableau")
        calc.set("formula", formula)
        column.append(calc)
        ds.append(column)

    def set_parameter(
        self,
        *,
        name: str,
        data_type: str,
        value: str,
        allowable_values: Optional[List[str]] = None,
        display_format: Optional[str] = None,
    ) -> None:
        parameter = parameters.find_parameter(self.root, name)
        if parameter is None:
            parameter = parameters.create_parameter(self.root, name=name, data_type=data_type, value=value)
        else:
            parameter.set("datatype", data_type)
            parameter.set("current-value", value)
        if allowable_values is not None:
            values_node = parameter.find("values")
            if values_node is None:
                values_node = etree.Element("values")
                parameter.append(values_node)
            values_node.clear()
            for item in allowable_values:
                value_node = etree.Element("value")
                value_node.text = str(item)
                values_node.append(value_node)
        if display_format is not None:
            parameter.set("display-format", display_format)

    def add_sheet_to_dashboard(
        self,
        *,
        dashboard: str,
        sheet: str,
        floating: bool,
        container: str,
        index: int,
    ) -> None:
        worksheet = worksheets.find_worksheet(self.root, sheet)
        if worksheet is None:
            raise ValueError(f"Worksheet '{sheet}' not found")
        dashboard_element = dashboards.find_dashboard(self.root, dashboard)
        if dashboard_element is None:
            raise ValueError(f"Dashboard '{dashboard}' not found")
        dashboards.append_sheet_zone(
            dashboard_element,
            sheet_name=sheet,
            registry=self.id_registry,
            floating=floating,
            container=container,
            index=index,
        )

    def move_zone(
        self,
        *,
        dashboard: str,
        zone_id: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        w: Optional[int] = None,
        h: Optional[int] = None,
    ) -> None:
        dashboard_element = dashboards.find_dashboard(self.root, dashboard)
        if dashboard_element is None:
            raise ValueError(f"Dashboard '{dashboard}' not found")
        for zone in dashboards.list_dashboard_zones(dashboard_element):
            if zone.get("id") == zone_id:
                dashboards.update_zone_geometry(zone, x=x, y=y, w=w, h=h)
                return
        raise ValueError(f"Zone '{zone_id}' not found in dashboard '{dashboard}'")

    def add_filter_action(self, *, source: str, target: str, mapping: Dict[str, str]) -> None:
        actions.create_filter_action(self.root, source=source, target=target, mapping=mapping)

    def set_connection(
        self,
        *,
        datasource: str,
        server: Optional[str] = None,
        db: Optional[str] = None,
        schema: Optional[str] = None,
        table: Optional[str] = None,
    ) -> None:
        ds = datasources.find_datasource(self.root, datasource)
        if ds is None:
            raise ValueError(f"Datasource '{datasource}' not found")
        connection = ds.find("connection")
        if connection is None:
            connection = etree.Element("connection")
            ds.append(connection)
        update: Dict[str, Optional[str]] = {
            "server": server,
            "dbname": db,
            "schema": schema,
            "table": table,
        }
        for key, value in update.items():
            if value is not None:
                connection.set(key, value)

    # ------------------------------------------------------------------
    def validate(self) -> validators.ValidationReport:
        return validators.validate_workbook(self.root)

    def diff(self) -> List[str]:
        before = load_xml(self._original)
        return [] if etree.tostring(before) == etree.tostring(self.root) else ["Workbook modified"]

    # ------------------------------------------------------------------
    def save(
        self,
        *,
        path: Optional[str | Path] = None,
        package_assets: bool = False,
        target_version: Optional[str] = None,
        dry_run: bool = False,
    ) -> Path | None:
        versioning.ensure_target_version(self.root, target_version)
        xml_bytes = dump_xml(self.root)
        if dry_run:
            return None
        writer = WorkbookWriter(self.source)
        target_path = Path(path) if path is not None else None
        return writer.write(target_path, xml_bytes, package_assets=package_assets)

    def save_as(self, path: str | Path, *, package_assets: bool = False, target_version: Optional[str] = None) -> Path | None:
        return self.save(path=path, package_assets=package_assets, target_version=target_version)
