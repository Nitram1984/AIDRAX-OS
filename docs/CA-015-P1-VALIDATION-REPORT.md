# CA-015 P1 Validation Report

Status: GREEN

## Scope

This report records the validation evidence for CA-015 Sprint 02 P1 Capability Discovery & Activation on branch `closed-alpha`. It covers the provider-neutral capability layer only; no provider runtime, AI execution, marketplace, or external service was introduced.

## Executed validation

| Gate | Command or check | Result |
| --- | --- | --- |
| Source compilation | `compileall -q src tests scripts` via `scripts/verify.sh` | GREEN |
| Public contracts | `python scripts/verify_contracts.py` | GREEN — `CONTRACT_VALIDATION_GREEN` |
| CI definition | `python scripts/verify_ci_workflow.py` | GREEN — `CI_WORKFLOW_VALIDATION_GREEN` |
| Import and smoke checks | Embedded checks in `scripts/verify.sh` | GREEN — `IMPORT_VALIDATION_GREEN`, `SMOKE_TESTS_GREEN` |
| Capability tests | `pytest` | GREEN — 47 passed |
| Manifest validation | Closed schema, strict semantic version validation, invalid JSON and duplicate-ID cases in capability tests | GREEN |
| Recursive discovery | Nested `*.json` manifest fixture discovered deterministically and returned in capability-ID order | GREEN |
| Dependency validation | Missing dependency, exact-version mismatch, cycle detection, and dependency-first ordering tests | GREEN |
| Activation validation | Discovery → validation → resolution → registration → instantiation → activation → health → `READY` test | GREEN |
| Rollback validation | Failed health and failed factory creation restore the prior ATLAS registry state and release created instances | GREEN |
| Factory validation | Missing creator and incompatible lifecycle implementation are rejected through the provider-neutral factory boundary | GREEN |
| Package build | `pip wheel --no-build-isolation --no-deps .` | GREEN — `aidrax_os-0.15.0a2-py3-none-any.whl` |
| Isolated installation | Fresh virtual environment installation and packaged Config checks | GREEN — `INSTALLATION_CONFIG_GREEN` |
| Registry validation | Canonical ATLAS registry read check | GREEN — `REGISTRY_VALIDATION_GREEN` |

## Contract conformance

| Engineering System Contract area | Evidence |
| --- | --- |
| Platform first | Capability code is an additive boundary and does not alter ATLAS, HERMES, Config, Logger, or core runtime ownership. |
| Provider neutrality | Discovery reads only local manifests; factory uses injected callables and no provider name, plugin lookup, dynamic import, credential, or AI execution path. |
| Canonical components | ATLAS remains the only persistence path; HERMES emits lifecycle events; `CapabilityRuntime` owns lifecycle transitions; Config and Logger are reused. |
| Quality gates | One discovery implementation, one dependency resolver, no parallel registry, documented public exports, and existing direct lifecycle APIs preserved. |
| Capability rules | Every instantiated object is validated against the canonical lifecycle protocol and activation occurs only through `CapabilityRuntime`. |
| Repository health | Recursive scan closes the last stated discovery gap; technical debt and rollback behavior are documented in the engineering report. |

## Validation environment

The project system Python did not include `pytest`. Validation therefore used an isolated temporary Python 3.12 environment with `pytest 8.4.2` and `setuptools 84.0.0`; no project dependency or source file was changed to accommodate the environment.

## Sprint Result

`READY_FOR_REVIEW = YES`

The next sprint should remain operational hardening and observability only. Provider implementations, AI execution, a marketplace, and alternative persistence remain out of scope.
