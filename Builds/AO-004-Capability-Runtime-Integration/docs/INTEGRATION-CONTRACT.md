# Integration Contract

`CapabilityBootstrap` receives the canonical runtime as an injected adapter. It invokes `discover_and_activate()` once per boot, keeps a read-only status snapshot, and delegates shutdown. ATLAS remains the sole registry, HERMES remains the event bus, ARGUS consumes emitted evidence, and `CapabilityRuntime` remains the only lifecycle owner.
