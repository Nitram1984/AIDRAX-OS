# CA-014 Risk Matrix

| Risk | Likelihood | Impact | Affected task | Mitigation | Rollback trigger |
|---|---|---|---|---|---|
| Installed commands silently use fallback rather than owner-configured files. | High | High | T-014-01 | Isolated-install tests and explicit configuration-root contract. | Config root changes command behavior unexpectedly. |
| Pipeline failure leaves registry, event report and bus state inconsistent. | Medium | High | T-014-02 | Stage-level failure injection, recoverable transition design and rerun tests. | Any forced failure cannot restore or explain state. |
| Queue bound changes expected HERMES behavior. | Medium | Medium | T-014-03 | Preserve FIFO ordering and document rejection behavior before implementation. | Existing public flows lose messages without defined signal. |
| Handler isolation hides faults or propagates them inconsistently. | Medium | High | T-014-03 | Decide one explicit error policy, log it and test it. | Handler errors become silent or corrupt pending state. |
| Stricter compatibility verifier rejects valid public behavior. | Low | Medium | T-014-04 | Fixture-driven verification and review of every declared signature. | Verifier mismatches approved contract text. |
| Redaction policy removes necessary diagnostic context. | Medium | Low | T-014-06 | Keep field allow/deny rules observable and test selected values. | Operations cannot diagnose a supported failure. |
| CI differs from the local Python 3.12 environment. | Medium | Medium | T-014-07 | Pin Python version and run the same `verify.sh` entrypoint. | CI-only breakage cannot be reproduced locally. |
| Namespace migration breaks imports. | Medium | High | T-014-08 | Review only; no CA-014 rename. | Any proposal lacks a compatibility bridge. |

## Security Focus

- Keep CLI arguments as data; do not introduce shell execution.
- Keep registry writes inside explicitly selected paths and test write errors.
- Do not log raw secrets or arbitrary object representations without a documented policy.
- Ensure import validation remains zero-I/O and zero-network.
