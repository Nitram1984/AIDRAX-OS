"""Non-executing AO-023 boot-entry contract."""
from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True)
class BootEntry:
    name: str
    persistent_storage: str
    next_surface: str

class BootContract:
    def __init__(self, payload: Mapping[str, object]):
        if payload.get("schema_version") != 1 or payload.get("default_entry") != "live-desktop":
            raise ValueError("AO-023 must default to live-desktop")
        entries = payload.get("entries")
        if not isinstance(entries, dict) or set(entries) != {"live-desktop", "install", "recovery"}:
            raise ValueError("AO-023 requires exactly live-desktop, install, and recovery entries")
        self._entries = {name: BootEntry(name, item["persistent_storage"], item["next_surface"]) for name, item in entries.items() if isinstance(item, dict)}
        if len(self._entries) != 3 or self._entries["live-desktop"].persistent_storage != "unchanged":
            raise ValueError("live desktop must preserve persistent storage")
        if self._entries["install"].persistent_storage != "owner-gated":
            raise ValueError("installation must remain owner-gated")
    def entry(self, name: str) -> BootEntry:
        try: return self._entries[name]
        except KeyError as error: raise ValueError("unknown boot entry") from error
