# Platform Lifecycle

The platform starts only when every predecessor stage has completed.

1. **Configuration** validates local inputs.
2. **Logging** opens the evidence stream.
3. **ATLAS** restores the authoritative registry.
4. **HERMES** becomes the event transport.
5. **ARGUS** observes policy and health.
6. **CapabilityRuntime** discovers and activates approved capabilities.
7. **MissionControl** exposes the operator surface.

If a stage fails, the platform stops before dependent stages begin and records a
machine-readable failure event. Shutdown is reverse dependency order. AO-001
defines the lifecycle contract; it does not start host services.
