# CA-014 Engineering Plan – Runtime Hardening

**Planning baseline:** `c3d0d23` on `closed-alpha`  
**Purpose:** Transform CAR-001 findings into reviewable hardening work.  
**Build type:** Planning only; this document introduces no runtime behavior.

## Executive Summary

CA-012 established a stable engineering baseline and CA-013 froze its public contracts. CAR-001 confirmed an acyclic, cohesive system but rated the baseline YELLOW because configuration is not reliably deployable outside the checkout, contract verification is shallow, HERMES lacks bounded failure semantics, and the pipeline can leave a partially persisted outcome.

CA-014 must harden these existing boundaries without adding a capability, provider, model, orchestration path, user surface, or architectural layer. The execution sequence is: establish reproducible configuration location, make state transitions recoverable, define HERMES failure and capacity behavior, deepen contract verification, then add CI-ready verification and performance evidence.

## Objectives

1. Make the existing configuration contract reproducible for installed commands and explicit for callers.
2. Ensure registry and integration writes have defined failure, recovery, and rollback behavior.
3. Define bounded HERMES resource use and deterministic subscriber failure semantics.
4. Extend CA-013 compatibility checks from export names to signatures, status objects, and declared exception behavior.
5. Add failure, recovery, rollback, and bounded-load test evidence without changing public architecture.

## Non Objectives

- No AI capability manager, provider adapter, model integration, Serus, AGY, or Codex runtime.
- No new transport, persistence backend, UI, service, or external network dependency.
- No replacement of ATLAS, HERMES, ARGUS, CoreRuntime, or the current contract model.
- No broad API rename or incompatible contract revision.

## Repository Health Summary

| Area | CA-013 state | CA-014 planning response |
|---|---|---|
| Package | Python 3.12 package, wheel succeeds | Verify installed-config behavior in an isolated installation. |
| Imports | 21 Python modules, no cycles, no import actions | Preserve this as a negative acceptance test. |
| Registry | One canonical ATLAS writer, atomic file replacement | Test write failure and recovery explicitly. |
| Pipeline | ATLAS then report write and HERMES publish | Specify a recoverable state transition. |
| Configuration | Shared `Config`, relative default paths | Establish one deployment-resolved configuration root. |
| HERMES | Synchronous, in-memory, unbounded queue | Define queue bound and subscriber-failure contract. |
| Contracts | Eight 1.0.0 documents and manifest | Verify signatures, exceptions, status schemas, and root exports. |
| Verification | Compile, imports, smoke, tests, wheel | Add contract behavior, installation and negative-path stages. |

## Module Inventory

| Area | Modules | CA-014 relevance |
|---|---|---|
| Core | `aidrax_core.config`, `aidrax_core.logging`, `aidrax_core.runtime` | Configuration root, logging safety, status contract. |
| Discovery/registry | `argus.scanner`, `atlas.registry` | Canonical persistence and error recovery. |
| Runtime transport | `hermes.bus` | Capacity and exception semantics. |
| Integration | `integration.pipeline` | Recoverable multi-step write flow. |
| Entry points | `cli.*` | Installed-command configuration and failure exits. |
| Assurance | `scripts/verify.sh`, `scripts/verify_contracts.py`, `tests/*` | Deeper compatibility and scenario validation. |

## Contract Inventory

CA-014 preserves all eight CA-013 contracts at `1.0.0` until a reviewed implementation justifies a compatible patch increment. The public interfaces are the exports listed in `CONTRACT_MANIFEST.json` plus the five console commands. Internal state remains `CoreRuntime.modules`, `EventBus.queue`, `EventBus.subscribers`, concrete report paths, handlers, and temporary persistence files.

## Technical Debt Inventory

| ID | Debt | Source | Priority |
|---|---|---|---|
| TD-014-01 | Relative configuration files are not deployment-resolved for installed commands. | CAR-001 | P0 |
| TD-014-02 | Pipeline has no documented compensation or recovery after partial persistence. | CAR-001 | P0 |
| TD-014-03 | HERMES queue is unbounded and subscriber exceptions are not isolated or specified. | CAR-001 | P1 |
| TD-014-04 | Contract verifier checks names, not signatures, status schemas, or exception semantics. | CAR-001 | P1 |
| TD-014-05 | Failure-path and performance evidence is sparse. | CAR-001 | P1 |
| TD-014-06 | Structured logging can stringify unexpected values and lacks an explicit redaction boundary. | CAR-001 | P2 |
| TD-014-07 | No CI execution definition is present. | CA-013 report | P2 |
| TD-014-08 | Top-level package names are generic and could collide in a larger Python environment. | CAR-001 | P3 |

## Acceptance Criteria

- Existing public API names, command names and compatible return types remain unchanged.
- A freshly installed package resolves the intended configuration without relying on checkout-relative files.
- Registry and pipeline failure paths leave either the prior valid state or a documented recoverable state, never an undocumented mixture.
- HERMES has tested capacity and subscriber-error behavior defined in `RuntimeContract.md`.
- Contract verification rejects public export, signature, status-object, exception and version drift.
- Verification includes installation, unit, integration, failure, recovery, rollback and bounded-load stages.
- The complete CA-014 pipeline is GREEN before owner review.

## Definition of Done

All accepted CA-014 tasks have a code review, matching contract update where behavior is observable, focused tests, negative-path evidence, rollback evidence, and a successful full verification run. No task may introduce provider, capability, model, external network or architectural behavior.
