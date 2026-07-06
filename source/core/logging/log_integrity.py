from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Any


def verify_log_file(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return {"status": "YELLOW", "message": "log file missing", "file": str(path)}

    checked = 0
    invalid = 0
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            checked += 1
            try:
                entry = json.loads(line)
                expected = entry.pop("integrity", None)
                payload = json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")
                actual = hashlib.sha256(payload).hexdigest()
                if expected != actual:
                    invalid += 1
            except Exception:
                invalid += 1

    return {
        "status": "GREEN" if invalid == 0 else "RED",
        "file": str(path),
        "checked": checked,
        "invalid": invalid,
    }
