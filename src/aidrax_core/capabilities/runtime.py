"""Canonical provider-neutral lifecycle owner for AIDRAX capabilities."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from aidrax_core.capabilities.contracts import Capability, CapabilityHealth, CapabilityState
from aidrax_core.capabilities.dependencies import DependencyResolver
from aidrax_core.capabilities.discovery import CapabilityDiscovery
from aidrax_core.capabilities.factory import CapabilityFactory
from aidrax_core.capabilities.manifest import CapabilityManifest, CapabilityStatus
from aidrax_core.config import Config
from aidrax_core.errors import (
    CapabilityDependencyError,
    CapabilityFactoryError,
    CapabilityLifecycleError,
    CapabilityPermissionError,
    CapabilityRegistrationError,
)
from aidrax_core.logging import get_logger
from atlas.registry import Registry
from hermes.bus import EventBus


@dataclass(slots=True)
class _ManagedCapability:
    """Private in-memory binding between a manifest and an injected implementation."""

    manifest: CapabilityManifest
    capability: Capability
    state: CapabilityState
    health: CapabilityHealth


class CapabilityRuntime:
    """Own registration, discovery activation, persistence, and observation for capabilities."""

    def __init__(
        self,
        registry: Registry | None = None,
        event_bus: EventBus | None = None,
        config: Config | None = None,
        discovery: CapabilityDiscovery | None = None,
        factory: CapabilityFactory | None = None,
    ) -> None:
        """Create a runtime using explicit existing infrastructure adapters only."""
        self._registry = registry if registry is not None else Registry()
        self._event_bus = event_bus if event_bus is not None else EventBus()
        self._config = config if config is not None else Config.for_component("capabilities")
        self._discovery = discovery
        self._factory = factory
        self._managed: dict[str, _ManagedCapability] = {}
        self._resolver = DependencyResolver()
        self._logger = get_logger("capabilities.runtime")

    def register(self, manifest: CapabilityManifest | Mapping[str, Any], capability: Capability) -> CapabilityStatus:
        """Register an injected capability through the sole supported lifecycle boundary."""
        normalized = manifest if isinstance(manifest, CapabilityManifest) else CapabilityManifest.from_mapping(manifest)
        if not isinstance(capability, Capability):
            raise CapabilityRegistrationError("capability must implement the canonical Capability interface")
        self._validate_diagnostics(capability)
        if normalized.capability_id in self._managed or self._registry_contains(normalized.capability_id):
            raise CapabilityRegistrationError(f"capability id is already registered: {normalized.capability_id}")
        managed = _ManagedCapability(
            manifest=normalized,
            capability=capability,
            state=CapabilityState.REGISTERED,
            health=normalized.health,
        )
        self._managed[normalized.capability_id] = managed
        try:
            self._persist(managed)
            status = self._status(managed)
            self._emit("capability.registered", status)
            return status
        except BaseException as error:
            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise
            self._managed.pop(normalized.capability_id, None)
            self._restore_registration(normalized.capability_id)
            raise

    def discover(self) -> list[CapabilityStatus]:
        """Return ATLAS capability records in deterministic identity order."""
        discovered = []
        for component in self._registry.load()["components"]:
            capability_record = component.get("capability")
            if not isinstance(capability_record, Mapping):
                continue
            manifest = CapabilityManifest.from_mapping(capability_record)
            state = _state(component.get("status", CapabilityState.REGISTERED.value))
            health = _health(component.get("health", manifest.health.value))
            discovered.append(CapabilityStatus.create(manifest, state, health))
        return sorted(discovered, key=lambda status: status.capability_id)

    def discover_and_activate(self) -> list[CapabilityStatus]:
        """Discover, validate, register, activate, health-check, and mark a batch READY."""
        discovery = self._discovery if self._discovery is not None else CapabilityDiscovery.from_config(self._config)
        if self._factory is None:
            raise CapabilityFactoryError("capability activation requires an explicit provider-neutral factory")
        manifests = discovery.discover()
        ordered = self._resolver.resolve(manifests)
        self._validate_batch_registration(ordered)
        previous_registry = self._registry.load() if self._registry.path.exists() else None
        registered: list[str] = []
        try:
            for manifest in ordered:
                self.register(manifest, self._factory.create(manifest))
                registered.append(manifest.capability_id)
            ready = []
            for manifest in ordered:
                self.activate(manifest.capability_id)
                status = self.health(manifest.capability_id)
                ready.append(self._mark_ready(manifest.capability_id, status))
            return ready
        except BaseException as error:
            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise
            self._rollback_activation(registered, previous_registry, error)
            raise

    def load(self, capability_id: str) -> CapabilityStatus:
        """Initialize a capability and all required dependencies in stable order."""
        self._load_resolved(self._resolved_manifests(capability_id))
        return self._status(self._require_managed(capability_id))

    def activate(self, capability_id: str) -> CapabilityStatus:
        """Activate a loaded capability after dependencies and permissions are satisfied."""
        resolved = self._resolved_manifests(capability_id)
        self._load_resolved(resolved)
        for manifest in resolved:
            managed = self._require_managed(manifest.capability_id)
            self._validate_permissions(managed.manifest)
            if managed.state in {CapabilityState.ACTIVE, CapabilityState.READY}:
                continue
            self._transition(managed, CapabilityState.ACTIVE, managed.capability.activate, "activated")
        return self._status(self._require_managed(capability_id))

    def deactivate(self, capability_id: str) -> CapabilityStatus:
        """Deactivate an active or ready capability after dependents are stopped."""
        managed = self._require_managed(capability_id)
        active_dependents = sorted(
            item.manifest.capability_id
            for item in self._managed.values()
            if item.state in {CapabilityState.ACTIVE, CapabilityState.READY}
            and any(dependency.capability_id == capability_id for dependency in item.manifest.dependencies)
        )
        if active_dependents:
            raise CapabilityLifecycleError(
                f"cannot deactivate {capability_id}; active dependents: {', '.join(active_dependents)}"
            )
        if managed.state not in {CapabilityState.ACTIVE, CapabilityState.READY}:
            return self._status(managed)
        self._transition(managed, CapabilityState.INACTIVE, managed.capability.deactivate, "deactivated")
        return self._status(managed)

    def health(self, capability_id: str) -> CapabilityStatus:
        """Refresh health through the injected capability without provider-specific probes."""
        managed = self._require_managed(capability_id)
        try:
            managed.health = _health(managed.capability.health())
            self._persist(managed)
            status = self._status(managed)
            self._emit("capability.health_changed", status)
            return status
        except BaseException as error:
            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise
            self._fail(managed, "health", error)
            raise CapabilityLifecycleError(f"capability health failed: {capability_id}", cause=error) from error

    def status(self, capability_id: str | None = None) -> CapabilityStatus | list[CapabilityStatus]:
        """Return one status or all managed statuses sorted by capability identity."""
        if capability_id is not None:
            return self._status(self._require_managed(capability_id))
        return [self._status(self._managed[key]) for key in sorted(self._managed)]

    def shutdown(self) -> list[CapabilityStatus]:
        """Deactivate and release managed capabilities in reverse dependency order."""
        outcomes = []
        for capability_id in reversed(self._topological_order()):
            managed = self._managed[capability_id]
            try:
                if managed.state in {CapabilityState.ACTIVE, CapabilityState.READY}:
                    self.deactivate(capability_id)
                self._transition(managed, CapabilityState.INACTIVE, managed.capability.shutdown, "shutdown_completed")
            except CapabilityLifecycleError:
                outcomes.append(self._status(managed))
                continue
            outcomes.append(self._status(managed))
        return outcomes

    def _load_resolved(self, manifests: list[CapabilityManifest]) -> None:
        """Initialize every manifest in an already validated dependency-first order."""
        for manifest in manifests:
            managed = self._require_managed(manifest.capability_id)
            if managed.state in {CapabilityState.LOADED, CapabilityState.ACTIVE, CapabilityState.READY}:
                continue
            self._transition(managed, CapabilityState.LOADED, managed.capability.initialize, "loaded")

    def _resolved_manifests(self, capability_id: str) -> list[CapabilityManifest]:
        """Resolve one managed capability graph using the shared deterministic resolver."""
        self._require_managed(capability_id)
        return self._resolver.resolve_for(
            capability_id, {identifier: item.manifest for identifier, item in self._managed.items()}
        )

    def _topological_order(self) -> list[str]:
        """Return a stable dependency-first order for all managed capability identities."""
        return [manifest.capability_id for manifest in self._resolver.resolve([item.manifest for item in self._managed.values()])]

    def _mark_ready(self, capability_id: str, status: CapabilityStatus) -> CapabilityStatus:
        """Commit READY only after the capability reports healthy post-activation status."""
        if status.health is not CapabilityHealth.HEALTHY:
            raise CapabilityLifecycleError(f"capability health verification failed: {capability_id}")
        managed = self._require_managed(capability_id)
        managed.state = CapabilityState.READY
        self._persist(managed)
        ready = self._status(managed)
        self._emit("capability.ready", ready)
        return ready

    def _validate_batch_registration(self, manifests: list[CapabilityManifest]) -> None:
        """Reject any discovery batch that would collide before durable mutation begins."""
        persistent_ids = {component["id"] for component in self._registry.load()["components"]}
        conflicting = sorted(
            manifest.capability_id
            for manifest in manifests
            if manifest.capability_id in self._managed or manifest.capability_id in persistent_ids
        )
        if conflicting:
            raise CapabilityRegistrationError(
                f"discovered capability ids are already registered: {', '.join(conflicting)}"
            )

    def _rollback_activation(
        self, registered: list[str], previous_registry: Mapping[str, Any] | None, error: BaseException
    ) -> None:
        """Compensate a failed discovery activation batch without masking its original error."""
        rollback_failed = False
        for capability_id in reversed(registered):
            managed = self._managed.get(capability_id)
            if managed is None:
                continue
            try:
                if managed.state in {CapabilityState.ACTIVE, CapabilityState.READY}:
                    managed.capability.deactivate()
                managed.capability.shutdown()
            except BaseException as rollback_error:
                if isinstance(rollback_error, (KeyboardInterrupt, SystemExit)):
                    raise
                rollback_failed = True
                self._logger.error(
                    "capability_rollback_callback_failed",
                    extra={
                        "event": "capability.rollback_callback_failed",
                        "capability_id": capability_id,
                        "failure_type": type(rollback_error).__name__,
                    },
                )
            finally:
                self._managed.pop(capability_id, None)
        try:
            self._registry.restore(previous_registry)
        except BaseException as rollback_error:
            if isinstance(rollback_error, (KeyboardInterrupt, SystemExit)):
                raise
            rollback_failed = True
            self._logger.error(
                "capability_rollback_registry_failed",
                extra={"event": "capability.rollback_registry_failed", "failure_type": type(rollback_error).__name__},
            )
        self._logger.error(
            "capability_activation_rolled_back",
            extra={
                "event": "capability.activation_rolled_back",
                "registered_count": len(registered),
                "rollback_failed": rollback_failed,
                "failure_type": type(error).__name__,
            },
        )

    def _transition(
        self,
        managed: _ManagedCapability,
        target: CapabilityState,
        operation: object,
        event_suffix: str,
    ) -> None:
        """Run one lifecycle callback and durably record its resulting state."""
        if not callable(operation):
            raise CapabilityLifecycleError("capability lifecycle operation must be callable")
        try:
            operation()
            managed.state = target
            self._persist(managed)
            self._emit(f"capability.{event_suffix}", self._status(managed))
        except BaseException as error:
            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise
            self._fail(managed, event_suffix, error)
            raise CapabilityLifecycleError(
                f"capability {event_suffix} failed: {managed.manifest.capability_id}", cause=error
            ) from error

    def _fail(self, managed: _ManagedCapability, phase: str, error: BaseException) -> None:
        """Record a failed lifecycle transition without masking the original failure."""
        managed.state = CapabilityState.FAILED
        try:
            self._persist(managed)
        except BaseException as persistence_error:
            if isinstance(persistence_error, (KeyboardInterrupt, SystemExit)):
                raise
            self._logger.error(
                "capability_failure_persistence_failed",
                extra={
                    "event": "capability.failure_persistence_failed",
                    "capability_id": managed.manifest.capability_id,
                    "phase": phase,
                    "failure_type": type(persistence_error).__name__,
                },
            )
        self._logger.error(
            "capability_failed",
            extra={
                "event": "capability.failed",
                "capability_id": managed.manifest.capability_id,
                "phase": phase,
                "failure_type": type(error).__name__,
            },
        )

    def _persist(self, managed: _ManagedCapability) -> None:
        """Upsert a capability record through the canonical ATLAS registry."""
        data = self._registry.load()
        component = {
            "id": managed.manifest.capability_id,
            "status": managed.state.value,
            "health": managed.health.value,
            "capability": managed.manifest.as_dict(),
        }
        components = [item for item in data["components"] if item["id"] != managed.manifest.capability_id]
        components.append(component)
        self._registry.save({"components": components})

    def _emit(self, event: str, status: CapabilityStatus) -> None:
        """Publish one committed lifecycle transition through HERMES and structured logs."""
        payload = status.as_dict()
        self._event_bus.publish(event, payload)
        self._logger.info(
            "capability_lifecycle_event",
            extra={"event": event, "capability_id": status.capability_id, "state": status.state.value},
        )

    def _restore_registration(self, capability_id: str) -> None:
        """Remove a newly created registration when its initial transition cannot complete."""
        data = self._registry.load()
        retained = [item for item in data["components"] if item["id"] != capability_id]
        if len(retained) != len(data["components"]):
            self._registry.save({"components": retained})

    def _registry_contains(self, capability_id: str) -> bool:
        """Check persistent identity uniqueness through ATLAS before registration."""
        return any(item["id"] == capability_id for item in self._registry.load()["components"])

    def _require_managed(self, capability_id: str) -> _ManagedCapability:
        """Resolve one current-runtime binding without dynamic provider loading."""
        if not isinstance(capability_id, str) or not capability_id.strip():
            raise CapabilityLifecycleError("capability_id must be a non-empty string")
        try:
            return self._managed[capability_id]
        except KeyError as error:
            raise CapabilityLifecycleError(f"capability is not loaded into this runtime: {capability_id}") from error

    def _validate_permissions(self, manifest: CapabilityManifest) -> None:
        """Require every requested manifest permission to be granted by Config."""
        settings = self._config.load()
        granted = settings.get("granted_permissions", [])
        if not isinstance(granted, list) or any(not isinstance(item, str) for item in granted):
            raise CapabilityPermissionError("capabilities.granted_permissions must be an array of strings")
        missing = sorted(set(manifest.permissions) - set(granted))
        if missing:
            raise CapabilityPermissionError(
                f"capability permissions are not granted for {manifest.capability_id}: {', '.join(missing)}"
            )

    @staticmethod
    def _validate_diagnostics(capability: Capability) -> None:
        """Validate that diagnostic hooks produce non-secret mapping structures."""
        if not isinstance(capability.metadata(), Mapping):
            raise CapabilityRegistrationError("capability metadata() must return a mapping")
        if not isinstance(capability.status(), Mapping):
            raise CapabilityRegistrationError("capability status() must return a mapping")

    @staticmethod
    def _status(managed: _ManagedCapability) -> CapabilityStatus:
        """Build a stable status from lifecycle-owned state only."""
        return CapabilityStatus.create(managed.manifest, managed.state, managed.health)


def _state(value: object) -> CapabilityState:
    """Parse a persisted state without accepting arbitrary registry values."""
    try:
        return CapabilityState(value)
    except (TypeError, ValueError) as error:
        raise CapabilityLifecycleError("persisted capability state is invalid") from error


def _health(value: object) -> CapabilityHealth:
    """Parse a reported health value into the stable public classification."""
    try:
        return CapabilityHealth(value)
    except (TypeError, ValueError) as error:
        raise CapabilityLifecycleError("capability health is invalid") from error
