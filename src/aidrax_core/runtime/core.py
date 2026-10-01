"""Small, deterministic runtime registry used by the Closed Alpha core."""

from __future__ import annotations

from typing import Any

from aidrax_core.config import Config
from aidrax_core.errors import RuntimeValidationError


class CoreRuntime:
    """Own in-process module registration; it has no import-time side effects."""

    def __init__(self, config: Config | None = None) -> None:
        self._config = config if config is not None else Config()
        self.settings = self._config.load()
        self.modules: dict[str, Any] = {}
        self.running = False

    def register(self, name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise RuntimeValidationError("module name must be a non-empty string")
        if name in self.modules:
            raise RuntimeValidationError(f"module '{name}' already registered")
        self.modules[name] = None

    def unregister(self, name: str) -> None:
        self.modules.pop(name, None)

    def start(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False

    def status(self) -> dict[str, object]:
        return {"count": len(self.modules), "modules": list(self.modules)}


Runtime = CoreRuntime
