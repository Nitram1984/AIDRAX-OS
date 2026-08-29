# Mission Control Contract

`MissionControl` receives three read-only adapters: `RegistryView` supplies the current ATLAS component view, `EventView` supplies an already-redacted HERMES event view, and `HealthView` supplies the current ARGUS health view.

`snapshot()` canonicalizes component and health records by identifier and returns immutable tuples. It accepts neither a filesystem path nor any registry/event/lifecycle mutation interface. It therefore does not replace ATLAS persistence, HERMES transport, ARGUS observability, or the canonical capability lifecycle.

`propose_action()` is deliberately not an execution API. It creates an immutable proposal with status `PENDING_OWNER` unless an injected Owner Gate returns approval. Even an approved proposal is `APPROVED_FOR_DISPATCH` only; the canonical AIDRAX orchestrator must validate and dispatch it through its own policy and runtime boundaries.
