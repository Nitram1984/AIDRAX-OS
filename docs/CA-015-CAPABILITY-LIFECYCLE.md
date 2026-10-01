# CA-015 Capability Lifecycle

Status: Proposed contract model; no runtime behavior is introduced by this document.

## Canonical States

| State | Meaning | Persisted in ATLAS | Eligible next states |
| --- | --- | --- | --- |
| `DISCOVERED` | A manifest was found but has not passed registration validation. | No | `REGISTERED`, `FAILED` |
| `REGISTERED` | Manifest, identity, version, permissions, and dependency declaration are valid. | Yes | `LOADED`, `INACTIVE`, `FAILED`, `UNREGISTERED` |
| `LOADED` | Capability implementation was instantiated but is not active. | Yes | `ACTIVE`, `INACTIVE`, `FAILED` |
| `ACTIVE` | Capability passed activation and may serve internal AIDRAX runtime requests. | Yes | `DEACTIVATING`, `FAILED` |
| `DEACTIVATING` | Deactivation is in progress; new runtime requests are rejected. | Yes | `INACTIVE`, `FAILED` |
| `INACTIVE` | Capability is registered but not serving requests. | Yes | `LOADED`, `UNREGISTERED`, `FAILED` |
| `FAILED` | The latest lifecycle transition failed with a classified status. | Yes | `LOADED`, `INACTIVE`, `UNREGISTERED` |
| `UNREGISTERED` | Registry record was removed after successful shutdown and dependency checks. | No | terminal |

`DISCOVERED` is an ephemeral scan result. Every other observable state has a deterministic capability status. A capability never transitions directly from `ACTIVE` to `UNREGISTERED`; deactivation and shutdown are mandatory.

## Transition Rules

| Operation | Preconditions | Success | Failure / rollback |
| --- | --- | --- | --- |
| Register | Valid manifest, unique ID, supported manifest version, approved permissions, dependencies syntactically valid | `REGISTERED` and atomic ATLAS record | No record is persisted; classified validation error |
| Discover | Source contains candidate manifest | ephemeral `DISCOVERED` result | Invalid candidate is reported as a classified discovery result, not registered |
| Load | `REGISTERED`, dependencies registered and version-compatible, no cycle | `LOADED` | Instance is discarded; prior registry state restored; `FAILED` recorded only if the record existed |
| Activate | `LOADED`, transitive dependencies `ACTIVE`, permissions granted | `ACTIVE` | Deactivation/cleanup is attempted; state becomes `INACTIVE` or `FAILED` with recovery flag |
| Health check | `LOADED` or `ACTIVE` | Same state plus fresh health timestamp/status | State unchanged; failure is recorded and policy decides whether it becomes `FAILED` |
| Deactivate | `ACTIVE` | `INACTIVE` | `FAILED`; runtime rejects new requests during recovery |
| Unregister | `INACTIVE`, no registered dependents | `UNREGISTERED` | Record remains unchanged |
| Shutdown | Runtime owns loaded capabilities | All active capabilities deactivate in reverse dependency order | Independent capabilities continue; aggregate classified shutdown result is returned |

## Lifecycle Ordering

1. Validate manifest schema and capability identity.
2. Validate version compatibility and requested permissions.
3. Resolve transitive dependencies and reject missing or cyclic graphs.
4. Persist the canonical registry record atomically.
5. Instantiate and load in topological dependency order.
6. Activate in topological dependency order.
7. Publish lifecycle events after each committed state transition.
8. On shutdown, deactivate in reverse topological order and then release loaded instances.

Events are published only after the durable state transition they describe. A HERMES publication failure follows the established pipeline rule: durable state may be valid while the operation returns a classified unrecovered publish failure. This condition must never be reported as a complete rollback.

## Health Model

Every capability status contains `state`, `capability_id`, `version`, `updated_at`, `health`, and optional classified failure status. Health is one of `UNKNOWN`, `HEALTHY`, `DEGRADED`, or `UNHEALTHY`. Health observation does not grant activation; activation remains a lifecycle operation with its own preconditions.

The capability core invokes no network health probes itself. A future adapter may implement its own health observation behind the approved capability interface. Timeouts, retry policy, and external liveness checks require a later explicit contract decision.

## Recovery Model

- Manifest and policy validation failures do not mutate durable state.
- Registry persistence failure retains the last valid ATLAS document.
- Load and activation failures run the capability cleanup hook when available, restore the previous durable record, and return a classified `RuntimeFailure` status.
- Publication failure is classified separately from durable rollback because HERMES subscribers can observe an event before an error is propagated.
- Shutdown produces an aggregate status that retains each capability failure; it does not hide failures behind a successful process exit.
