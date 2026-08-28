"""Integration of ARGUS discoveries with ATLAS and HERMES."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from aidrax_core.config import Config
from aidrax_core.errors import PipelineError, RuntimeFailure
from aidrax_core.logging import get_logger
from atlas.registry import Registry, normalize_component
from hermes.bus import EventBus


@dataclass(frozen=True, slots=True)
class _FileSnapshot:
    """Internal byte-level snapshot for rollback of one pipeline report artifact."""

    path: Path
    content: bytes | None

    @classmethod
    def capture(cls, path: Path) -> "_FileSnapshot":
        """Capture a file before the pipeline changes it."""
        try:
            return cls(path=path, content=path.read_bytes() if path.exists() else None)
        except OSError as error:
            raise PipelineError("snapshot", f"cannot snapshot report: {path}", cause=error) from error

    def restore(self) -> None:
        """Restore the captured report or remove a report that was previously absent."""
        try:
            if self.content is None:
                self.path.unlink(missing_ok=True)
                return
            _write_bytes_atomically(self.path, self.content)
        except OSError as error:
            raise PipelineError("rollback", f"cannot restore report: {self.path}", cause=error) from error


def _write_bytes_atomically(path: Path, content: bytes) -> None:
    """Persist one report artifact without exposing a partially written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="wb", dir=path.parent, delete=False) as temporary_file:
        temporary_file.write(content)
        temporary_path = Path(temporary_file.name)
    try:
        os.replace(temporary_path, path)
    except OSError:
        temporary_path.unlink(missing_ok=True)
        raise


def _rollback(
    registry: Registry, previous_registry: Mapping[str, Any] | None, report_snapshot: _FileSnapshot
) -> bool:
    """Restore durable pipeline artifacts and report whether restoration completed."""
    logger = get_logger("integration.pipeline")
    try:
        registry.restore(previous_registry)
        report_snapshot.restore()
    except RuntimeFailure as error:
        logger.error(
            "pipeline_rollback_failed",
            extra={"event": "integration.rollback_failed", "code": error.code.value},
        )
        return False
    logger.info("pipeline_rollback_completed", extra={"event": "integration.rollback_completed"})
    return True


def integrate(
    projects: Sequence[Mapping[str, Any]],
    registry: Registry | None = None,
    event_bus: EventBus | None = None,
    config: Config | None = None,
) -> int:
    """Integrate projects or raise a classified error after recovering durable state."""
    logger = get_logger("integration.pipeline")
    reports_path = Path("reports/events.json")
    canonical_registry: Registry | None = registry
    previous_registry: Mapping[str, Any] | None = None
    report_snapshot: _FileSnapshot | None = None
    phase = "configuration"
    try:
        canonical_registry = registry if registry is not None else Registry()
        configuration = config if config is not None else Config.for_component("integration")
        configuration.load()
        phase = "validation"
        components = [normalize_component(project) for project in projects]
        phase = "snapshot"
        previous_registry = canonical_registry.load() if canonical_registry.path.exists() else None
        report_snapshot = _FileSnapshot.capture(reports_path)
        phase = "registry"
        canonical_registry.save({"components": components})
        events = [
            {"event": "component.discovered", "component": component["id"]}
            for component in components
        ]
        phase = "report"
        _write_bytes_atomically(
            reports_path,
            (json.dumps({"events": events}, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        phase = "publish"
        bus = event_bus if event_bus is not None else EventBus()
        for event in events:
            bus.publish(event["event"], {"component": event["component"]})
    except BaseException as error:
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            raise
        recovered = False
        if report_snapshot is not None and canonical_registry is not None:
            recovered = _rollback(canonical_registry, previous_registry, report_snapshot)
        if phase == "publish":
            recovered = False
        logger.error(
            "pipeline_failed",
            extra={"event": "integration.failed", "phase": phase, "recovered": recovered},
        )
        raise PipelineError(
            phase,
            f"integration failed during {phase}",
            cause=error,
            recovered=recovered,
        ) from error
    logger.info(
        "integration_completed",
        extra={"event": "integration.completed", "component_count": len(components)},
    )
    return len(components)
