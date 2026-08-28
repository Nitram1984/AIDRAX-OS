# Identity Contract

AO-002 is an authorization boundary, not a provider-authentication system.

| Object | Contract |
| --- | --- |
| `Principal` | immutable local ID, display name, and finite roles |
| `IdentityPolicy` | explicit action-to-role allowance |
| `Session` | random ephemeral handle containing no credential |
| `IdentityRuntime` | registration, policy evaluation, session lifecycle, evidence events |

The runtime calls ATLAS through `RegistryAdapter.add()` on startup and HERMES
through `EventBusAdapter.publish()` for lifecycle and decision events. Event
payloads contain only IDs, roles, actions, and timestamps; ARGUS can consume
them as audit evidence. No payload includes passwords, tokens, or providers.
