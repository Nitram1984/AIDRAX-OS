"""AIDRAX OS composition boundary for the AI provider runtime."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from aidrax_ai.provider.bootstrap import build_default_provider_runtime
from aidrax_ai.provider.integration import capability_factory
from aidrax_ai.provider.runtime import AuthorizationHook, ProviderRuntime
from aidrax_core.capabilities.discovery import CapabilityDiscovery
from aidrax_core.capabilities.runtime import CapabilityRuntime
from aidrax_core.config import Config
from atlas.registry import Registry
from hermes.bus import EventBus


class AIProviderService:
    """Bind AI providers into the canonical capability lifecycle."""

    def __init__(
        self,
        authorization: AuthorizationHook | None = None,
        *,
        config_directory: str | Path | None = None,
        registry: Registry | None = None,
        event_bus: EventBus | None = None,
        provider_runtime: ProviderRuntime | None = None,
        manifest_path: str | Path | None = None,
    ) -> None:
        root = Path(config_directory) if config_directory is not None else _default_config_directory()
        catalog_path = root / "providers.json"
        resolved_manifest = (
            Path(manifest_path)
            if manifest_path is not None
            else root / "capability-manifests" / "aidrax-ai-provider-runtime.json"
        )
        self.provider_runtime = provider_runtime or build_default_provider_runtime(
            authorization=authorization,
            catalog_path=catalog_path,
            initialize=False,
        )
        self.capability_runtime = CapabilityRuntime(
            registry=registry,
            event_bus=event_bus,
            config=Config.for_component("capabilities", root),
            discovery=CapabilityDiscovery([resolved_manifest]),
            factory=capability_factory(self.provider_runtime),
        )
        self._started = False

    def start(self) -> list[object]:
        """Activate the AI provider capability through CapabilityRuntime."""
        if self._started:
            status = self.capability_runtime.status()
            return status if isinstance(status, list) else [status]
        status = self.capability_runtime.discover_and_activate()
        self._started = True
        return status

    def execute(self, capability: str, payload: dict[str, Any]):
        """Execute a provider capability after the service is ready."""
        if not self._started:
            raise RuntimeError("AI provider service is not started")
        return self.provider_runtime.execute(capability, payload)

    def status(self) -> dict[str, object]:
        """Return non-secret capability and provider status."""
        capability_status = self.capability_runtime.status()
        capabilities = capability_status if isinstance(capability_status, list) else [capability_status]
        return {
            "started": self._started,
            "capabilities": [item.as_dict() for item in capabilities],
            "providers": self.provider_runtime.status(),
        }

    def stop(self) -> list[object]:
        """Shutdown through the canonical capability lifecycle."""
        if not self._started:
            return []
        status = self.capability_runtime.shutdown()
        self._started = False
        return status


def _default_config_directory() -> Path:
    """Resolve the runtime configuration directory for repo and installed OS use."""
    configured = os.environ.get("AIDRAX_CONFIG_DIR")
    if configured:
        return Path(configured)
    system_config = Path("/etc/aidrax-os")
    if system_config.exists():
        return system_config
    return Path(__file__).resolve().parents[3] / "config"
