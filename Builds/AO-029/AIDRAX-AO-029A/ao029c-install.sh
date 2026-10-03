#!/usr/bin/env bash
set -euo pipefail

BASE="/var/lib/aidrax/inventory"
BIN="/usr/local/sbin/aidrax-hw-mesh-export"

cat > "$BIN" <<'PY'
#!/usr/bin/env python3

import json
import socket
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/var/lib/aidrax/inventory")
INVENTORY = BASE / "latest.json"
HEALTH = BASE / "health.json"
OUT = BASE / "mesh-node.json"

def load(path):
    return json.loads(path.read_text())

inventory = load(INVENTORY)
health = load(HEALTH)

checks = {
    item["name"]: item["status"]
    for item in health.get("checks", [])
}

payload = {
    "schema_version": "1.0",
    "mesh_type": "aidrax.hardware-health",
    "module": "AO-029C",
    "node": {
        "hostname": socket.gethostname(),
        "role": "AM",
        "platform": inventory.get("system", {}).get("product_name", "unknown"),
        "system_version": inventory.get("system", {}).get("version", "unknown"),
        "kernel": inventory.get("node", {}).get("kernel", "unknown")
    },
    "status": {
        "overall": health.get("overall_status", "UNKNOWN"),
        "bios": checks.get("bios", "UNKNOWN"),
        "tpm": checks.get("tpm", "UNKNOWN"),
        "secure_boot": checks.get("secure_boot", "UNKNOWN"),
        "fingerprint": checks.get("fingerprint", "UNKNOWN"),
        "firmware_history": checks.get("firmware_history", "UNKNOWN")
    },
    "firmware": {
        "bios_vendor": inventory.get("bios", {}).get("vendor", "unknown"),
        "bios_version": inventory.get("bios", {}).get("version", "unknown"),
        "bios_release_date": inventory.get("bios", {}).get("release_date", "unknown")
    },
    "source": {
        "inventory": "/var/lib/aidrax/inventory/latest.json",
        "health": "/var/lib/aidrax/inventory/health.json"
    },
    "timestamp": datetime.now(timezone.utc).isoformat()
}

tmp = OUT.with_suffix(".json.tmp")
tmp.write_text(
    json.dumps(payload, indent=2, ensure_ascii=False)
)
tmp.replace(OUT)

print(f"AO-029C: {payload['status']['overall']}")
print(f"Node: {payload['node']['hostname']}")
print(f"Mesh payload: {OUT}")
PY

chmod 0755 "$BIN"

echo "=== AO-029C EXPORT ==="
"$BIN"

echo
echo "=== VALIDATION ==="
python3 -m json.tool "$BASE/mesh-node.json" >/dev/null
echo "JSON: VALID"

echo
echo "=== PAYLOAD ==="
cat "$BASE/mesh-node.json"
