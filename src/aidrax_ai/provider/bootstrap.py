from __future__ import annotations

from pathlib import Path

from .catalog import ProviderCatalog
from .factory import ProviderFactory
from .ollama import OllamaProvider
from .runtime import AuthorizationHook, ProviderRuntime


def build_default_provider_runtime(
    authorization: AuthorizationHook | None = None,
    catalog_path: str | Path = "config/providers.json",
    *,
    initialize: bool = False,
) -> ProviderRuntime:
    """Build the tracked local provider composition deterministically."""
    runtime = ProviderRuntime(authorization=authorization)
    factory = ProviderFactory({
        "ollama.local": OllamaProvider,
    })
    runtime.restore(ProviderCatalog(catalog_path), factory, initialize=initialize)
    return runtime
