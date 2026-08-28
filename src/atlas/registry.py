"""Canonical persistence layer for AIDRAX OS component registry data."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from aidrax_core.config import Config
from aidrax_core.errors import RegistryError
from aidrax_core.logging import get_logger


def normalize_component(component: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize the CA-011 scanner shape into the canonical component shape."""
    component_id = component.get("id", component.get("name"))
    path = component.get("path")
    status = component.get("status")
    health = component.get("health")
    capability = component.get("capability")
    if not isinstance(component_id, str) or not component_id.strip():
        raise RegistryError("component requires a non-empty 'id' or legacy 'name'")
    normalized = {"id": component_id}
    if path is not None:
        if not isinstance(path, str) or not path.strip():
            raise RegistryError("component path must be a non-empty string")
        normalized["path"] = path
    if status is not None:
        if not isinstance(status, str) or not status.strip():
            raise RegistryError("component status must be a non-empty string")
        normalized["status"] = status
    elif path is not None:
        normalized["status"] = "DISCOVERED"
    if health is not None:
        if not isinstance(health, str) or not health.strip():
            raise RegistryError("component health must be a non-empty string")
        normalized["health"] = health
    if capability is not None:
        if not isinstance(capability, Mapping):
            raise RegistryError("component capability must be an object")
        normalized["capability"] = dict(capability)
    return normalized


def validate_registry(data: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Validate and normalize a complete component registry document."""
    components = data.get("components")
    if not isinstance(components, Sequence) or isinstance(components, (str, bytes)):
        raise RegistryError("registry requires a 'components' array")
    normalized: list[dict[str, Any]] = []
    component_ids: set[str] = set()
    for component in components:
        if not isinstance(component, Mapping):
            raise RegistryError("each component must be an object")
        normalized_component = normalize_component(component)
        if normalized_component["id"] in component_ids:
            raise RegistryError(f"duplicate component id: {normalized_component['id']}")
        component_ids.add(normalized_component["id"])
        normalized.append(normalized_component)
    return {"components": normalized}


class Registry:
    """Read and atomically write the sole AIDRAX OS component registry."""

    def __init__(self, path: str | Path | None = None, config: Config | None = None) -> None:
        """Create a registry using ATLAS configuration when no path is supplied."""
        if path is None:
            configuration = config if config is not None else Config.for_component("atlas")
            path = configuration.get("registry", "registry/components.json")
        self.path = Path(path)
        self._logger = get_logger("atlas.registry")

    def load(self) -> dict[str, list[dict[str, Any]]]:
        """Load a normalized registry or the empty registry when no file exists."""
        if not self.path.exists():
            return {"components": []}
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except OSError as error:
            self._logger.error("registry_read_failed", extra={"event": "atlas.registry_read_failed", "path": str(self.path)})
            raise RegistryError(f"cannot read registry: {self.path}", cause=error) from error
        except json.JSONDecodeError as error:
            self._logger.error("registry_invalid_json", extra={"event": "atlas.registry_invalid_json", "path": str(self.path)})
            raise RegistryError(f"invalid registry JSON: {self.path}", cause=error) from error
        if not isinstance(value, Mapping):
            raise RegistryError("registry root must be an object")
        return validate_registry(value)

    def save(self, data: Mapping[str, Any]) -> None:
        """Validate and atomically persist a complete registry document."""
        normalized = validate_registry(data)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=self.path.parent, delete=False
        ) as temporary_file:
            temporary_file.write(encoded)
            temporary_path = Path(temporary_file.name)
        try:
            os.replace(temporary_path, self.path)
        except OSError as error:
            temporary_path.unlink(missing_ok=True)
            self._logger.error("registry_write_failed", extra={"event": "atlas.registry_write_failed", "path": str(self.path)})
            raise RegistryError(f"cannot write registry: {self.path}", cause=error) from error
        self._logger.info(
            "registry_saved",
            extra={
                "event": "atlas.registry_saved",
                "path": str(self.path),
                "component_count": len(normalized["components"]),
            },
        )

    def add(self, component: Mapping[str, Any]) -> None:
        """Add one normalized component without permitting duplicate identifiers."""
        data = self.load()
        data["components"].append(normalize_component(component))
        self.save(data)

    def restore(self, data: Mapping[str, Any] | None) -> None:
        """Restore a captured registry state after a failed higher-level transition."""
        if data is None:
            try:
                self.path.unlink(missing_ok=True)
            except OSError as error:
                self._logger.error("registry_rollback_failed", extra={"event": "atlas.registry_rollback_failed", "path": str(self.path)})
                raise RegistryError(f"cannot remove registry during rollback: {self.path}", cause=error) from error
            self._logger.info("registry_rollback_completed", extra={"event": "atlas.registry_rollback_completed", "path": str(self.path)})
            return
        self.save(data)
        self._logger.info("registry_rollback_completed", extra={"event": "atlas.registry_rollback_completed", "path": str(self.path)})
