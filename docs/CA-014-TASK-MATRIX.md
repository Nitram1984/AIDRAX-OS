# CA-014 Task Matrix

| ID | Priority | Task | Affected modules | Complexity | Dependencies | Verification | Rollback |
|---|---|---|---|---|---|---|---|
| T-014-01 | P0 | Define and implement one installed-package configuration-root resolution policy while preserving explicit `Config(path)` callers. | `aidrax_core.config`, installer, package metadata, config docs, CLI tests | M | None | Isolated install resolves each existing config; explicit path remains unchanged; absent config still returns `{}`. | Revert resolution change; explicit paths remain a safe fallback. |
| T-014-02 | P0 | Make `integrate` recoverable across registry persistence, event report write and HERMES publication. Define its observable failure outcome before code changes. | `integration.pipeline`, `atlas.registry`, `PipelineContract`, tests | M | T-014-01 | Forced failure after each stage; prior registry and report states checked; rerun recovery checked. | Preserve previous valid artifacts or restore backup created by the transition. |
| T-014-03 | P1 | Define queue capacity and subscriber exception semantics for existing in-memory HERMES. | `hermes.bus`, `config/hermes.json`, `RuntimeContract`, tests | M | T-014-01 | Full queue, rejecting/handling subscriber failure, ordering and pending-count tests. | Restore current in-memory behavior through a contract-compatible configuration default only if the approved policy permits. |
| T-014-04 | P1 | Upgrade contract verifier to inspect declared signatures, root package exports, status-object shape and exception contracts. | `scripts/verify_contracts.py`, manifest, contracts, tests | M | T-014-02, T-014-03 | Deliberate fixture drift for each checked contract must fail the verifier. | Revert verifier checks independently; no runtime state changes. |
| T-014-05 | P1 | Add focused unit, failure, recovery, rollback and bounded-load tests for every changed hardening boundary. | `tests/*`, `scripts/verify.sh` | M | T-014-01 through T-014-04 | Targeted tests plus full pipeline. | Test-only changes are independently reversible. |
| T-014-06 | P2 | Define a logging redaction and supported-value policy for structured extra fields. | `aidrax_core.logging`, `LoggingContract`, tests | S | T-014-04 | Sensitive key/value and non-serializable value tests. | Preserve existing formatter behavior if policy is rejected before release. |
| T-014-07 | P2 | Add a CI execution definition that invokes the existing verification command on Python 3.12. | CI asset, docs | S | T-014-05 | Clean environment executes full pipeline. | Disable the CI asset without runtime impact. |
| T-014-08 | P3 | Assess package-namespace collision risk and present a compatibility-preserving migration proposal only. | packaging docs, CAR follow-up | S | None | Review-only; no rename in CA-014 unless separately approved. | Not applicable. |

## Implementation Order

1. T-014-01, because all installed command and configuration tests need a stable resolution policy.
2. T-014-02, because pipeline recovery determines the observable state contract.
3. T-014-03, because HERMES semantics are required by the pipeline’s final step.
4. T-014-04, after the observable contracts are final.
5. T-014-05, then T-014-06 and T-014-07; T-014-08 remains review-only.

## Priority Matrix

| Priority | Meaning | CA-014 tasks |
|---|---|---|
| P0 | Required to make installed runtime state deterministic and recoverable. | T-014-01, T-014-02 |
| P1 | Required before a hardening release claim. | T-014-03, T-014-04, T-014-05 |
| P2 | Strengthens operational safety and repeatability. | T-014-06, T-014-07 |
| P3 | Architectural preparation with no CA-014 runtime change. | T-014-08 |
