"""Secret resolution boundary for provider adapters.

Secrets are resolved at runtime only. They are never stored in manifests,
ATLAS records, HERMES events, provider catalogs, or diagnostic metadata.
"""

from __future__ import annotations

import os
import re
from typing import Protocol, runtime_checkable


@runtime_checkable
class SecretResolver(Protocol):
    """Resolve one provider secret without exposing persistence semantics."""

    def resolve(self, provider_id: str, secret_name: str) -> str | None:
        """Return a secret value or None when it is unavailable."""


class EnvironmentSecretResolver:
    """Read provider secrets from explicitly named environment variables."""

    def __init__(self, prefix: str = "AIDRAX_PROVIDER") -> None:
        self.prefix = _segment(prefix)

    def key(self, provider_id: str, secret_name: str) -> str:
        return f"{self.prefix}_{_segment(provider_id)}_{_segment(secret_name)}"

    def resolve(self, provider_id: str, secret_name: str) -> str | None:
        value = os.environ.get(self.key(provider_id, secret_name))
        return value if value else None


def _segment(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("secret identifier segments must be non-empty strings")
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").upper()
    if not normalized:
        raise ValueError("secret identifier segment cannot be normalized")
    return normalized


__all__ = ["EnvironmentSecretResolver", "SecretResolver"]
