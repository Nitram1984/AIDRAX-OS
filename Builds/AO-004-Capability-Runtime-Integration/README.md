# AIDRAX OS — AO-004 Capability Runtime Integration

AO-004 composes the existing canonical `CapabilityRuntime` into the platform boot path. It owns no capability lifecycle itself: it calls the existing discover/activate and shutdown methods through an injected adapter.

No provider, secret, network, dynamic plugin source, or second registry is introduced.
