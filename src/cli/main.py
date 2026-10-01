"""Explicit CLI entrypoint for the AIDRAX OS runtime status."""

from __future__ import annotations

from collections.abc import Sequence

from aidrax_core.logging import configure_logging, get_logger
from aidrax_core.runtime import CoreRuntime


def main(argv: Sequence[str] | None = None) -> int:
    """Log the current runtime status without modifying runtime state."""
    del argv
    configure_logging()
    status = CoreRuntime().status()
    get_logger("cli.main").info("runtime_status", extra={"event": "runtime.status", **status})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
