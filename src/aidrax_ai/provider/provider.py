from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from .lifecycle import ProviderHealth


class Provider(ABC):
    @abstractmethod
    def name(self) -> str:
        """Return a stable human-readable provider name."""

    @abstractmethod
    def capabilities(self) -> tuple[str, ...]:
        """Return the capabilities handled by this provider."""

    @abstractmethod
    def execute(self, capability: str, payload: dict[str, Any]):
        """Execute one declared capability."""

    def initialize(self) -> None:
        """Prepare provider resources without performing user work."""

    def shutdown(self) -> None:
        """Release provider resources."""

    def health(self) -> ProviderHealth:
        return ProviderHealth.HEALTHY

    def metadata(self) -> Mapping[str, object]:
        return {}

    def owner_gate_required(self, capability: str) -> bool:
        """Return True when execution requires an explicit owner approval."""
        return False
