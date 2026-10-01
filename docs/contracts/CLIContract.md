# CLI Contract 1.0.0

**Classification:** Public  
**Stability:** Stable

The public commands are `aidrax-core`, `aidrax-events`, `aidrax-integrate`, `aidrax-registry`, and `aidrax-scan`. Each maps to the same `main(argv=None) -> int` convention, returns `0` on successful completion, emits structured logs, and has no action at Python import time.

`aidrax-events EVENT [--payload JSON_OBJECT]`, `aidrax-integrate PROJECT [PROJECT ...]`, `aidrax-registry [--path PATH]`, and `aidrax-scan [--root PATH] [--output PATH]` are stable argument forms. `aidrax-core` takes no arguments. Python modules below `cli` are internal adapters; only their console-command mappings are public.
