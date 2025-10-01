"""Command line interface for :mod:`tableau_workbook_editor`."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from .core.reader import open_workbook

console = Console()


def _load_workbook(path: Path):
    return open_workbook(path)


def _save_workbook(workbook, *, target: Optional[Path], dry_run: bool, package_assets: bool) -> None:
    workbook.save(path=target, dry_run=dry_run, package_assets=package_assets)
    if dry_run:
        console.print("[yellow]Dry run complete - no files written[/yellow]")
    else:
        console.print(f"[green]Saved workbook to {target or workbook.source.path}[/green]")


def _maybe_backup(workbook, enabled: bool) -> None:
    if not enabled:
        return
    source = workbook.source.path
    backup_path = source.with_suffix(source.suffix + ".bak")
    backup_path.write_bytes(source.read_bytes())
    console.print(f"[cyan]Backup written to {backup_path}[/cyan]")


def mutation_options(func):
    func = click.option("--backup", is_flag=True, default=False)(func)
    func = click.option("--package-assets", is_flag=True, default=False, help="Write the result as a packaged workbook")(
        func
    )
    func = click.option("--dry-run", is_flag=True, default=False)(func)
    func = click.option("--as", "target_path", type=click.Path(path_type=Path))(func)
    func = click.argument("workbook", type=click.Path(path_type=Path, exists=True))(func)
    return func


@click.group()
@click.version_option()
def main() -> None:
    """Tableau workbook editing tools."""


@main.command()
@click.argument("workbook", type=click.Path(path_type=Path, exists=True))
def inspect(workbook: Path) -> None:
    """Print a summary of the workbook."""

    wb = _load_workbook(workbook)
    tree = Tree(f"Workbook: {workbook.name}")
    sheets = tree.add("Worksheets")
    for sheet in wb.list_worksheets():
        sheets.add(sheet)
    dashboards_branch = tree.add("Dashboards")
    for dash in wb.list_dashboards():
        dashboards_branch.add(dash)
    datasources_branch = tree.add("Datasources")
    for ds in wb.list_datasources():
        datasources_branch.add(ds)
    params_branch = tree.add("Parameters")
    for param in wb.list_parameters():
        params_branch.add(param)
    console.print(tree)


@main.command()
@click.argument("workbook", type=click.Path(path_type=Path, exists=True))
@click.option("--out", "out_path", type=click.Path(path_type=Path))
def export_json(workbook: Path, out_path: Optional[Path]) -> None:
    """Export workbook metadata as JSON."""

    import json

    wb = _load_workbook(workbook)
    data = {
        "worksheets": wb.list_worksheets(),
        "dashboards": wb.list_dashboards(),
        "datasources": wb.list_datasources(),
        "parameters": wb.list_parameters(),
    }
    payload = json.dumps(data, indent=2)
    if out_path is None:
        console.print(payload)
    else:
        out_path.write_text(payload)
        console.print(f"[green]Metadata exported to {out_path}")


@main.command()
@click.argument("workbook", type=click.Path(path_type=Path, exists=True))
@click.option("--sheets", "list_sheets", is_flag=True, help="List worksheets")
@click.option("--dashboards", "list_dashboards_flag", is_flag=True, help="List dashboards")
@click.option("--datasources", "list_datasources_flag", is_flag=True, help="List datasources")
@click.option("--parameters", "list_parameters_flag", is_flag=True, help="List parameters")
def list(workbook: Path, list_sheets: bool, list_dashboards_flag: bool, list_datasources_flag: bool, list_parameters_flag: bool) -> None:
    """List workbook components."""

    wb = _load_workbook(workbook)
    table = Table("Type", "Name")
    if list_sheets:
        for name in wb.list_worksheets():
            table.add_row("worksheet", name)
    if list_dashboards_flag:
        for name in wb.list_dashboards():
            table.add_row("dashboard", name)
    if list_datasources_flag:
        for name in wb.list_datasources():
            table.add_row("datasource", name)
    if list_parameters_flag:
        for name in wb.list_parameters():
            table.add_row("parameter", name)
    console.print(table)


@main.command("rename-field")
@mutation_options
@click.option("--datasource", required=True)
@click.option("--from", "from_name", required=True)
@click.option("--to", required=True)
def rename_field_cmd(workbook: Path, target_path: Optional[Path], dry_run: bool, package_assets: bool, backup: bool, datasource: str, from_name: str, to: str) -> None:
    wb = _load_workbook(workbook)
    _maybe_backup(wb, backup)
    wb.rename_field(datasource=datasource, old=from_name, new=to)
    _save_workbook(wb, target=target_path, dry_run=dry_run, package_assets=package_assets)


@main.command("add-calc")
@mutation_options
@click.option("--datasource", required=True)
@click.option("--name", required=True)
@click.option("--formula", required=True)
@click.option("--type", "data_type", default="string")
def add_calc_cmd(workbook: Path, target_path: Optional[Path], dry_run: bool, package_assets: bool, backup: bool, datasource: str, name: str, formula: str, data_type: str) -> None:
    wb = _load_workbook(workbook)
    _maybe_backup(wb, backup)
    wb.add_calculation(datasource=datasource, name=name, formula=formula, data_type=data_type)
    _save_workbook(wb, target=target_path, dry_run=dry_run, package_assets=package_assets)


@main.command("set-parameter")
@mutation_options
@click.option("--name", required=True)
@click.option("--type", "data_type", required=True)
@click.option("--value", required=True)
@click.option("--allow", "allowable_values", multiple=True)
@click.option("--display-format")
def set_parameter_cmd(workbook: Path, target_path: Optional[Path], dry_run: bool, package_assets: bool, backup: bool, name: str, data_type: str, value: str, allowable_values: tuple[str, ...], display_format: Optional[str]) -> None:
    wb = _load_workbook(workbook)
    _maybe_backup(wb, backup)
    wb.set_parameter(name=name, data_type=data_type, value=value, allowable_values=list(allowable_values) or None, display_format=display_format)
    _save_workbook(wb, target=target_path, dry_run=dry_run, package_assets=package_assets)


@main.command("add-sheet-to-dashboard")
@mutation_options
@click.option("--dashboard", required=True)
@click.option("--sheet", required=True)
@click.option("--floating", type=bool, default=False)
@click.option("--container", default="")
@click.option("--index", type=int, default=-1)
def add_sheet_to_dashboard_cmd(workbook: Path, target_path: Optional[Path], dry_run: bool, package_assets: bool, backup: bool, dashboard: str, sheet: str, floating: bool, container: str, index: int) -> None:
    wb = _load_workbook(workbook)
    _maybe_backup(wb, backup)
    wb.add_sheet_to_dashboard(dashboard=dashboard, sheet=sheet, floating=floating, container=container, index=index)
    _save_workbook(wb, target=target_path, dry_run=dry_run, package_assets=package_assets)


@main.command("move-zone")
@mutation_options
@click.option("--dashboard", required=True)
@click.option("--zone-id", required=True)
@click.option("--x", type=int)
@click.option("--y", type=int)
@click.option("--w", type=int)
@click.option("--h", type=int)
def move_zone_cmd(workbook: Path, target_path: Optional[Path], dry_run: bool, package_assets: bool, backup: bool, dashboard: str, zone_id: str, x: Optional[int], y: Optional[int], w: Optional[int], h: Optional[int]) -> None:
    wb = _load_workbook(workbook)
    _maybe_backup(wb, backup)
    wb.move_zone(dashboard=dashboard, zone_id=zone_id, x=x, y=y, w=w, h=h)
    _save_workbook(wb, target=target_path, dry_run=dry_run, package_assets=package_assets)


@main.command("add-filter-action")
@mutation_options
@click.option("--source", required=True)
@click.option("--target", "target_sheet", required=True)
@click.option("--mapping", required=False, default="")
def add_filter_action_cmd(workbook: Path, target_path: Optional[Path], dry_run: bool, package_assets: bool, backup: bool, source: str, target_sheet: str, mapping: str) -> None:
    wb = _load_workbook(workbook)
    _maybe_backup(wb, backup)
    mapping_dict: Dict[str, str] = {}
    if mapping:
        for pair in mapping.split(";"):
            if not pair:
                continue
            left, _, right = pair.partition("=")
            mapping_dict[left.strip()] = right.strip()
    wb.add_filter_action(source=source, target=target_sheet, mapping=mapping_dict)
    _save_workbook(wb, target=target_path, dry_run=dry_run, package_assets=package_assets)


@main.command("set-connection")
@mutation_options
@click.option("--datasource", required=True)
@click.option("--server")
@click.option("--db")
@click.option("--schema")
@click.option("--table")
def set_connection_cmd(workbook: Path, target_path: Optional[Path], dry_run: bool, package_assets: bool, backup: bool, datasource: str, server: Optional[str], db: Optional[str], schema: Optional[str], table: Optional[str]) -> None:
    wb = _load_workbook(workbook)
    _maybe_backup(wb, backup)
    wb.set_connection(datasource=datasource, server=server, db=db, schema=schema, table=table)
    _save_workbook(wb, target=target_path, dry_run=dry_run, package_assets=package_assets)


@main.command("save")
@mutation_options
def save_cmd(workbook: Path, target_path: Optional[Path], dry_run: bool, package_assets: bool, backup: bool) -> None:
    wb = _load_workbook(workbook)
    _maybe_backup(wb, backup)
    _save_workbook(wb, target=target_path, dry_run=dry_run, package_assets=package_assets)


if __name__ == "__main__":  # pragma: no cover
    main()
