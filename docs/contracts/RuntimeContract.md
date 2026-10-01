# Runtime Contract 1.0.4

**Classification:** Public  
**Stability:** Stable

Module `aidrax_core.runtime` exports `CoreRuntime`. `CoreRuntime(config=None)` creates isolated runtime state. `register(name)` accepts a non-empty string and returns `None`; invalid names raise `RuntimeValidationError`, also a `ValueError`. `status()` returns the stable status object `{"modules": list[str], "count": int}`. `settings` returns the object loaded through the supplied or default `Config`.

Module `hermes` exports `EventBus`. `subscribe(event, handler)` and `publish(event, payload)` return `None`; `pending()` returns `int`. Invalid event names raise `RuntimeValidationError`, also a `ValueError`; non-callable handlers and non-mapping payloads raise `RuntimeTypeError`, also a `TypeError`; an unsupported configured queue raises `ConfigurationError`.

The in-memory queue uses `capacity`, `overflow_policy`, `subscriber_failure_policy` and optional `subscriber_timeout_seconds` from `hermes.json`. The default capacity is 256 and default overflow policy is `reject`: `publish` raises `QueueOverflowError` before queue mutation. `drop_oldest` is the only explicit event-loss policy and emits `hermes.event_dropped`. Subscriber failures and post-execution deadline overruns are logged. Policy `continue` isolates them and continues delivery; policy `raise` propagates `SubscriberFailureError` or `SubscriberTimeoutError` after the event has been queued. A deadline is measured for a synchronous handler after it returns; it does not attempt unsafe thread termination.

The root package exports `RuntimeFailure`, `RuntimeFailureCode`, `ConfigurationError`, `RegistryError`, `PipelineError`, `RuntimeValidationError`, `RuntimeTypeError`, `QueueOverflowError`, `SubscriberFailureError`, `SubscriberTimeoutError`, `CapabilityManifestError`, `CapabilityDiscoveryError`, `CapabilityRegistrationError`, `CapabilityDependencyError`, `CapabilityFactoryError`, `CapabilityPermissionError`, and `CapabilityLifecycleError`. Every classified failure has `status()` returning `status`, `code`, `message` and `recovered`; `PipelineError.status()` additionally returns `phase`.

`CoreRuntime.modules`, `EventBus.queue`, and `EventBus.subscribers` are internal implementation state and are not stable mutation surfaces.
