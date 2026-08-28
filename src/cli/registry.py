"""Explicit CLI entrypoint for inspecting the ATLAS registry."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from aidrax_core.logging import configure_logging, get_logger
from atlas.registry import Registry


def main(argv: Sequence[str] | None = None) -> int:
    """Log registry metadata without mutating the registry."""
    parser = argparse.ArgumentParser(description="Inspect the AIDRAX OS component registry")
    parser.add_argument("--path", help="registry path")
    arguments = parser.parse_args(argv)
    configure_logging()
    registry = Registry(arguments.path) if arguments.path else Registry()
    components = registry.load()["components"]
    get_logger("cli.registry").info(
        "registry_status", extra={"event": "atlas.registry_status", "component_count": len(components)}
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
