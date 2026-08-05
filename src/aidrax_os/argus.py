from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

PROJECT_MARKERS = (
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "docker-compose.yml",
    "compose.yml",
    "CMakeLists.txt",
)

IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
}


@dataclass(frozen=True)
class ProjectRecord:
    name: str
    path: str
    markers: tuple[str, ...]
    modified_at: str


def _utc_timestamp(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()


def _project_record(path: Path, markers: Iterable[str]) -> ProjectRecord:
    stat = path.stat()
    return ProjectRecord(
        name=path.name,
        path=str(path.resolve()),
        markers=tuple(sorted(markers)),
        modified_at=_utc_timestamp(stat.st_mtime),
    )


def discover_projects(root: Path) -> list[ProjectRecord]:
    root = root.expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Project root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Project root is not a directory: {root}")

    discovered: list[ProjectRecord] = []

    for current_root, directory_names, file_names in os.walk(root):
        directory_names[:] = [
            name for name in directory_names if name not in IGNORED_DIRECTORIES
        ]
        current = Path(current_root)
        markers = PROJECT_MARKERS_INTERSECTION(file_names)
        if markers:
            discovered.append(_project_record(current, markers))
            directory_names[:] = []

    return sorted(discovered, key=lambda record: record.path.casefold())


def PROJECT_MARKERS_INTERSECTION(file_names: Iterable[str]) -> tuple[str, ...]:
    available = set(file_names)
    return tuple(marker for marker in PROJECT_MARKERS if marker in available)


def build_registry(root: Path) -> dict[str, object]:
    projects = discover_projects(root)
    return {
        "schema": "aidrax.ca011r1.argus.registry.v1",
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "root": str(root.expanduser().resolve()),
        "project_count": len(projects),
        "projects": [asdict(project) for project in projects],
    }


def write_registry(registry: dict[str, object], output: Path) -> None:
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="aidrax-argus",
        description="Scan the AIDRAX project root and generate a deterministic registry.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("/mnt/DATA2/Projects"),
        help="Project root to scan.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("runtime/argus-project-registry.json"),
        help="Registry JSON output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = build_registry(args.root)
    write_registry(registry, args.output)
    print(
        json.dumps(
            {
                "status": "GREEN",
                "projects": registry["project_count"],
                "registry": str(args.output.expanduser().resolve()),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
