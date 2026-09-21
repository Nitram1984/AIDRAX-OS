from __future__ import annotations

import json
from pathlib import Path

from aidrax_core.capabilities.factory import CapabilityFactory
from aidrax_core.capabilities.manifest import CapabilityManifest

from .capability import AIProviderCapability
from .runtime import ProviderRuntime

DEFAULT_MANIFEST = Path("config/capability-manifests/aidrax-ai-provider-runtime.json")


def load_manifest(path: str | Path = DEFAULT_MANIFEST) -> CapabilityManifest:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return CapabilityManifest.from_mapping(data)


def capability_factory(provider_runtime: ProviderRuntime) -> CapabilityFactory:
    return CapabilityFactory({
        "ai-provider-runtime": lambda: AIProviderCapability(provider_runtime),
    })
