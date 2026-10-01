# CA-014 Sprint 02 P1 Engineering Report

**Baseline:** CA-014 Sprint 01 commit `7d98c02` on `closed-alpha`  
**Scope:** HERMES runtime resilience, contract validation depth and failure-path tests  
**Status:** GREEN

## Modified Files

| Area | Files | Result |
|---|---|---|
| HERMES | `src/hermes/bus.py`, `config/hermes.json`, `src/aidrax_core/config/defaults/hermes.json` | Bounded queue, explicit overflow policy, subscriber failure policy and synchronous deadline classification. |
| Runtime errors | `src/aidrax_core/errors.py`, `src/aidrax_core/__init__.py` | Queue overflow, subscriber failure and subscriber timeout become classified public runtime failures. |
| Contracts | `docs/contracts/CONTRACT_MANIFEST.json`, `RuntimeContract.md` | Runtime contract 1.0.2; API signatures, status-object schemas and exception inheritance are now machine-checked. |
| Verification | `scripts/verify_contracts.py`, `scripts/verify.sh`, `tests/test_contracts.py`, `tests/test_bus.py`, `tests/test_pipeline.py`, `tests/test_config.py` | Interface-drift, capacity, overflow, subscriber, timeout, corrupted-config and rollback paths are validated. |
| Documentation | `README.md`, `docs/BUILD.md`, `CHANGELOG.md` | Sprint 02 runtime and verification behavior documented. |

## Engineering Rationale

HERMES remains the existing in-memory event bus. It now derives four validated settings from the established `hermes.json`: `capacity`, `overflow_policy`, `subscriber_failure_policy` and optional `subscriber_timeout_seconds`. The default policy is conservative: capacity 256, overflow rejection and subscriber continuation. Therefore an overflowing event is rejected before queue mutation, and a failing subscriber cannot silently stop subsequent subscribers.

Event loss requires the explicit `drop_oldest` policy and produces a structured warning. Policy `raise` makes a subscriber error observable to the caller as `SubscriberFailureError`; deadline overruns become `SubscriberTimeoutError`. The deadline is intentionally measured after synchronous handler execution because safe cancellation of arbitrary Python code is not available in this architecture.

Contract validation now verifies public method names, parameter lists, return annotations, runtime/failure status schemas and promised exception base classes. A regression fixture proves that parameter drift fails validation.

## Test Summary

```text
CONTRACT_VALIDATION_GREEN
33 passed
INSTALLATION_CONFIG_GREEN
REGISTRY_VALIDATION_GREEN
CA-014_P1_VERIFICATION_GREEN
No broken requirements found.
```

Tests cover subscriber exception isolation, explicit exception propagation, queue rejection, explicit drop-oldest behavior, deadline classification, invalid HERMES state, corrupted HERMES configuration, contract signature drift, pipeline rollback and post-failure recovery.

## Risk Assessment

- **Queue behavior:** The default rejects new events at capacity rather than silently losing them. Existing workloads that exceed 256 pending events now receive an explicit `QueueOverflowError` and must choose a policy deliberately.
- **Subscriber policy:** `continue` is the default and preserves event-system availability. `raise` is deliberate and preserves the queued event, which is documented and testable.
- **Deadline semantics:** A deadline detects an overlong synchronous call after return; it cannot preempt arbitrary handler code. This limitation is explicit and avoids unsafe background execution.
- **Contract strictness:** Signature validation can intentionally block incompatible API changes before runtime. Compatible additions require a manifest and contract update.

## Compatibility Analysis

Existing `EventBus(config=None)`, `subscribe`, `publish` and `pending` signatures and successful return values are unchanged. New configuration keys have stable defaults. The public error additions are compatible extensions. `ValueError`/`TypeError` compatibility remains for existing input validation errors; queue and subscriber policy errors are new explicit failure categories.

## Repository Health Delta

| Measure | Sprint 01 | Sprint 02 |
|---|---:|---:|
| Full tests | 26 | 33 |
| Contract checks | exports, versions | exports, versions, signatures, status schemas, exception bases |
| HERMES capacity | unbounded | configured and bounded |
| Subscriber failure behavior | implicit propagation | explicit continue/raise policy with structured logs |
| Event loss behavior | undefined under unbounded growth | rejected by default; loss only by explicit policy |

## Technical Debt Delta

Resolved: unbounded queue behavior, unspecified subscriber-error handling, shallow API compatibility checks, missing queue/timeout/corrupted-configuration failure tests.

Remaining: synchronous subscribers cannot be forcibly interrupted; logging redaction and CI integration are P2; namespace collision assessment remains P3. No provider, capability, model, memory-runtime or architecture debt was introduced.

## Recommendation for Sprint 03

Proceed with approved P2 only: structured logging redaction policy and CI integration of the established verification pipeline. Do not introduce a new runtime capability or modify the HERMES architecture in that sprint.
