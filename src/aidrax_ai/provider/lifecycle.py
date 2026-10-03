from dataclasses import dataclass
from enum import StrEnum


class ProviderState(StrEnum):
    CREATED = "CREATED"
    REGISTERED = "REGISTERED"
    READY = "READY"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class ProviderHealth(StrEnum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


@dataclass(slots=True)
class ProviderRecord:
    provider_id: str
    provider: object
    state: ProviderState = ProviderState.REGISTERED
    health: ProviderHealth = ProviderHealth.DEGRADED
    last_error: str | None = None
