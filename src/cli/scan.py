"""Explicit CLI entrypoint for ARGUS project scanning."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from aidrax_core.logging import configure_logging, get_logger
from argus.scanner import scan, write_registry


def main(argv: Sequence[str] | None = None) -> int:
    """Scan an optional root and persist the result through ATLAS."""
    parser = argparse.ArgumentParser(description="Scan AIDRAX OS projects")
    parser.add_argument("--root", help="directory to scan")
    parser.add_argument("--output", default="registry/components.json", help="registry path")
    arguments = parser.parse_args(argv)
    configure_logging()
    projects = scan(arguments.root)
    write_registry(projects, arguments.output)
    get_logger("cli.scan").info(
        "scan_registry_completed",
        extra={"event": "argus.registry_updated", "project_count": len(projects), "output": arguments.output},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
