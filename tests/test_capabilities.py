"""Capability runtime contract and lifecycle tests without provider integrations."""

from __future__ import annotations

import json

import pytest

from aidrax_core.capabilities import (
    CapabilityDiscovery,
    CapabilityFactory,
    CapabilityHealth,
    CapabilityManifest,
    CapabilityRuntime,
    CapabilityState,
    DependencyResolver,
)
from aidrax_core.config import Config
from aidrax_core.errors import (
    CapabilityDependencyError,
    CapabilityDiscoveryError,
    CapabilityFactoryError,
    CapabilityLifecycleError,
    CapabilityManifestError,
    CapabilityPermissionError,
    CapabilityRegistrationError,
)
from atlas.registry import Registry
from hermes.bus import EventBus


class LifecycleProbe:
    """Provider-free contract implementation used to verify lifecycle orchestration."""

    def __init__(self, health: CapabilityHealth = CapabilityHealth.HEALTHY, fail_on: str | None = None) -> None:
        self.calls: list[str] = []
        self.health_value = health
        self.fail_on = fail_on

    def initialize(self) -> None:
        self._record("initialize")

    def activate(self) -> None:
        self._record("activate")

    def deactivate(self) -> None:
        self._record("deactivate")

    def health(self) -> CapabilityHealth:
        self._record("health")
        return self.health_value

    def shutdown(self) -> None:
        self._record("shutdown")

    def metadata(self) -> dict[str, str]:
        return {"kind": "lifecycle-probe"}

    def status(self) -> dict[str, str]:
        return {"state": "ready"}

    def _record(self, operation: str) -> None:
        self.calls.append(operation)
        if self.fail_on == operation:
            raise RuntimeError(f"{operation} failed")


def capability_manifest(
    capability_id: str = "aidrax.test",
    *,
    version: str = "1.0.0",
    dependencies: list[dict[str, str]] | None = None,
    permissions: list[str] | None = None,
) -> dict[str, object]:
    """Build a complete canonical manifest fixture without provider behavior."""
    return {
        "id": capability_id,
        "name": "Test capability",
        "version": version,
        "description": "Provider-neutral lifecycle test capability",
        "author": "AIDRAX",
        "dependencies": [] if dependencies is None else dependencies,
        "permissions": [] if permissions is None else permissions,
        "health": "UNKNOWN",
        "priority": 10,
        "supported_interfaces": ["aidrax.capability.v1"],
    }


def runtime(tmp_path, granted_permissions: list[str] | None = None) -> CapabilityRuntime:
    """Create a fully injected capability runtime over existing infrastructure."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    settings_path = tmp_path / "capabilities.json"
    settings_path.write_text(
        json.dumps({"granted_permissions": [] if granted_permissions is None else granted_permissions}),
        encoding="utf-8",
    )
    return CapabilityRuntime(
        registry=Registry(tmp_path / "registry" / "components.json"),
        event_bus=EventBus(),
        config=Config(settings_path),
    )


def write_manifest(directory, manifest: dict[str, object], filename: str) -> None:
    """Persist one local JSON manifest for deterministic discovery tests."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / filename).write_text(json.dumps(manifest), encoding="utf-8")


def test_manifest_validation_is_closed_and_deterministic():
    manifest = CapabilityManifest.from_mapping(capability_manifest())

    assert manifest.as_dict() == capability_manifest()

    invalid = capability_manifest()
    invalid["extra"] = "forbidden"
    with pytest.raises(CapabilityManifestError, match="unexpected fields"):
        CapabilityManifest.from_mapping(invalid)

    invalid_version = capability_manifest(version="1.0")
    with pytest.raises(CapabilityManifestError, match="semantic versioning"):
        CapabilityManifest.from_mapping(invalid_version)


def test_registration_discovery_and_full_lifecycle_use_atlas_and_hermes(tmp_path):
    registry = Registry(tmp_path / "registry" / "components.json")
    event_bus = EventBus()
    settings_path = tmp_path / "capabilities.json"
    settings_path.write_text('{"granted_permissions": []}', encoding="utf-8")
    capability_runtime = CapabilityRuntime(
        registry=registry,
        event_bus=event_bus,
        config=Config(settings_path),
    )
    probe = LifecycleProbe()

    registered = capability_runtime.register(capability_manifest(), probe)
    assert registered.state is CapabilityState.REGISTERED
    assert capability_runtime.discover()[0].as_dict()["id"] == "aidrax.test"
    assert capability_runtime.activate("aidrax.test").state is CapabilityState.ACTIVE
    assert capability_runtime.health("aidrax.test").health is CapabilityHealth.HEALTHY
    assert capability_runtime.deactivate("aidrax.test").state is CapabilityState.INACTIVE
    assert capability_runtime.shutdown()[0].state is CapabilityState.INACTIVE
    assert probe.calls == ["initialize", "activate", "health", "deactivate", "shutdown"]
    assert [event for event, _ in event_bus.queue] == [
        "capability.registered",
        "capability.loaded",
        "capability.activated",
        "capability.health_changed",
        "capability.deactivated",
        "capability.shutdown_completed",
    ]
    persisted = registry.load()["components"]
    assert persisted[0]["capability"]["id"] == "aidrax.test"
    assert persisted[0]["status"] == "INACTIVE"


