from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .errors import ProviderRegistrationError


@dataclass(frozen=True, slots=True)
class ProviderBinding:
    provider_id: str
    creator: str


class ProviderCatalog:
    """Small durable binding catalog for restart-safe explicit provider composition."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> tuple[ProviderBinding, ...]:
        if not self.path.exists():
            return ()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ProviderRegistrationError("provider catalog is unreadable") from error
        if not isinstance(raw, list):
            raise ProviderRegistrationError("provider catalog must contain a JSON array")
        bindings = []
        seen = set()
        for item in raw:
            if not isinstance(item, dict) or set(item) != {"id", "creator"}:
                raise ProviderRegistrationError("provider catalog entry must contain exactly id and creator")
            pid, creator = item["id"], item["creator"]
            if not isinstance(pid, str) or not pid or not isinstance(creator, str) or not creator:
                raise ProviderRegistrationError("provider catalog id and creator must be non-empty strings")
            if pid in seen:
                raise ProviderRegistrationError(f"duplicate provider id in catalog: {pid}")
            seen.add(pid)
            bindings.append(ProviderBinding(pid, creator))
        return tuple(sorted(bindings, key=lambda item: item.provider_id))

    def save(self, bindings: tuple[ProviderBinding, ...]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [{"id": item.provider_id, "creator": item.creator} for item in sorted(bindings, key=lambda x: x.provider_id)]
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.path)
