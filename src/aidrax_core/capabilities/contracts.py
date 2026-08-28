"""Provider-neutral contracts for the AIDRAX capability lifecycle."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Protocol, runtime_checkable


class CapabilityState(StrEnum):
    """Stable states owned exclusively by :class:`CapabilityRuntime`."""

    REGISTERED = "REGISTERED"
    LOADED = "LOADED"
    ACTIVE = "ACTIVE"
    READY = "READY"
    INACTIVE = "INACTIVE"
    FAILED = "FAILED"


class CapabilityHealth(StrEnum):
    """Stable health classifications reported by a capability."""

    UNKNOWN = "UNKNOWN"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


@runtime_checkable
class Capability(Protocol):
    """Canonical provider-neutral lifecycle interface for future capabilities."""

    def initialize(self) -> None:
        """Prepare the capability for later activation."""

    def activate(self) -> None:
        """Make the initialized capability available to the internal runtime."""

    def deactivate(self) -> None:
        """Stop active work while retaining the initialized capability."""

    def health(self) -> CapabilityHealth:
        """Return the current capability health classification."""

    def shutdown(self) -> None:
        """Release capability resources after deactivation."""

    def metadata(self) -> Mapping[str, object]:
        """Return non-secret implementation metadata for internal diagnostics."""

    def status(self) -> Mapping[str, object]:
        """Return non-secret implementation status for internal diagnostics."""