def test_duplicate_registration_is_rejected_against_runtime_and_atlas(tmp_path):
    capability_runtime = runtime(tmp_path)
    capability_runtime.register(capability_manifest(), LifecycleProbe())

    with pytest.raises(CapabilityRegistrationError, match="already registered"):
        capability_runtime.register(capability_manifest(), LifecycleProbe())

    restarted = runtime(tmp_path)
    with pytest.raises(CapabilityRegistrationError, match="already registered"):
        restarted.register(capability_manifest(), LifecycleProbe())


def test_dependency_validation_loads_dependencies_in_order_and_rejects_version_drift(tmp_path):
    capability_runtime = runtime(tmp_path)
    dependent = LifecycleProbe()
    dependency = LifecycleProbe()
    capability_runtime.register(
        capability_manifest("aidrax.dependent", dependencies=[{"id": "aidrax.base", "version": "1.0.0"}]),
        dependent,
    )
    capability_runtime.register(capability_manifest("aidrax.base"), dependency)

    capability_runtime.activate("aidrax.dependent")
    assert dependency.calls == ["initialize", "activate"]
    assert dependent.calls == ["initialize", "activate"]

    drift_runtime = runtime(tmp_path / "drift")
    drift_runtime.register(capability_manifest("aidrax.base", version="1.0.0"), LifecycleProbe())
    drift_runtime.register(
        capability_manifest("aidrax.dependent", dependencies=[{"id": "aidrax.base", "version": "1.1.0"}]),
        LifecycleProbe(),
    )
    with pytest.raises(CapabilityDependencyError, match="version mismatch"):
        drift_runtime.load("aidrax.dependent")


def test_dependency_cycle_and_permission_denial_are_classified(tmp_path):
    capability_runtime = runtime(tmp_path)
    capability_runtime.register(
        capability_manifest("aidrax.alpha", dependencies=[{"id": "aidrax.beta", "version": "1.0.0"}]),
        LifecycleProbe(),
    )
    capability_runtime.register(
        capability_manifest("aidrax.beta", dependencies=[{"id": "aidrax.alpha", "version": "1.0.0"}]),
        LifecycleProbe(),
    )
    with pytest.raises(CapabilityDependencyError, match="cyclic dependency"):
        capability_runtime.load("aidrax.alpha")

    permission_runtime = runtime(tmp_path / "permission")
    permission_runtime.register(
        capability_manifest("aidrax.restricted", permissions=["runtime.events.publish"]), LifecycleProbe()
    )
    with pytest.raises(CapabilityPermissionError, match="not granted"):
        permission_runtime.activate("aidrax.restricted")


def test_lifecycle_failure_is_classified_and_persisted(tmp_path):
    capability_runtime = runtime(tmp_path)
    capability_runtime.register(capability_manifest(), LifecycleProbe(fail_on="activate"))

    with pytest.raises(CapabilityLifecycleError, match="activated failed") as error:
        capability_runtime.activate("aidrax.test")

    assert error.value.status()["code"] == "capability_lifecycle"
    assert capability_runtime.status("aidrax.test").state is CapabilityState.FAILED


def test_local_discovery_validates_manifests_rejects_duplicates_and_sorts_ids(tmp_path):
    manifests = tmp_path / "manifests"
    write_manifest(manifests, capability_manifest("aidrax.zeta"), "zeta.json")
    write_manifest(manifests / "nested", capability_manifest("aidrax.alpha"), "alpha.json")

    assert [manifest.capability_id for manifest in CapabilityDiscovery([manifests]).discover()] == [
        "aidrax.alpha",
        "aidrax.zeta",
    ]

    duplicate = tmp_path / "duplicate"
    write_manifest(duplicate, capability_manifest("aidrax.alpha"), "again.json")
    with pytest.raises(CapabilityDiscoveryError, match="duplicate discovered capability id"):
        CapabilityDiscovery([manifests, duplicate]).discover()

    invalid = tmp_path / "invalid"
    write_manifest(invalid, capability_manifest(version="1.0"), "invalid.json")
    with pytest.raises(CapabilityManifestError, match="semantic versioning"):
        CapabilityDiscovery([invalid]).discover()


