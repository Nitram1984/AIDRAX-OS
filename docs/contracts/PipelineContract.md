# Pipeline Contract 1.0.1

**Classification:** Public  
**Stability:** Stable

Module `integration` exports `integrate(projects, registry=None, event_bus=None, config=None) -> int` and `PipelineError`. It accepts a sequence of component mappings, normalizes them using the Registry Contract, captures prior durable state, persists the complete registry through ATLAS, writes `reports/events.json`, then publishes `component.discovered` through HERMES and returns the number of integrated components.

Any `integrate` failure raises `PipelineError` with a classified cause and deterministic status. Before HERMES publication, the prior registry and report are restored where possible; `recovered=true` means durable rollback completed. A subscriber failure can leave an already published in-memory event, so it is reported with `phase="publish"` and `recovered=false`; it is never silent. `registry`, `event_bus`, and `config` are dependency-injection parameters. Their concrete defaults, report file location, and log field details are internal implementation details.
