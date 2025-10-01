"""Validation helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from . import dashboards, worksheets
from .xml_utils import Element


@dataclass
class ValidationIssue:
    message: str


@dataclass
class ValidationReport:
    issues: List[ValidationIssue]

    @property
    def ok(self) -> bool:
        return not self.issues


def validate_workbook(root: Element) -> ValidationReport:
    issues: List[ValidationIssue] = []
    worksheet_names = set(worksheets.list_worksheets(root))
    for dashboard_name in dashboards.list_dashboards(root):
        dashboard = dashboards.find_dashboard(root, dashboard_name)
        if dashboard is None:
            continue
        for zone in dashboards.list_dashboard_zones(dashboard):
            if zone.get("type") == "worksheet":
                sheet = zone.get("worksheet")
                if sheet not in worksheet_names:
                    issues.append(ValidationIssue(f"Dashboard '{dashboard_name}' references missing worksheet '{sheet}'"))
    return ValidationReport(issues=issues)
