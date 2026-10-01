# CA-015 P1 Engineering Report

Status: GREEN

## Modified files

| Area | Files | Result |
| --- | --- | --- |
| Discovery | `src/aidrax_core/capabilities/discovery.py`, configuration defaults | Deterministic recursive local JSON manifest discovery from explicit files/directories, closed-schema validation, duplicate rejection, and sorted IDs. |
| Dependencies | `src/aidrax_core/capabilities/dependencies.py`, runtime | Shared exact-version dependency resolver with missing-dependency, version-drift, cycle, and stable topological-order checks. |
| Factory | `src/aidrax_core/capabilities/factory.py` | Explicit mapping-based instance construction with no dynamic import, provider knowledge, plugin lookup, external service, or AI execution. |
| Activation | `src/aidrax_core/capabilities/runtime.py` | `discover_and_activate()` performs discovery → validation → dependency ordering → registration → activation → health verification → `READY`; failure restores the prior ATLAS snapshot and tears down newly created instances. |
| Contracts | Capability, Runtime, Configuration contracts; manifest; errors; exports | Capability Contract 2.1.0 documents discovery, factory, READY, rollback, and new classified errors. |
| Tests and verification | `tests/test_capabilities.py`, config tests, `verify.sh` | Local discovery, invalid manifests, duplicates, graph ordering, missing dependencies, READY transition, health rollback, factory rollback, installed defaults, and existing regressions covered. |

## Engineering rationale

P1 adds extension points rather than provider behavior. A future capability supplies a manifest file and an explicitly injected creator; the platform core neither imports a provider package nor executes a capability-specific protocol. `CapabilityDiscovery` validates all local manifests before registration. `DependencyResolver` produces one deterministic graph order reused by loading, activation, and shutdown. `CapabilityFactory` has one responsibility: construct an object implementing the established `Capability` interface.

The activation pipeline captures the existing ATLAS state before the first mutation. If factory construction, registration, activation, event handling, or health verification fails, every newly created instance is deactivated/shut down in reverse order and `Registry.restore` re-establishes the prior durable state. The original classified error remains visible; rollback evidence is logged through the existing structured logging path.

## Compatibility analysis

P0 APIs remain available with unchanged successful behavior. `CapabilityRuntime` receives additive optional `discovery` and `factory` dependencies; direct `register`, `load`, `activate`, `health`, `deactivate`, and `shutdown` callers remain compatible. `CapabilityState.READY`, discovery/factory exports, and classified errors are additive. Existing ATLAS records, HERMES policies, Config precedence, CLI commands, and provider absence guarantees are unchanged. Package version is synchronized at `0.15.0a2`.

## Repository Health Delta

| Area | Sprint 01 | Sprint 02 |
| --- | --- | --- |
| Manifest intake | Direct caller mapping only | Deterministic local file/directory discovery with full validation |
| Dependencies | Runtime-local recursion | Reusable deterministic resolver shared by lifecycle operations |
| Instance construction | Manual direct injection | Explicit provider-neutral factory boundary |
| Batch activation | Individual transitions | Discovery-to-READY transaction with ATLAS restoration |
| Failure evidence | Single lifecycle failure status | Factory, health, dependency, duplicate, and rollback paths tested |

## Platform Health Delta

| Platform concern | Before Sprint 02 | After Sprint 02 |
| --- | --- | --- |
| Capability intake | Callers had to supply validated manifests directly | One provider-neutral, deterministic recursive discovery boundary validates the complete batch before registration. |
| Stable runtime state | Lifecycle operations were individually durable | Batch activation is transactional at the ATLAS boundary and restores the previous stable registry state on failure. |
| Startup order | Dependency handling was limited to direct runtime activation | Exact semantic versions, cycles, absent dependencies, and a dependency-first activation order are validated centrally. |
| Provider isolation | No provider implementation was present | The factory only accepts injected creators and the canonical lifecycle contract; no provider name, dynamic import, plugin lookup, credential, or AI execution path was added. |

## Risk assessment

| Risk | Assessment | Mitigation and rollback |
| --- | --- | --- |
| Invalid or conflicting manifests | Low | Closed schema, strict semantic versions, recursive deterministic scan, and duplicate-ID rejection stop the batch before registry mutation. |
| Partial activation failure | Low | The runtime captures the ATLAS snapshot, releases created instances in reverse order, and restores the exact previous registry snapshot. |
| Callback cleanup itself fails | Medium | The original activation failure is preserved, cleanup failures are structured-logged, and the ATLAS restoration attempt still runs. Operator follow-up is required only when that log evidence appears. |
| Future version-range requirements | Low | Exact-version resolution is deliberate and documented; a range model requires an approved contract amendment rather than implicit behavior. |

## Technical Debt Delta

Reduced:

- No duplicate dependency traversal remains in activation and shutdown ordering.
- Discovery has one deterministic local implementation instead of callers needing ad-hoc manifest parsing.
- Partial discovered-batch registry state is compensated through the canonical ATLAS restore path.

Remaining:

- Dependencies intentionally use exact versions; range semantics remain deferred for an approved future contract amendment.
- Factory creator mappings are explicit in-memory composition. Persistent rebinding after restart and any provider adapter remain out of scope.
- HERMES remains synchronous/in-memory; lifecycle event durability is not introduced by this sprint.

## Validation summary

- `compileall`: GREEN
- Contract validation: GREEN
- Manifest, discovery, dependency, activation, health, and rollback validation: GREEN
- `pytest`: GREEN — 47 passed
- CI workflow validation: GREEN
- Full `verify.sh`, wheel build, isolated wheel install, registry validation, and `pip check`: GREEN

## Recommendation for Sprint 03

Perform the approved operational-hardening sprint only: add capability administration observability and contract-verifier fixtures for deliberate discovery/factory drift. Do not add a provider, AI execution, external service, plugin marketplace, or second persistence layer.

## AIDRAX Sprint Result

| Item | Result |
| --- | --- |
| Build | `0.15.0a2` |
| Commit | `CA-015 Sprint02 P1 Capability Discovery & Activation` plus the recursive-discovery completion commit |
| Branch | `closed-alpha` |
| Tests | GREEN — 47 passed |
| Verification | GREEN — compileall, contracts, CI workflow, smoke tests, wheel build, isolated wheel installation, and registry validation |
| Repository Health | GREEN — shared ATLAS, HERMES, Logger, Config, and Registry boundaries remain canonical |
| Platform Health | GREEN — deterministic discovery-to-READY transaction with rollback is available and provider agnosticism is retained |
| Technical Debt | Exact versions, in-memory creator composition, and synchronous HERMES durability remain intentionally deferred |
| Risk | Low overall; cleanup-callback failure is observable and requires operator follow-up |
| Next Recommended Sprint | Sprint 03 operational hardening only |
| READY_FOR_REVIEW | YES |
