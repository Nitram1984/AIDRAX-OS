# CA-015 P0 Engineering Report

Status: GREEN

## Modified files

| Area | Files | Result |
| --- | --- | --- |
| Capability domain | `src/aidrax_core/capabilities/*`, `src/aidrax_core/errors.py`, `src/aidrax_core/__init__.py` | Canonical manifest, strict semantic versions, dependency declarations, provider-neutral interface, lifecycle states, health, statuses, runtime and classified errors. |
| Canonical persistence | `src/atlas/registry.py`, Registry Contract | ATLAS accepts additive `health` and `capability` records while preserving legacy component normalization and atomic persistence. |
| Configuration | `config/capabilities.json`, packaged default, Configuration Contract | The existing `Config` path supplies the explicit `granted_permissions` policy. |
| Contracts | Capability, Registry, Runtime, Configuration, Pipeline contracts; manifest; verifier | Capability Contract 2.0.0 is executable; Pipeline Contract manifest/title are both 1.0.1; document-version parity is machine-validated. |
| Assurance | `tests/test_capabilities.py`, existing contract/config tests, `scripts/verify.sh` | Manifest, lifecycle, duplicate, dependency, version, permission, contract and clean-install checks are covered. |
| Documentation | README, build notes, changelog, contract overview | CA-015 P0 scope and provider-free boundary are explicit. |

## Engineering rationale

`CapabilityRuntime` is the single lifecycle owner. It receives explicitly injected objects conforming to `Capability`; no dynamic import, plugin discovery, provider SDK, network call, model invocation, or AI execution was introduced. The runtime validates a closed manifest schema, persists state through the existing ATLAS registry, emits committed lifecycle observations through HERMES, loads configuration only through `Config`, and uses the existing redacted structured logger.

The P0 gate is closed. `PipelineContract.md` and `CONTRACT_MANIFEST.json` now both declare 1.0.1, and contract verification rejects future document/manifest version divergence.

## Compatibility analysis

Existing CA-014 exports, CLI commands, registry records, HERMES behavior, configuration precedence, and successful return values are unchanged. Registry support for `health` and `capability` is additive; legacy records remain valid. New capability APIs are exported only from `aidrax_core.capabilities`, and new error types are additive root exports. The package version is `0.15.0a1` and matches the contract manifest.

## Risk assessment

Risk is controlled and low for the existing platform because no external provider or executable capability was introduced. The primary new boundary is injected lifecycle behavior: activation, health, deactivation, and shutdown can fail, so each failure is classified, logged, and persisted as `FAILED`. HERMES remains the established synchronous in-memory transport; its documented queue and subscriber policies continue to apply to lifecycle events.

## Technical debt

- P0 intentionally uses exact dependency versions; compatible version ranges require an owner-approved future contract increment.
- Runtime instance bindings are in-memory by design. Rebinding an implementation after process restart is deferred until a separately approved factory/loading build.
- Permission policy is an explicit string allow-list; secret retrieval and provider authorization remain out of scope.
- The prior CA-014 namespace-collision assessment remains a P3 concern.

## Repository health delta

| Area | Before | After |
| --- | --- | --- |
| Capability lifecycle | Reserved contract only | One typed, provider-neutral lifecycle owner |
| Manifest validation | None | Closed deterministic schema and strict semantic versions |
| Durable capability state | None | ATLAS-only, atomically persisted additive records |
| Contract drift detection | Header versions unchecked | Manifest/title parity validated |
| Failure-path evidence | No capability coverage | Manifest, duplicate, dependency, permission, lifecycle and persistence tests |

## Validation summary

- `compileall`: GREEN
- Contract validation: GREEN
- Manifest and lifecycle validation: GREEN
- `pytest`: GREEN — 42 passed
- CI workflow validation: GREEN
- Full `verify.sh`, wheel build, isolated wheel install, registry validation: GREEN

## Recommendation for Sprint 02

Implement only the approved next capability-runtime layer: dependency graph enhancement and restart-safe factory binding, after an explicit contract decision for version ranges and activation recovery semantics. Do not introduce a provider, AI execution, plugin loading, or a parallel registry.
