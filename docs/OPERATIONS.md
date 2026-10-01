# AIDRAX OS Operations

## Structured Logging and Redaction

All runtime records use `aidrax_core.logging.StructuredFormatter` and produce JSON lines. Redaction policy 1.0 replaces sensitive structured fields with `[REDACTED]` before serialization. Sensitive names include `api_key`, `authorization`, `cookie`, `password`, `private_key`, `secret`, `session_token`, `token`, and normalized suffixes such as `client_secret` or `access_token`.

Nested mappings and sequences are traversed. Typical message fragments in the form `secret=value` are masked. Operators must pass sensitive data as structured fields, not embed it in unconstrained prose, because unstructured text cannot be classified with full certainty.

## Engineering Verification

Run the complete local verification from the repository root:

```bash
PYTHON_BIN=python3 ./scripts/verify.sh
```

The command compiles modules, validates contract headers, versions, APIs and the CI workflow, runs imports and smoke tests, executes pytest, builds a wheel, verifies installed package defaults, validates the registry, and covers capability manifest, discovery, dependency, activation, health, and rollback contracts. Success ends with `CA-015_P1_VERIFICATION_GREEN`.

## Release Verification Procedure

1. Start from the intended release commit with no unexpected source changes.
2. Install the test extra in an isolated Python 3.12 environment.
3. Run `./scripts/verify.sh` once from the repository root.
4. Confirm `CONTRACT_VALIDATION_GREEN`, `CI_WORKFLOW_VALIDATION_GREEN`, `INSTALLATION_CONFIG_GREEN`, `REGISTRY_VALIDATION_GREEN`, and the final P1 marker.
5. Review the generated wheel only from its temporary verification directory; do not add runtime artifacts to the repository.
6. Record the commit and verification output in the release handoff.

GitHub Actions executes the same `./scripts/verify.sh` command on pushes and pull requests targeting `closed-alpha`.
