# CA-015 Capability Contract Proposal

Status: Proposed successor to the reserved Capability Contract 1.0.0. It is not an implemented public API.

## Contract Classification and Versioning

The future `CapabilityContract` is public and stable after owner approval. Its initial executable release is proposed as `2.0.0` because CA-013 explicitly reserved the name while guaranteeing no executable API. The version is intentionally a new major contract rather than a silent reinterpretation of the reserved 1.0.0 document.

`ProviderContract` remains reserved until a provider-facing adapter is separately approved. The capability contract must not require a provider package or provider credentials.

## Proposed Public Domain Objects

| Object | Required fields / behavior | Notes |
| --- | --- | --- |
| `CapabilityManifest` | `capability_id`, `version`, `runtime_api_version`, `entrypoint`, `priority`, `dependencies`, `permissions`, `metadata` | Immutable validated representation; `metadata` must contain no secrets. |
| `CapabilityDependency` | `capability_id`, `version_specifier`, `required` | `required=false` dependencies never alter topological ordering unless present. |
| `CapabilityPermission` | finite approved permission name | No implicit permissions and no wildcard grant. |
| `CapabilityState` | lifecycle values defined in the lifecycle document | Serialized as stable strings. |
| `CapabilityHealth` | `UNKNOWN`, `HEALTHY`, `DEGRADED`, `UNHEALTHY` | Separate from lifecycle state. |
| `CapabilityStatus` | `capability_id`, `version`, `state`, `health`, `updated_at`, `dependencies`, `permissions`, optional `failure` | Stable return object for discovery and runtime inspection. |
| `CapabilityRuntime` | registration, discovery, load, activate, deactivate, health, status, shutdown | The only supported lifecycle owner. |

## Proposed Manifest Schema

```json
{
  "schema_version": "1.0.0",
  "capability_id": "aidrax.example",
  "version": "1.0.0",
  "runtime_api_version": "2.0.0",
  "entrypoint": "package.module:factory",
  "priority": 100,
  "dependencies": [
    {"capability_id": "aidrax.dependency", "version_specifier": ">=1.0.0,<2.0.0", "required": true}
  ],
  "permissions": ["runtime.events.publish"],
  "metadata": {"display_name": "Internal capability"}
}
```

The example is schema documentation, not a provider or runnable capability. `entrypoint` is an internal implementation locator and is never surfaced as a user identity. The final schema must define a closed allowed-key set and JSON primitive types so it can be deterministically validated without arbitrary code execution.

## Proposed Runtime Interface

| Method | Return | Deterministic failure |
| --- | --- | --- |
| `register(manifest) -> CapabilityStatus` | Registered status | manifest, version, duplicate-ID, dependency-declaration, or permission validation error |
| `discover() -> list[CapabilityStatus]` | Sorted, non-registered discovery results | discovery failure result; no implicit registration |
| `load(capability_id) -> CapabilityStatus` | Loaded status | missing/incompatible/cyclic dependency or load failure |
| `activate(capability_id) -> CapabilityStatus` | Active status | unsatisfied dependency, denied permission, activation failure |
| `deactivate(capability_id) -> CapabilityStatus` | Inactive status | deactivation failure |
| `health(capability_id) -> CapabilityStatus` | Same lifecycle state with refreshed health | health failure status |
| `status(capability_id=None) -> CapabilityStatus | list[CapabilityStatus]` | One or all stable status objects | unknown ID validation error |
| `shutdown() -> ShutdownStatus` | Aggregate reverse-order outcome | aggregate failure status preserves every failed capability |

The precise Python type names and signatures must be recorded in `CONTRACT_MANIFEST.json` before their implementation lands. The runtime accepts dependency injection for ATLAS, HERMES, `Config`, logger, clock, and factory resolver; defaults use the existing AIDRAX implementations.

## Error Contract

Capability failures inherit the current `RuntimeFailure` model and preserve its `status`, `code`, `message`, and `recovered` fields. Proposed additive codes are `capability_manifest`, `capability_dependency`, `capability_permission`, `capability_load`, `capability_activation`, `capability_health`, `capability_deactivation`, and `capability_shutdown`.

Each lifecycle failure must identify the `capability_id`, transition phase, prior state, target state, and recovery result in a redacted structured log and a stable error status. Input compatibility with `ValueError` or `TypeError` must be explicitly selected per exception and enforced by contract verification.

## Compatibility Guarantees

- Capability IDs are never reused for a semantically unrelated implementation.
- A manifest major version change is incompatible; minor and patch versions must remain backward compatible with the declared runtime API range.
- Adding optional manifest fields is a compatible minor schema change only when older runtimes can reject or ignore them deterministically according to the schema rule.
- Existing CA-014 APIs, CLI commands, config paths, and registry behavior remain stable.
- The runtime does not expose provider-specific names, credentials, SDK types, or transport errors through a public AIDRAX-facing contract.
