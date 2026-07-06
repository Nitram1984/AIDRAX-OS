from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "SECURITY", "AUDIT", "PRIVACY"}
ROUTE_FILES = {
    "SECURITY": "security.log",
    "AUDIT": "audit.log",
    "PRIVACY": "privacy.log",
}


class EnterpriseLogger:
    """AIDRAX OS enterprise logging foundation.

    Writes JSON-lines logs into logs/runtime.log plus separated security,
    audit and privacy streams. This is a foundation component, not a daemon.
    """

    def __init__(self, log_root: str | Path = "logs", max_bytes: int = 1_000_000):
        self.log_root = Path(log_root)
        self.max_bytes = max_bytes
        self.log_root.mkdir(parents=True, exist_ok=True)
        (self.log_root / "modules").mkdir(parents=True, exist_ok=True)
        (self.log_root / "archive").mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _target_file(self, level: str, component: str) -> Path:
        if component.startswith("module:"):
            safe = component.split(":", 1)[1].replace("/", "_").replace("..", "_")
            return self.log_root / "modules" / f"{safe}.log"
        return self.log_root / ROUTE_FILES.get(level, "runtime.log")

    def _rotate_if_needed(self, path: Path) -> None:
        if path.exists() and path.stat().st_size >= self.max_bytes:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            archive = self.log_root / "archive" / f"{path.stem}_{stamp}{path.suffix}"
            path.rename(archive)

    def _hash_entry(self, entry: Dict[str, Any]) -> str:
        payload = json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def log(self, level: str, message: str, component: str = "core", extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        level = level.upper().strip()
        if level not in VALID_LEVELS:
            raise ValueError(f"Unsupported log level: {level}")

        entry: Dict[str, Any] = {
            "timestamp": self._now(),
            "level": level,
            "component": component,
            "message": message,
            "extra": extra or {},
        }
        entry["integrity"] = self._hash_entry(entry)

        path = self._target_file(level, component)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._rotate_if_needed(path)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def health(self) -> Dict[str, Any]:
        return {
            "status": "GREEN",
            "component": "enterprise_logger",
            "log_root": str(self.log_root),
            "streams": ["runtime", "security", "audit", "privacy", "modules", "archive"],
        }
