"""Optional helpers for interacting with Tableau Hyper extracts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - optional dependency
    from tableauhyperapi import HyperProcess  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    HyperProcess = None  # type: ignore


@dataclass
class HyperInfo:
    path: Path


def is_available() -> bool:
    return HyperProcess is not None


def describe_hyper(path: Path) -> Optional[HyperInfo]:
    if not path.exists():
        return None
    return HyperInfo(path=path)
