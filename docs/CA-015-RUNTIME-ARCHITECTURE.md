# CA-015 Runtime Architecture

Status: Target architecture for approved implementation; no current module is changed by this document.

## Canonical Integration Path

```text
Internal AIDRAX request
        |
CapabilityRuntime
  | manifest/policy/dependency/lifecycle
  +--> Config                 (configuration resolution)
  +--> ATLAS Registry         (sole durable capability record)
  +--> Factory Resolver       (validated entrypoint loading)
  +--> HERMES EventBus        (lifecycle events)
  +--> Structured Logger      (redacted operational evidence)
        |
Active internal capability
```

The capability runtime is the only lifecycle owner. A capability may not write its own registration record, bypass dependency ordering, self-activate outside the runtime, or publish undocumented lifecycle state. The capability implementation boundary is below the runtime; AIDRAX remains the sole user-visible intelligence layer.

## Proposed Module Boundaries

| Proposed module area | Responsibility | May depend on | Must not depend on |
| --- | --- | --- | --- |
| `aidrax_core.capabilities.contracts` | Immutable domain objects, manifest validation, versions, statuses, errors | `aidrax_core.errors` | ATLAS, HERMES, CLI, provider packages |
| `aidrax_core.capabilities.dependencies` | Graph validation and deterministic topological ordering | contracts | factories, CLI, provider packages |
| `aidrax_core.capabilities.runtime` | Lifecycle coordination and recovery | contracts, dependencies, Config, Registry, EventBus, logging | CLI, provider package imports at module import time |
| `aidrax_core.capabilities.discovery` | Candidate manifest discovery through approved sources | contracts, Config | registry writes, provider SDKs |
| `atlas.registry` | Canonical atomic capability record persistence | config, errors, logging | capability factories, HERMES, CLI |
| `cli.capabilities` (only if approved) | Internal administrative adapter | runtime, logging | direct ATLAS/HERMES mutation |

The package naming is a proposed implementation boundary, not a decision to create modules in this build. Dependency direction must remain acyclic: CLI → CapabilityRuntime → contracts/dependencies + infrastructure adapters; ATLAS and HERMES never import runtime or CLI.

## Registry Architecture

ATLAS retains the single document root `{"components": [...]}`. CA-015 must choose one compatible representation before code changes:

1. Extend the existing component object with an optional `capability` mapping, preserving legacy `id`, `path`, and `status`; or
2. Introduce an optional typed component category within the same canonical ATLAS document.

Either representation requires a Registry Contract patch/minor revision, normalization rules, migration fixtures, atomic persistence, and restoration through `Registry.restore`. A separate `capabilities.json`, SQLite database, or provider registry is prohibited by this plan.

## Event Architecture

Proposed lifecycle event names are `capability.registered`, `capability.loaded`, `capability.activated`, `capability.deactivated`, `capability.health_changed`, `capability.failed`, and `capability.shutdown_completed`. Payloads contain capability ID, version, lifecycle state, health, correlation ID, and failure code only; they must not contain manifest secrets, credentials, prompt content, or raw provider exceptions.

The event contract needs a HERMES-compatible mapping payload and must honor capacity and subscriber-failure policy. Event delivery is observability, not a second state store.

## Configuration and Permissions

Capability configuration is one `Config.for_component("capabilities")` mapping plus per-capability non-secret settings referenced by ID. Permission grants are policy configuration owned by the platform, not capability-supplied values. The runtime computes `requested ∩ granted`; missing required permissions deny activation before factory loading.

Secrets, if a later approved provider requires them, remain external to manifests, logs, and registry records. Secret retrieval requires a future approved security contract and is explicitly out of scope.

## Shutdown and Failure Containment

The runtime owns factory instances and calls shutdown/deactivation in reverse dependency order. It records each result, continues with independent capabilities, and returns an aggregate deterministic status. It does not terminate processes, threads, or external providers; such behavior would require a later capability-specific contract.
