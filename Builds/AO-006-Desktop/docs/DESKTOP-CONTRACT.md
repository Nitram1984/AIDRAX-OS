# Desktop Shell Contract

`DesktopShell` is a local presentation model with `LOCKED` and `READY` states. `unlock()` accepts only an already-authenticated principal identifier; authentication remains the responsibility of the approved login layer.

Controls produce immutable proposals only. Without an injected canonical Owner Gate, every `SESSION`, `RESTART`, or `POWER` proposal remains `PENDING_OWNER`. The shell never invokes a process, systemd, DBus, SDDM, or host power interface. ATLAS, HERMES, ARGUS, CapabilityRuntime and AIDRAX retain their established authority.
