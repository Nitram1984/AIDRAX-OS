# CA-015 Task Matrix

| ID | Priority | Deliverable | Affected areas | Dependencies | Verification | Rollback |
| --- | --- | --- | --- | --- | --- | --- |
| T-015-01 | P0 | Resolve the existing Pipeline Contract label/manifest mismatch, then approve executable Capability Contract classifications, semantic versions, errors, status schemas, and lifecycle event vocabulary. | Contract documents, manifest, verifier tests | Owner + architecture review | Markdown/manifest version parity and intentional contract drift both fail verification. | Revert contract-only change; no runtime state exists. |
| T-015-02 | P0 | Implement deterministic manifest, semantic-version, dependency, permission, state, health, and status domain objects. | Proposed capability contract domain | T-015-01 | Valid/invalid schema, version, permission, and status serialization tests. | Remove isolated domain package; no persistence touched. |
| T-015-03 | P0 | Define and implement ATLAS-compatible capability record normalization, migration, atomic save, and restore. | ATLAS, Registry Contract, config, tests | T-015-01, T-015-02 | Legacy registry, duplicate ID, write failure, restore, wheel-install tests. | Restore prior ATLAS document through existing `Registry.restore`. |
| T-015-04 | P1 | Implement dependency graph validation and stable topological ordering. | Capability dependency domain, tests | T-015-02 | Missing, incompatible, optional, diamond, cycle, and deterministic-order tests. | Isolated module removal; no activation path yet. |
| T-015-05 | P1 | Implement provider-neutral factory loading, lifecycle coordinator, activation/deactivation recovery, and deterministic status. | Capability runtime, runtime/errors/contracts, tests | T-015-02 through T-015-04 | Load/activate/deactivate failure and cleanup/rollback tests. | Disable new runtime surface; ATLAS restores captured record. |
| T-015-06 | P1 | Integrate redacted lifecycle logging and HERMES events, including publication-failure semantics. | logging, HERMES, contracts, tests | T-015-05 | Event payload, redaction, queue overflow, subscriber policy, publish rollback tests. | Remove event emission without changing persisted lifecycle state. |
| T-015-07 | P2 | Add capability policy configuration and optional approved administrative CLI adapter. | Config, CLI, docs, tests | T-015-05, T-015-06 | Checkout/install/default precedence and CLI failure exit tests. | Explicit config path/defaults preserve existing behavior; CLI is removable adapter. |
| T-015-08 | P2 | Extend verification and CI to validate capability contracts, manifests, registry migration, lifecycle failures, and wheel installation. | verify scripts, workflow, tests | T-015-01 through T-015-07 | Canonical `verify.sh` and hosted CI run green. | Revert validation additions independently of runtime. |
| T-015-09 | P3 | Architecture review proving a future provider adapter can integrate without modifying capability core. | Architecture review, sample non-provider fixture | T-015-08 | Core dependency graph and extension test. | Review-only. |

## Priority Rationale

P0 freezes the observable model and durable representation before behavior. P1 creates the lifecycle only after its persistence and graph semantics are proven. P2 operationalizes the approved runtime. P3 is a no-provider extensibility review; it must not be used to smuggle in an integration.
