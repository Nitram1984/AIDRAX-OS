from __future__ import annotations

from collections.abc import Callable, Mapping

from .errors import ProviderRegistrationError
from .provider import Provider

ProviderCreator = Callable[[], Provider]


class ProviderFactory:
    """Explicit provider construction boundary; never dynamically imports code."""

    def __init__(self, creators: Mapping[str, ProviderCreator]):
        if not isinstance(creators, Mapping) or any(not isinstance(k, str) or not k for k in creators):
            raise ProviderRegistrationError("provider factory creators must be a mapping of non-empty keys")
        if any(not callable(v) for v in creators.values()):
            raise ProviderRegistrationError("provider factory creators must be callable")
        self._creators = dict(creators)

    def create(self, creator_key: str) -> Provider:
        try:
            creator = self._creators[creator_key]
        except KeyError as error:
            raise ProviderRegistrationError(f"unknown provider creator: {creator_key}") from error
        provider = creator()
        if not isinstance(provider, Provider):
            raise ProviderRegistrationError(f"provider creator returned incompatible object: {creator_key}")
        return provider
