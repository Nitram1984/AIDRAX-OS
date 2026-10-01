# CA-015 Engineering Plan – Capability Runtime

Status: PLANNING

## Executive Summary

CA-015 designs the first executable capability boundary for AIDRAX OS. It does not implement a provider, model, memory system, or capability. The existing `CapabilityContract` and `ProviderContract` deliberately guarantee only the absence of those integrations. CA-015 must replace that reserved boundary through an owner-approved, versioned capability contract before runtime code is added.

The target is one canonical lifecycle owned by AIDRAX OS: manifest validation, registration, discovery, dependency resolution, permission validation, loading, activation, health observation, deactivation, and shutdown. Present and future integrations enter only through this lifecycle. ATLAS remains the sole persistent registry, HERMES remains the event transport, `Config` remains the configuration boundary, and the existing structured logger remains the observability boundary.

## Objectives

1. Define one capability manifest and one lifecycle state machine.
2. Define stable contracts for runtime-facing capability operations, status, errors, events, and version compatibility.
3. Preserve provider opacity: end users continue to interact solely with AIDRAX.
4. Reuse ATLAS, HERMES, `Config`, structured logging, and the verification pipeline without parallel persistence or configuration paths.
5. Decompose implementation into reviewable, rollback-safe builds that introduce no provider implementation in CA-015 planning.

## Non Objectives

- No Serus, AGY, Codex Runtime, Memory Runtime, Context Runtime, local-model, or external-provider implementation.
- No provider credentials, network calls, provider configuration, or provider discovery.
- No replacement of ATLAS, HERMES, `CoreRuntime`, configuration, logging, contracts, CLI, or verification.
- No capability behavior, runtime code, source-code modification, commit, or package-version change in this planning build.

## Current-State Analysis

| Existing boundary | Verified current role | CA-015 constraint |
| --- | --- | --- |
| `atlas.Registry` | Sole atomic persistent component registry | It must remain the only persistence implementation; capability records use its canonical document or an approved compatible extension. |
| `hermes.EventBus` | Bounded synchronous in-memory event transport | Lifecycle observation uses named structured events and its established overflow/failure policy. |
| `aidrax_core.config.Config` | Deterministic checkout/install/default configuration resolution | Capability settings are loaded through `Config.for_component`; no ad-hoc file lookup. |
| `aidrax_core.logging` | Structured logging with central redaction | Lifecycle actions log structured, redactable context only. |
| `aidrax_core.errors` | Classified runtime failures with stable status objects | Capability-specific failures extend this model and preserve deterministic `status()`. |
| `CoreRuntime` | Current module-name status holder | It is not a capability manager and must not be silently repurposed. |
| `scripts/verify.sh` | Canonical local and CI verification command | Capability checks extend this pipeline only after their contract is approved. |

## Required Contract Decisions Before Implementation

| Decision | Proposed rule | Owner/architecture gate |
| --- | --- | --- |
| Identity | `capability_id` is a stable, lowercase dotted identifier; provider identities are metadata internal to AIDRAX. | Required |
| Manifest version | Manifest schema has independent semantic versioning; runtime accepts only declared compatible major versions. | Required |
| Registry record | The ATLAS canonical component record gains capability metadata only through a compatible Registry Contract amendment. | Required |
| Permissions | Requested permissions are explicit, finite strings; activation is denied when not granted by policy. | Required |
| Dependencies | Dependencies are capability IDs plus compatible version ranges; cycles are rejected before loading. | Required |
| Failure | Validation/load/activation/health/deactivation/shutdown failures are classified `RuntimeFailure` descendants and emit redacted structured events. | Required |
| API exposure | AIDRAX-facing contract exposes capabilities, never provider-specific conversation surfaces. | Required |

## Contract Inventory Finding

The current source tree contains one version-label inconsistency: `docs/contracts/PipelineContract.md` is labeled `1.0.1`, while `CONTRACT_MANIFEST.json` declares `PipelineContract` as `1.0.0`. The current verifier establishes document existence and manifest validity but does not compare Markdown title versions with manifest versions. CA-015 must resolve this as part of T-015-01 before introducing a capability contract amendment; this planning build does not alter either existing contract.

## Implementation Sequence

1. **Contract gate:** Amend Capability, Provider, Registry, Runtime, Logging, Configuration, Pipeline, and CLI contracts only where an observable capability surface is introduced. Add manifest entries and contract-verifier fixtures first.
2. **Domain foundation:** Introduce immutable manifest, dependency, permission, version, lifecycle-state, status, and typed-error domain objects without a provider adapter.
3. **Registry integration:** Extend the canonical ATLAS data model compatibly, migrate legacy component data at the boundary, and prove atomic rollback.
4. **Lifecycle runtime:** Add registration through shutdown with dependency ordering, policy checks, HERMES events, structured logs, and deterministic status.
5. **Operational integration:** Add configuration policy, an internal administration CLI only if approved, contract validation, and full failure/recovery tests.
6. **Provider readiness review:** Confirm that a future adapter can be implemented as a capability package without modifying core lifecycle code. Do not implement the adapter in CA-015 unless separately authorized.

## Architecture Invariants

- No provider-specific import may enter `aidrax_core`, ATLAS, HERMES, CLI, or the capability runtime core.
- Importing every module remains side-effect free.
- No lifecycle operation logs credentials, tokens, prompt content, or provider secrets.
- Every state change is observable through a structured event and log record, except validation failures before an event bus is available; those still log a classified failure.
- Activation is all-or-nothing per capability: failed activation must leave the capability inactive and restore its previous durable registry state.
- Shutdown runs active capabilities in reverse resolved dependency order; one failure is recorded but does not silently skip remaining independent shutdown actions.
- The public surface uses capability IDs and capability status only. Provider identities are internal and not user-facing.

## Acceptance Criteria

- A versioned Capability Contract defines each public type, method, status object, exception, event, and compatibility rule.
- Exactly one lifecycle owner exists; no capability bypasses registration, policy, dependency validation, or shutdown.
- ATLAS remains the only persistent registry; no side registry or direct manifest persistence is added.
- Invalid manifests, duplicate IDs, incompatible versions, missing dependencies, dependency cycles, denied permissions, load failure, activation failure, health failure, and shutdown failure have deterministic outcomes and tests.
- `verify.sh` and the GitHub workflow validate manifests, API contracts, lifecycle invariants, registry migration, unit tests, integration tests, and wheel installation.
- A reference provider-free test capability proves extension points without becoming a production provider or user-visible capability.

## Definition of Done

CA-015 implementation may be declared ready only after all approved tasks in the task matrix are reviewed, contract-validated, rollback-tested, green through the canonical verification command, and committed in scope-separated changes. This planning deliverable itself is ready for architecture and owner review only.

READY_FOR_REVIEW = YES
