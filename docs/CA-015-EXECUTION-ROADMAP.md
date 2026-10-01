# CA-015 Execution Roadmap

## Phase A — Contract and Data Model Gate

Review and approve T-015-01 through T-015-03. The result is an executable capability contract, a documented ATLAS representation, and migration/rollback criteria. No lifecycle code starts before this phase is accepted.

**Exit criteria:** public contract versions, status schemas, error inheritance, event names, permissions, schema compatibility, and ATLAS migration strategy are owner-approved.

## Phase B — Deterministic Lifecycle Core

Implement T-015-04 and T-015-05 in small, independently verifiable changes. Prove dependency ordering, cycle rejection, loading, activation, deactivation, cleanup, recovery, and aggregate shutdown status using provider-free fixtures only.

**Exit criteria:** no partial activation after a forced failure; all lifecycle outcomes have stable statuses and classified errors; imports remain side-effect free.

## Phase C — Operations and Verification

Implement T-015-06 through T-015-08. Integrate redacted observability, HERMES lifecycle events, policy configuration, any approved CLI adapter, contract verification, migration checks, clean-wheel tests, and hosted CI.

**Exit criteria:** `verify.sh` is green locally and in CI, lifecycle logs/events are redacted and deterministic, and installed-package tests do not rely on a checkout.

## Phase D — Extensibility Review

Perform T-015-09 as an architecture review. Demonstrate that a future adapter can be placed behind a validated factory entrypoint without changing capability-core source. Do not implement Serus, AGY, Codex Runtime, Memory Runtime, Context Runtime, or any provider as part of this review.

**Exit criteria:** architecture review confirms the dependency graph and public AIDRAX-only boundary; owner separately authorizes any first real capability build.

## Test Strategy

| Test level | Required evidence |
| --- | --- |
| Unit | Manifest schema, semver, permissions, status object, state transitions, dependency graph, error status. |
| Integration | ATLAS persistence/migration/restore, runtime plus HERMES events, config precedence, CLI only if approved. |
| Failure | Invalid manifests, duplicate IDs, denied permissions, missing/incompatible dependencies, cycles, load/activation/deactivation/health/shutdown exceptions, queue and subscriber failures. |
| Recovery | Prior registry restoration, cleanup after activation failure, deterministic failed state, retried activation. |
| Rollback | Atomic registry failure, report/event publication failure semantics, migration rollback. |
| Packaging | Compileall, import side-effect scan, contract validation, clean-wheel install, full pytest, registry validation. |

## Release Gate

The release command remains `./scripts/verify.sh`. It may be extended only after the contracts and tests are added. A green local result, green hosted CI result, contract review, rollback evidence, and owner approval are all required before declaring CA-015 implementation complete.

READY_FOR_REVIEW = YES
