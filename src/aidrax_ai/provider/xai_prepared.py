from __future__ import annotations

from typing import Any

from .errors import ProviderExecutionError, ProviderLifecycleError
from .lifecycle import ProviderHealth
from .provider import Provider


class XAIPreparedProvider(Provider):
    """Fail-closed xAI adapter placeholder."""

    def name(self) -> str:
        return "xAI (prepared/inactive)"

    def capabilities(self) -> tuple[str, ...]:
        return ("ai.chat", "ai.code")

    def initialize(self) -> None:
        raise ProviderLifecycleError("xAI provider is prepared/inactive")

    def health(self) -> ProviderHealth:
        return ProviderHealth.DEGRADED

    def execute(self, capability: str, payload: dict[str, Any]):
        raise ProviderExecutionError("xAI provider is prepared/inactive")

    def owner_gate_required(self, capability: str) -> bool:
        return True

    def metadata(self) -> dict[str, object]:
        return {
            "vendor": "xAI",
            "status": "prepared_inactive",
            "production": False,
            "default": False,
            "fallback": False,
            "base_url": "https://api.x.ai/v1",
            "model": "grok-4.7",
            "context_window": 500_000,
            "activation": "separate_owner_approval_required",
        }


__all__ = ["XAIPreparedProvider"]
