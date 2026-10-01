"""Provider-neutral explicit factory for capability interface instances."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from aidrax_core.capabilities.contracts import Capability
from aidrax_core.capabilities.manifest import CapabilityManifest
from aidrax_core.errors import CapabilityFactoryError

CapabilityCreator = Callable[[], Capability]


class CapabilityFactory:
    """Create only explicitly configured capability instances; never load providers or plugins."""

    def __init__(self, creators: Mapping[str, CapabilityCreator]) -> None:
        """Retain immutable explicit creators keyed by canonical capability ID."""
        if not isinstance(creators, Mapping):
            raise CapabilityFactoryError("capability factory creators must be a mapping")
        if any(not isinstance(capability_id, str) or not capability_id for capability_id in creators):
            raise CapabilityFactoryError("capability factory creator ids must be non-empty strings")
        if any(not callable(creator) for creator in creators.values()):
            raise CapabilityFactoryError("capability factory creators must be callable")
        self._creators = dict(creators)

    def create(self, manifest: CapabilityManifest) -> Capability:
        """Create one instance for a validated manifest without dynamic importing."""
        try:
            creator = self._creators[manifest.capability_id]
        except KeyError as error:
            raise CapabilityFactoryError(f"no capability factory creator for: {manifest.capability_id}") from error
        try:
            capability = creator()
        except BaseException as error:
            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise
            raise CapabilityFactoryError(
                f"capability factory creator failed for: {manifest.capability_id}", cause=error
            ) from error
        if not isinstance(capability, Capability):
            raise CapabilityFactoryError(
                f"capability factory creator returned an incompatible object: {manifest.capability_id}"
            )
        return capability
