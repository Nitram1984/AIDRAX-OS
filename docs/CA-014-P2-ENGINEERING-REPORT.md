# CA-014 P2 Engineering Report

Status: GREEN
Build: CA-014 Runtime Hardening – Sprint 03 (P2)
Branch: `closed-alpha`

## Modified files

| Area | Files | Result |
| --- | --- | --- |
| Structured logging | `src/aidrax_core/logging/logger.py`, `src/aidrax_core/logging/__init__.py`, `tests/test_logger.py` | Central, deterministic redaction for sensitive structured fields and nested payloads. |
| Contract freeze | `docs/contracts/LoggingContract.md`, `docs/contracts/CONTRACT_MANIFEST.json`, `pyproject.toml`, `src/aidrax_core/__init__.py` | Logging contract advanced from 1.0.0 to 1.0.1; package version advanced to `0.14.0a3`. |
| CI verification | `.github/workflows/verification.yml`, `scripts/verify_ci_workflow.py`, `tests/test_ci.py`, `scripts/verify.sh` | GitHub Actions delegates to the canonical verification command; its definition is validated locally. |
| Operations documentation | `docs/OPERATIONS.md`, `README.md`, `docs/BUILD.md`, `CHANGELOG.md` | Reproducible logging, verification, and release procedures. |

## Engineering rationale

Structured logging now uses one redaction policy. Sensitive field names and stable suffixes are classified centrally, values are replaced with `[REDACTED]`, and nested mappings and sequences are handled recursively. Non-sensitive context remains visible for diagnosis. The formatter also masks conventional `key=value` and `key: value` secret fragments in log messages.

The verification workflow has no duplicate verification logic: GitHub Actions installs the test extra and executes `./scripts/verify.sh`. The local CI-workflow validator ensures the workflow continues to use the approved Python version, dependency installation, and canonical command.

## Test summary

| Validation | Result |
| --- | --- |
| `compileall` | GREEN |
| Contract validation | GREEN |
| CI workflow validation | GREEN |
| Import validation | GREEN |
| Smoke tests | GREEN |
| `pytest` | GREEN — 35 passed |
| Wheel build and isolated installation | GREEN |
| Registry validation | GREEN |
| `pip check` | GREEN |
| Diff whitespace check | GREEN |

Canonical command:

```bash
PYTHON_BIN=/tmp/aidrax-ca012-venv/bin/python ./scripts/verify.sh
```

In a standard development environment, omit `PYTHON_BIN` to use the default `python3` interpreter.

## Risk assessment

Risk is low. The change is additive to the existing logging facade and retains the existing `configure_logging`, `get_logger`, and formatter behavior for non-sensitive values. Redaction intentionally prevents sensitive values from being available in output; this is a security property, not a data-loss defect.

The message redactor recognizes standard key/value forms. Callers should continue to provide secrets in structured fields rather than embedding them in unrestricted prose, which cannot be safely classified without false positives.

## Operational improvements

- A single policy now covers sensitive field classification and nested structured payloads.
- CI and local release verification execute the same canonical pipeline.
- `docs/OPERATIONS.md` supplies an explicit release verification sequence and expected success markers.

## Compatibility analysis

No public API was removed or had its signature changed. The logging module adds public helpers (`is_sensitive_field`, `redact_log_value`) and public policy constants, recorded in the contract manifest. Existing structured events retain their fields except that sensitive values are deterministically replaced with `[REDACTED]`. The installable package version is synchronized with the contract manifest.

## Remaining technical debt

- Redaction of arbitrary free-form prose is intentionally limited; structured logging remains the supported safe path.
- CI execution is defined and locally validated, but the first remote GitHub Actions run requires the repository host to receive a push or pull request.
- Existing P1 operational constraints, including explicitly selected HERMES loss policy behavior, remain outside this P2 scope.

## Recommendation for Sprint 04

Perform a P3-only operational review of real hosted CI results, release artifacts, and log retention requirements. Do not expand runtime capabilities or alter stable contracts without a separately approved plan.
