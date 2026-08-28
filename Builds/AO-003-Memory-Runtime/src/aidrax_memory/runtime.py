"""Append-only local memory with explicit durable state."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Protocol
from uuid import uuid4

_NAME = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$")
class RegistryAdapter(Protocol):
    def add(self, component: dict[str, object]) -> None: ...
class EventBusAdapter(Protocol):
    def publish(self, event: str, payload: dict[str, object]) -> None: ...
class MemoryRuntimeError(ValueError): pass

@dataclass(frozen=True, slots=True)
class MemoryEntry:
    entry_id: str
    namespace: str
    content: str
    tags: tuple[str, ...]
    created_at: str
    def audit_record(self) -> dict[str, object]:
        return {"entry_id": self.entry_id, "namespace": self.namespace, "tags": list(self.tags)}

class MemoryRuntime:
    COMPONENT_ID = "aidrax.memory.runtime"
    def __init__(self, journal_path: str | Path, registry: RegistryAdapter, events: EventBusAdapter) -> None:
        self._path, self._registry, self._events = Path(journal_path), registry, events
        self._entries: dict[str, MemoryEntry] = {}
    def start(self) -> None:
        self._restore()
        self._registry.add({"id": self.COMPONENT_ID, "status": "READY", "health": "HEALTHY"})
        self._emit("memory.runtime_ready", {"component_id": self.COMPONENT_ID, "active_entries": len(self._entries)})
    def remember(self, namespace: str, content: str, tags: tuple[str, ...] = ()) -> MemoryEntry:
        self._validate_name(namespace, "namespace")
        if not isinstance(content, str) or not content.strip(): raise MemoryRuntimeError("content must be non-empty")
        if len(content) > 16384: raise MemoryRuntimeError("content exceeds local entry limit")
        if any(not isinstance(tag, str) or not _NAME.fullmatch(tag) for tag in tags): raise MemoryRuntimeError("tags must be lowercase identifiers")
        entry = MemoryEntry(str(uuid4()), namespace, content, tuple(sorted(set(tags))), datetime.now(timezone.utc).isoformat())
        self._append({"kind": "entry", **asdict(entry)}); self._entries[entry.entry_id] = entry
        self._emit("memory.entry_recorded", entry.audit_record()); return entry
    def recall(self, namespace: str, query: str = "") -> tuple[MemoryEntry, ...]:
        self._validate_name(namespace, "namespace"); needle = query.casefold().strip()
        return tuple(entry for entry in self._entries.values() if entry.namespace == namespace and (not needle or needle in entry.content.casefold()))
    def forget(self, entry_id: str) -> None:
        if entry_id not in self._entries: raise MemoryRuntimeError("unknown or already forgotten entry")
        self._append({"kind": "tombstone", "entry_id": entry_id, "at": datetime.now(timezone.utc).isoformat()})
        entry = self._entries.pop(entry_id); self._emit("memory.entry_forgotten", entry.audit_record())
    def _restore(self) -> None:
        if not self._path.exists(): return
        for line in self._path.read_text(encoding="utf-8").splitlines():
            try: record = json.loads(line)
            except json.JSONDecodeError as error: raise MemoryRuntimeError("journal contains invalid JSON") from error
            if record.get("kind") == "entry":
                entry = MemoryEntry(record["entry_id"], record["namespace"], record["content"], tuple(record["tags"]), record["created_at"]); self._entries[entry.entry_id] = entry
            elif record.get("kind") == "tombstone": self._entries.pop(record.get("entry_id"), None)
            else: raise MemoryRuntimeError("journal has unknown record kind")
    def _append(self, record: dict[str, object]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as journal: journal.write(json.dumps(record, sort_keys=True) + "\n")
    def _emit(self, event: str, payload: dict[str, object]) -> None: self._events.publish(event, payload)
    @staticmethod
    def _validate_name(value: str, label: str) -> None:
        if not isinstance(value, str) or not _NAME.fullmatch(value): raise MemoryRuntimeError(f"{label} must be a lowercase dotted identifier")
