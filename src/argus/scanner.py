"""ARGUS discovery of local project directories."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aidrax_core.config import Config
from aidrax_core.logging import get_logger
from atlas.registry import Registry

_DEFAULT_SCAN_ROOT = Path("/mnt/DATA2/Projects")


@dataclass(frozen=True)
class Project:
    """Compatibility representation for ARGUS project reports."""

    name: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "path": self.path}


class ProjectScanner:
    """Object-oriented compatibility facade over the canonical scan function."""

    def scan(self, root: str | Path | None = None) -> list[Project]:
        return [Project(**project) for project in scan(root)]


def scan(root: str | Path | None = None, config: Config | None = None) -> list[dict[str, str]]:
    """Discover direct project directories using shared ARGUS configuration."""
    if root is None:
        configuration = config if config is not None else Config.for_component("argus")
        root = configuration.get("scan_root", str(_DEFAULT_SCAN_ROOT))
    scan_root = Path(root)
    projects = [
        {"name": project.name, "path": str(project)}
        for project in sorted(scan_root.iterdir())
        if project.is_dir()
    ] if scan_root.exists() else []
    get_logger("argus.scanner").info(
        "scan_completed",
        extra={"event": "argus.scan_completed", "root": str(scan_root), "project_count": len(projects)},
    )
    return projects


def write_registry(
    projects: Sequence[Mapping[str, Any]], out: str | Path = "registry/components.json"
) -> None:
    """Preserve the CA-011 API while delegating persistence to ATLAS."""
    Registry(out).save({"components": list(projects)})
