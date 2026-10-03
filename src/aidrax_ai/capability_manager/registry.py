from __future__ import annotations

import re

from aidrax_ai.provider.errors import ProviderRegistrationError
from aidrax_ai.provider.provider import Provider

_ID = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")


class CapabilityRegistry:
    def __init__(self):
        self._providers: dict[str, Provider] = {}
        self._provider_ids: dict[int, str] = {}

    def register(self, provider: Provider, provider_id: str | None = None) -> str:
        if not isinstance(provider, Provider):
            raise ProviderRegistrationError("provider must implement the Provider contract")
        pid = provider_id or self._default_id(provider.name())
        if _ID.fullmatch(pid) is None:
            raise ProviderRegistrationError(f"invalid provider id: {pid}")
        if pid in self.provider_ids():
            raise ProviderRegistrationError(f"provider id already registered: {pid}")
        capabilities = self._validate_capabilities(provider.capabilities())
        collisions = sorted(set(capabilities) & set(self._providers))
        if collisions:
            raise ProviderRegistrationError("capability already registered: " + ", ".join(collisions))
        for capability in capabilities:
            self._providers[capability] = provider
        self._provider_ids[id(provider)] = pid
        return pid

    def resolve(self, capability: str) -> Provider | None:
        return self._providers.get(capability)

    def provider_id(self, provider: Provider) -> str:
        try:
            return self._provider_ids[id(provider)]
        except KeyError as error:
            raise ProviderRegistrationError("provider is not registered") from error

    def provider_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._provider_ids.values()))

    def capabilities(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))

    @staticmethod
    def _validate_capabilities(value: object) -> tuple[str, ...]:
        if not isinstance(value, tuple) or not value:
            raise ProviderRegistrationError("provider capabilities must be a non-empty tuple")
        if any(not isinstance(item, str) or not item.strip() for item in value):
            raise ProviderRegistrationError("provider capabilities must contain non-empty strings")
        normalized = tuple(item.strip() for item in value)
        if len(set(normalized)) != len(normalized):
            raise ProviderRegistrationError("provider capabilities must not contain duplicates")
        return normalized

    @staticmethod
    def _default_id(name: str) -> str:
        value = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
        if not value:
            raise ProviderRegistrationError("provider name cannot produce a stable id")
        return value
