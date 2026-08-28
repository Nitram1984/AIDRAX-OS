"""Explicit CLI entrypoint for integrating selected project directories."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from aidrax_core.logging import configure_logging, get_logger
from integration.pipeline import integrate


def main(argv: Sequence[str] | None = None) -> int:
    """Integrate caller-supplied directories; no synthetic projects are created."""
    parser = argparse.ArgumentParser(description="Integrate AIDRAX OS project directories")
    parser.add_argument("projects", nargs="+", help="project directories")
    arguments = parser.parse_args(argv)
    projects = [{"name": Path(project).name, "path": str(Path(project))} for project in arguments.projects]
    configure_logging()
    count = integrate(projects)
    get_logger("cli.integrate").info(
        "integration_submission_completed",
        extra={"event": "integration.submission_completed", "component_count": count},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
