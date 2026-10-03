from __future__ import annotations

from aidrax_ai.provider.errors import ProviderError
from aidrax_ai.provider.runtime import ProviderRuntime

from .result import CapabilityResult


class CapabilityManager:
    def __init__(self, provider_runtime: ProviderRuntime | None = None):
        self.runtime = provider_runtime if provider_runtime is not None else ProviderRuntime()
        self.registry = self.runtime.registry

    def register(self, provider, provider_id: str | None = None):
        return self.runtime.register(provider, provider_id)

    def initialize(self):
        return self.runtime.initialize_all()

    def execute(self, capability, payload):
        provider = self.registry.resolve(capability)
        if provider is None:
            return CapabilityResult(capability, "", False, error="capability not registered")
        provider_id = self.registry.provider_id(provider)
        try:
            data = self.runtime.execute(capability, payload)
            return CapabilityResult(capability, provider_id, True, data=data)
        except ProviderError as error:
            return CapabilityResult(capability, provider_id, False, error=str(error))
