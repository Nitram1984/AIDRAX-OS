#!/usr/bin/env bash
set -euo pipefail

BASE="/var/lib/aidrax/inventory"
BIN="/usr/local/sbin/aidrax-hw-dashboard-export"

cat > "$BIN" <<'PY'
#!/usr/bin/env python3

import json
import socket
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/var/lib/aidrax/inventory")
INVENTORY = BASE / "latest.json"
HEALTH = BASE / "health.json"
MESH = BASE / "mesh-node.json"
OUT = BASE / "dashboard.json"

def load(path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}

inventory = load(INVENTORY)
health = load(HEALTH)
mesh = load(MESH)

checks = {
    x.get("name"): x
    for x in health.get("checks", [])
}

def status(name):
    return checks.get(name, {}).get("status", "UNKNOWN")

def message(name):
    return checks.get(name, {}).get("message", "No data")

payload = {
    "schema_version": "1.0",
    "module": "AO-029D",
    "component": "hardware_firmware_inventory",
    "generated_at": datetime.now(timezone.utc).isoformat(),

    "node": {
        "hostname": socket.gethostname(),
        "role": mesh.get("node", {}).get("role", "AM"),
        "model": inventory.get("system", {}).get(
            "system_version", "unknown"
        ),
        "product": inventory.get("system", {}).get(
            "product_name", "unknown"
        ),
        "kernel": inventory.get("node", {}).get(
            "kernel", "unknown"
        )
    },

    "summary": {
        "status": health.get("overall_status", "UNKNOWN"),
        "bios": status("bios"),
        "tpm": status("tpm"),
        "secure_boot": status("secure_boot"),
        "fingerprint": status("fingerprint"),
        "firmware": status("firmware_history")
    },

    "firmware": {
        "bios_vendor": inventory.get("bios", {}).get(
            "vendor", "unknown"
        ),
        "bios_version": inventory.get("bios", {}).get(
            "version", "unknown"
        ),
        "bios_release_date": inventory.get("bios", {}).get(
            "release_date", "unknown"
        )
    },

    "cards": [
        {
            "id": "bios",
            "title": "BIOS / UEFI",
            "status": status("bios"),
            "value": inventory.get("bios", {}).get(
                "version", "unknown"
            ),
            "detail": message("bios")
        },
        {
            "id": "tpm",
            "title": "TPM",
            "status": status("tpm"),
            "value": inventory.get("security", {}).get(
                "tpm", "unknown"
            ),
            "detail": message("tpm")
        },
        {
            "id": "secure_boot",
            "title": "Secure Boot",
            "status": status("secure_boot"),
            "value": inventory.get("security", {}).get(
                "secure_boot", "unknown"
            ),
            "detail": message("secure_boot")
        },
        {
            "id": "fingerprint",
            "title": "Fingerprint",
            "status": status("fingerprint"),
            "value": "not detected"
                if status("fingerprint") == "YELLOW"
                else "detected",
            "detail": message("fingerprint")
        },
        {
            "id": "firmware",
            "title": "Firmware",
            "status": status("firmware_history"),
            "value": status("firmware_history"),
            "detail": message("firmware_history")
        }
    ]
}

tmp = OUT.with_suffix(".json.tmp")
tmp.write_text(
    json.dumps(payload, indent=2, ensure_ascii=False)
)
tmp.replace(OUT)

print(f"AO-029D: {payload['summary']['status']}")
print(f"Dashboard payload: {OUT}")
print(f"Cards: {len(payload['cards'])}")
PY

chmod 0755 "$BIN"

echo "=== AO-029D EXPORT ==="
"$BIN"

echo
echo "=== VALIDATION ==="
python3 -m json.tool "$BASE/dashboard.json" >/dev/null
echo "JSON: VALID"

echo
echo "=== SUMMARY ==="
python3 - <<'PY'
import json
p="/var/lib/aidrax/inventory/dashboard.json"
d=json.load(open(p))

print("Node:", d["node"]["hostname"])
print("Status:", d["summary"]["status"])

for c in d["cards"]:
    print(
        f'{c["status"]:7} '
        f'{c["title"]}: '
        f'{c["value"]}'
    )
PY
