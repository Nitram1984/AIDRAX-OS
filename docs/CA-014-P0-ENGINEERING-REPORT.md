# CA-014 Sprint 01 P0 Engineering Report

**Baseline:** CA-013 commit `c3d0d23` on `closed-alpha`  
**Scope:** P0 configuration resolution, pipeline recovery and classified runtime failures  
**Status:** GREEN

## Modified Files

| Area | Files | Result |
|---|---|---|
| Runtime errors | `src/aidrax_core/errors.py`, `src/aidrax_core/__init__.py`, `src/aidrax_core/runtime/core.py`, `src/hermes/bus.py` | One classified `RuntimeFailure` model with stable error status objects; compatible `ValueError` and `TypeError` inheritance is preserved. |
| Configuration | `src/aidrax_core/config/config.py`, `src/aidrax_core/config/defaults/*.json`, `pyproject.toml` | Deterministic order: environment directory, source checkout configuration, packaged defaults; explicit paths remain unchanged. |
| Registry and pipeline | `src/atlas/registry.py`, `src/integration/pipeline.py`, `src/integration/__init__.py` | Registry restoration and durable pipeline rollback for registry/report artifacts; classified pipeline errors and structured failure/rollback events. |
| Contracts | `docs/contracts/CONTRACT_MANIFEST.json`, `ConfigurationContract.md`, `RegistryContract.md`, `RuntimeContract.md`, `PipelineContract.md` | Compatible 1.0.1 contract amendments and package version alignment to `0.14.0a1`. |
| Assurance | `tests/test_config.py`, `tests/test_core.py`, `tests/test_bus.py`, `tests/test_pipeline.py`, `scripts/verify.sh` | P0 tests plus source-independent installed-wheel configuration verification. |
| Documentation | `README.md`, `docs/BUILD.md`, `CHANGELOG.md` | CA-014 Sprint 01 operation and verification details. |

## Engineering Rationale

CA-013 resolved defaults relative to the running directory. CA-014 removes that repository-only assumption without breaking explicit `Config(path)` or `Config.for_component(component, config_directory)` callers. A configurable `AIDRAX_CONFIG_DIR` has highest precedence, a source checkout resolves from its package location rather than the current directory, and an installed wheel reads the packaged default JSON assets.

The integration pipeline now captures prior registry and report states before mutating either. If validation, persistence, report creation or event publication fails after durable state was captured, it restores the durable artifacts and raises `PipelineError` with phase, code, cause and recovery state. A HERMES subscriber can already have observed an in-memory event; that case is explicitly classified as `phase="publish"`, `recovered=false`, and is not reported as a complete rollback.

## Test Summary

```text
CONTRACT_VALIDATION_GREEN
26 passed
INSTALLATION_CONFIG_GREEN
REGISTRY_VALIDATION_GREEN
CA-014_P0_VERIFICATION_GREEN
No broken requirements found.
```

The suite covers absent and invalid explicit configuration, environment precedence, packaged defaults, classified CoreRuntime and HERMES validation failures, pipeline failure at publication, durable rollback, retry recovery, imports, contracts, smoke flow, wheel build and clean wheel installation.

## Risk Assessment

- **Configuration asset duplication:** Packaged JSON defaults intentionally mirror the established root configuration so that wheels are self-contained. The resolver has one deterministic precedence order and tests all supported locations.
- **Pipeline event rollback:** Durable artifacts are restored. In-memory subscriber side effects cannot be reversed by the present HERMES contract; the failure status therefore remains unrecovered and exposes the exact phase.
- **Compatibility:** `ConfigurationError`, `RegistryError`, input `ValueError`, and input `TypeError` remain catch-compatible with CA-013 consumers while now exposing classified runtime status.
- **Operational logging:** Failures and rollback outcomes emit structured events through the existing logger; no provider, network or capability path was added.

## Compatibility Analysis

Existing public command names, existing function names and successful return values are unchanged. `integrate` still returns `int` on success; on any failure it now consistently raises `PipelineError` rather than exposing varying lower-level exceptions. `Registry.restore` and the exported root error types are compatible additions. Contract versions changed only by compatible patch increments for the affected surfaces.

## Remaining Technical Debt

- HERMES is still unbounded and synchronously invokes subscribers; capacity and subscriber isolation are Sprint 02/P1 work.
- Pipeline cannot reverse arbitrary effects performed by a HERMES subscriber; it reports that condition deterministically.
- Logging redaction policy and CI integration remain P2 work.
- Namespace-collision assessment remains P3 review-only work.

## Recommendation for Sprint 02

Implement the approved P1 HERMES capacity and subscriber-failure policy, then deepen the contract verifier to assert signatures, status-object schemas and exception semantics. Build the resulting failure, recovery, rollback and bounded-load test suite before CI integration.