def test_dependency_resolver_has_stable_order_and_rejects_missing_dependencies():
    manifests = [
        CapabilityManifest.from_mapping(
            capability_manifest("aidrax.top", dependencies=[{"id": "aidrax.right", "version": "1.0.0"}])
        ),
        CapabilityManifest.from_mapping(capability_manifest("aidrax.right")),
        CapabilityManifest.from_mapping(capability_manifest("aidrax.base")),
        CapabilityManifest.from_mapping(
            capability_manifest("aidrax.left", dependencies=[{"id": "aidrax.base", "version": "1.0.0"}])
        ),
    ]
    manifests[0] = CapabilityManifest.from_mapping(
        capability_manifest(
            "aidrax.top",
            dependencies=[
                {"id": "aidrax.left", "version": "1.0.0"},
                {"id": "aidrax.right", "version": "1.0.0"},
            ],
        )
    )

    assert [manifest.capability_id for manifest in DependencyResolver().resolve(manifests)] == [
        "aidrax.base",
        "aidrax.left",
        "aidrax.right",
        "aidrax.top",
    ]

    missing = CapabilityManifest.from_mapping(
        capability_manifest("aidrax.missing", dependencies=[{"id": "aidrax.absent", "version": "1.0.0"}])
    )
    with pytest.raises(CapabilityDependencyError, match="missing capability dependency"):
        DependencyResolver().resolve([missing])


def test_discovery_activation_pipeline_marks_capabilities_ready(tmp_path):
    manifests = tmp_path / "manifests"
    write_manifest(manifests, capability_manifest("aidrax.beta"), "02-beta.json")
    write_manifest(manifests, capability_manifest("aidrax.alpha"), "01-alpha.json")
    alpha = LifecycleProbe()
    beta = LifecycleProbe()
    settings_path = tmp_path / "capabilities.json"
    settings_path.write_text(
        json.dumps({"granted_permissions": [], "discovery_directories": [str(manifests)]}),
        encoding="utf-8",
    )
    registry = Registry(tmp_path / "registry" / "components.json")
    event_bus = EventBus()
    capability_runtime = CapabilityRuntime(
        registry=registry,
        event_bus=event_bus,
        config=Config(settings_path),
        factory=CapabilityFactory({"aidrax.alpha": lambda: alpha, "aidrax.beta": lambda: beta}),
    )

    ready = capability_runtime.discover_and_activate()

    assert [status.capability_id for status in ready] == ["aidrax.alpha", "aidrax.beta"]
    assert all(status.state is CapabilityState.READY for status in ready)
    assert alpha.calls == ["initialize", "activate", "health"]
    assert beta.calls == ["initialize", "activate", "health"]
    assert [component["status"] for component in registry.load()["components"]] == ["READY", "READY"]
    assert [event for event, _ in event_bus.queue].count("capability.ready") == 2


def test_discovery_activation_rolls_back_atlas_and_instances_after_health_failure(tmp_path):
    manifests = tmp_path / "manifests"
    write_manifest(manifests, capability_manifest("aidrax.alpha"), "alpha.json")
    write_manifest(manifests, capability_manifest("aidrax.beta"), "beta.json")
    alpha = LifecycleProbe()
    beta = LifecycleProbe(health=CapabilityHealth.UNHEALTHY)
    registry = Registry(tmp_path / "registry" / "components.json")
    settings_path = tmp_path / "capabilities.json"
    settings_path.write_text(
        json.dumps({"granted_permissions": [], "discovery_directories": [str(manifests)]}),
        encoding="utf-8",
    )
    capability_runtime = CapabilityRuntime(
        registry=registry,
        event_bus=EventBus(),
        config=Config(settings_path),
        factory=CapabilityFactory({"aidrax.alpha": lambda: alpha, "aidrax.beta": lambda: beta}),
    )

    with pytest.raises(CapabilityLifecycleError, match="health verification failed"):
        capability_runtime.discover_and_activate()

    assert registry.load() == {"components": []}
    assert capability_runtime.status() == []
    assert alpha.calls == ["initialize", "activate", "health", "deactivate", "shutdown"]
    assert beta.calls == ["initialize", "activate", "health", "deactivate", "shutdown"]


def test_factory_failure_rolls_back_earlier_discovered_registration(tmp_path):
    manifests = tmp_path / "manifests"
    write_manifest(manifests, capability_manifest("aidrax.alpha"), "alpha.json")
    write_manifest(manifests, capability_manifest("aidrax.beta"), "beta.json")
    alpha = LifecycleProbe()
    registry = Registry(tmp_path / "registry" / "components.json")
    settings_path = tmp_path / "capabilities.json"
    settings_path.write_text(
        json.dumps({"granted_permissions": [], "discovery_directories": [str(manifests)]}),
        encoding="utf-8",
    )
    capability_runtime = CapabilityRuntime(
        registry=registry,
        event_bus=EventBus(),
        config=Config(settings_path),
        factory=CapabilityFactory({"aidrax.alpha": lambda: alpha}),
    )

    with pytest.raises(CapabilityFactoryError, match="no capability factory creator"):
        capability_runtime.discover_and_activate()

    assert registry.load() == {"components": []}
    assert alpha.calls == ["shutdown"]
