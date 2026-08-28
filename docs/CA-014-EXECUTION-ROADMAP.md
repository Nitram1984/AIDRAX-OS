# CA-014 Execution Roadmap

## Phase 0 – Contract decision gate

Review and approve the exact public semantics for configuration roots, HERMES overflow, subscriber errors and pipeline recovery. No implementation begins until these decisions are reflected in the affected CA-013 contracts or approved compatible amendments.

## Phase 1 – Deterministic configuration and persistence

Execute T-014-01 then T-014-02. Require isolated-install evidence, stage-level failure injection, recovery rerun evidence and explicit rollback instructions before progressing.

## Phase 2 – Runtime behavior hardening

Execute T-014-03. Verify FIFO behavior, capacity behavior, error behavior, logging and pending-count state under both success and failure.

## Phase 3 – Assurance hardening

Execute T-014-04 and T-014-05. The verifier must reject contract drift intentionally, and tests must cover unit, integration, failure, recovery, rollback and bounded-load scenarios.

## Phase 4 – Operational readiness

Execute T-014-06 and T-014-07 if the P0/P1 exit criteria are met. T-014-08 remains a recorded review output, not a runtime modification.

## Test Strategy

| Test type | Required evidence |
|---|---|
| Unit | Config root resolution, registry atomic behavior, HERMES validation and logging field policy. |
| Integration | Installed CLI → configuration → ARGUS/ATLAS/HERMES/pipeline flow in an isolated directory. |
| Failure | Invalid config, inaccessible write target, malformed registry, full queue and raising subscriber. |
| Recovery | Rerun after a forced pipeline stage failure returns a coherent documented state. |
| Rollback | Previous registry/report state remains restorable after every unsuccessful transition. |
| Performance | Bounded queue behavior and a deterministic small-load benchmark with no unbounded memory growth. |

## CA-014 Exit Gate

CA-014 is ready for owner review only when P0 and P1 tasks are complete, contracts and manifest agree, verification is GREEN in a clean Python 3.12 environment, and the hardening changes do not introduce any provider, capability or architecture change.
