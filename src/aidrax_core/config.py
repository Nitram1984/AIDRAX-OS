"""Deterministic JSON configuration access for AIDRAX OS components."""
from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .errors import ConfigurationError

_DEFAULTS: dict[str, dict[str, Any]] = {
    "settings.json": {},
    "argus.json": {"scan_root": "/mnt/DATA2/Projects"},
    "atlas.json": {"registry": "registry/components.json"},
    "capabilities.json": {"granted_permissions": [], "discovery_directories": []},
    "hermes.json": {"queue": "memory", "capacity": 256, "overflow_policy": "reject", "subscriber_failure_policy": "continue", "subscriber_timeout_seconds": None},
    "integration.json": {"mode": "closed-alpha"},
}


class Config:
    """Read one JSON-object configuration without import-time I/O."""
    def __init__(self, path: str | Path | None = None) -> None:
        """Create an explicit config or resolve the default settings source."""
        self.path = self._resolve_default_path("settings.json") if path is None else Path(path)
        self._resource_name = "settings.json" if path is None and self.path is None else None

    @classmethod
    def for_component(cls, component: str, config_directory: str | Path | None = None) -> "Config":
        """Return the conventional configuration reference for one component."""
        if not component or not component.replace("_", "").replace("-", "").isalnum():
            raise ConfigurationError("component name must contain letters, digits, '-' or '_'")
        filename = f"{component}.json"
        if config_directory is not None:
            return cls(Path(config_directory) / filename)
        instance = cls.__new__(cls)
        instance.path = cls._resolve_default_path(filename)
        instance._resource_name = filename if instance.path is None else None
        return instance

    @staticmethod
    def _resolve_default_path(filename: str) -> Path | None:
        """Resolve environment configuration before checked-out defaults."""
        configured_directory = os.environ.get("AIDRAX_CONFIG_DIR")
        if configured_directory:
            return Path(configured_directory) / filename
        checkout_directory = Path(__file__).resolve().parents[2] / "config"
        return checkout_directory / filename if (checkout_directory.parent / "pyproject.toml").is_file() else None

    def load(self) -> dict[str, Any]:
        """Load a JSON object, or an empty object for an absent explicit file."""
        if self.path is None:
            return dict(_DEFAULTS.get(self._resource_name or "", {}))
        if not self.path.exists():
            return {}
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except OSError as error:
            raise ConfigurationError(f"cannot read configuration: {self.path}", cause=error) from error
        except json.JSONDecodeError as error:
            raise ConfigurationError(f"invalid JSON configuration: {self.path}", cause=error) from error
        if not isinstance(value, dict):
            raise ConfigurationError(f"configuration must be a JSON object: {self.path}")
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """Return one configured value or the explicit fallback."""
        return self.load().get(key, default)

    def require_mapping(self, key: str) -> Mapping[str, Any]:
        """Return a required object-valued entry."""
        value = self.load().get(key)
        if not isinstance(value, Mapping):
            raise ConfigurationError(f"configuration entry '{key}' must be an object")
        return value


__all__ = ["Config", "ConfigurationError"]
