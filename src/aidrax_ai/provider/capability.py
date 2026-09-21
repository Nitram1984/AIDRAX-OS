from __future__ import annotations

from aidrax_core.capabilities.contracts import CapabilityHealth

from .lifecycle import ProviderHealth, ProviderState
from .runtime import ProviderRuntime


class AIProviderCapability:
    """Canonical Capability adapter for the AIDRAX AI provider runtime."""

    def __init__(self, runtime: ProviderRuntime):
        self.runtime = runtime
        self._active = False

    def initialize(self) -> None:
        self.runtime.initialize_all()

    def activate(self) -> None:
        self._active = True

    def deactivate(self) -> None:
        self._active = False

    def health(self) -> CapabilityHealth:
        statuses = self.runtime.status()
        if not statuses:
            return CapabilityHealth.DEGRADED
        if any(item["state"] == ProviderState.FAILED.value for item in statuses):
            return CapabilityHealth.UNHEALTHY
        if any(item["health"] != ProviderHealth.HEALTHY.value for item in statuses):
            return CapabilityHealth.DEGRADED
        return CapabilityHealth.HEALTHY if self._active else CapabilityHealth.DEGRADED

    def shutdown(self) -> None:
        self._active = False
        self.runtime.shutdown_all()

    def metadata(self) -> dict[str, object]:
        return {
            "component": "aidrax-ai-provider-runtime",
            "provider_count": len(self.runtime.status()),
            "capability_count": len(self.runtime.capabilities()),
        }

    def status(self) -> dict[str, object]:
        return {
            "active": self._active,
            "providers": self.runtime.status(),
        }
