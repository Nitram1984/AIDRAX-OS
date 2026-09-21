from __future__ import annotations

from collections.abc import Callable
from typing import Any

from aidrax_ai.capability_manager.registry import CapabilityRegistry

from .catalog import ProviderCatalog
from .errors import (
    ProviderAuthorizationError,
    ProviderExecutionError,
    ProviderLifecycleError,
    ProviderRegistrationError,
)
from .factory import ProviderFactory
from .lifecycle import ProviderHealth, ProviderRecord, ProviderState
from .provider import Provider

AuthorizationHook = Callable[[str, str, dict[str, Any]], bool]


class ProviderRuntime:
    def __init__(self, authorization: AuthorizationHook | None = None):
        self.registry = CapabilityRegistry()
        self._records: dict[str, ProviderRecord] = {}
        self._authorization = authorization

    def register(self, provider: Provider, provider_id: str | None = None) -> str:
        pid = self.registry.register(provider, provider_id)
        self._records[pid] = ProviderRecord(provider_id=pid, provider=provider)
        return pid

    def initialize(self, provider_id: str) -> dict[str, object]:
        record = self._require(provider_id)
        if record.state is ProviderState.READY:
            return self.status(provider_id)
        try:
            record.provider.initialize()
            record.health = ProviderHealth(record.provider.health())
            if record.health is ProviderHealth.UNHEALTHY:
                raise ProviderLifecycleError(f"provider is unhealthy after initialization: {provider_id}")
            record.state = ProviderState.READY
            record.last_error = None
            return self.status(provider_id)
        except BaseException as error:
            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise
            record.state = ProviderState.FAILED
            record.last_error = f"{type(error).__name__}: {error}"
            if isinstance(error, ProviderLifecycleError):
                raise
            raise ProviderLifecycleError(f"provider initialization failed: {provider_id}") from error

    def initialize_all(self) -> list[dict[str, object]]:
        return [self.initialize(provider_id) for provider_id in sorted(self._records)]

    def restore(
        self,
        catalog: ProviderCatalog,
        factory: ProviderFactory,
        *,
        initialize: bool = True,
    ) -> list[dict[str, object]]:
        """Rebind configured providers deterministically after restart."""
        if self._records:
            raise ProviderRegistrationError("provider runtime must be empty before restore")
        for binding in catalog.load():
            self.register(factory.create(binding.creator), binding.provider_id)
        if initialize:
            return self.initialize_all()
        return self.status()

    def execute(self, capability: str, payload: dict[str, Any]):
        if not isinstance(payload, dict):
            raise ProviderExecutionError("provider payload must be a dictionary")
        provider = self.registry.resolve(capability)
        if provider is None:
            raise ProviderExecutionError(f"capability not registered: {capability}")
        provider_id = self.registry.provider_id(provider)
        record = self._require(provider_id)
        if record.state is not ProviderState.READY:
            raise ProviderLifecycleError(f"provider is not ready: {provider_id}")
        if provider.owner_gate_required(capability):
            if self._authorization is None or not self._authorization(provider_id, capability, payload):
                raise ProviderAuthorizationError(
                    f"owner approval required for provider action: {provider_id}/{capability}"
                )
        try:
            return provider.execute(capability, payload)
        except BaseException as error:
            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise
            record.last_error = f"{type(error).__name__}: {error}"
            raise ProviderExecutionError(f"provider execution failed: {provider_id}/{capability}") from error

    def shutdown(self, provider_id: str) -> dict[str, object]:
        record = self._require(provider_id)
        try:
            record.provider.shutdown()
            record.state = ProviderState.STOPPED
            record.health = ProviderHealth.DEGRADED
            return self.status(provider_id)
        except BaseException as error:
            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise
            record.state = ProviderState.FAILED
            record.last_error = f"{type(error).__name__}: {error}"
            raise ProviderLifecycleError(f"provider shutdown failed: {provider_id}") from error

    def shutdown_all(self) -> list[dict[str, object]]:
        return [self.shutdown(provider_id) for provider_id in reversed(sorted(self._records))]

    def status(self, provider_id: str | None = None):
        if provider_id is not None:
            record = self._require(provider_id)
            return self._status(record)
        return [self._status(self._records[key]) for key in sorted(self._records)]

    def capabilities(self) -> tuple[str, ...]:
        return self.registry.capabilities()

    def _require(self, provider_id: str) -> ProviderRecord:
        try:
            return self._records[provider_id]
        except KeyError as error:
            raise ProviderRegistrationError(f"provider not registered: {provider_id}") from error

    @staticmethod
    def _status(record: ProviderRecord) -> dict[str, object]:
        provider = record.provider
        return {
            "id": record.provider_id,
            "name": provider.name(),
            "state": record.state.value,
            "health": record.health.value,
            "capabilities": list(provider.capabilities()),
            "owner_gated": [c for c in provider.capabilities() if provider.owner_gate_required(c)],
            "metadata": dict(provider.metadata()),
            "last_error": record.last_error,
        }
