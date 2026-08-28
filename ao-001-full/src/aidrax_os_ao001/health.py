"""Health output contract for non-secret, deterministic operational evidence."""

from __future__ import annotations

from dataclasses import dataclass

from .runtime import PlatformRuntime, RuntimeState


@dataclass(frozen=True)
class HealthReport:
    state: str
    healthy: bool
    component_count: int

    @classmethod
    def from_runtime(cls, runtime: PlatformRuntime) -> "HealthReport":
        status = runtime.status()
        return cls(
            state=str(status["state"]),
            healthy=runtime.state in {RuntimeState.READY, RuntimeState.RUNNING},
            component_count=len(status["components"]),
        )
