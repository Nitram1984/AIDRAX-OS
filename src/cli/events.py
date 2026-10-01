"""Explicit CLI entrypoint for publishing a HERMES event."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from typing import Any

from aidrax_core.logging import configure_logging, get_logger
from hermes.bus import EventBus


def main(argv: Sequence[str] | None = None) -> int:
    """Publish one caller-supplied JSON-object event payload."""
    parser = argparse.ArgumentParser(description="Publish one AIDRAX OS event")
    parser.add_argument("event", help="event name")
    parser.add_argument("--payload", default="{}", help="JSON object payload")
    arguments = parser.parse_args(argv)
    try:
        payload: Any = json.loads(arguments.payload)
    except json.JSONDecodeError as error:
        parser.error(f"invalid payload JSON: {error.msg}")
    if not isinstance(payload, Mapping):
        parser.error("payload must be a JSON object")
    configure_logging()
    bus = EventBus()
    bus.publish(arguments.event, payload)
    get_logger("cli.events").info(
        "event_submission_completed",
        extra={"event": arguments.event, "pending": bus.pending()},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
