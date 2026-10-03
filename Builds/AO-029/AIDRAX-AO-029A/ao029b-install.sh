#!/usr/bin/env bash
set -euo pipefail

BASE="/var/lib/aidrax/inventory"
ETC="/etc/aidrax/hardware"
BIN="/usr/local/sbin/aidrax-hw-health"

install -d -m 0755 "$BASE"
install -d -m 0755 "$ETC"

cat > "$ETC/expectations.json" <<'JSON'
{
  "schema_version": "1.0",
  "node": "AM",
  "expectations": {
    "tpm_required": true,
    "fingerprint_expected": true,
    "secure_boot_required": false
  }
}
JSON

chmod 0644 "$ETC/expectations.json"

cat > "$BIN" <<'PY'
#!/usr/bin/env python3

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/var/lib/aidrax/inventory")
LATEST = BASE / "latest.json"
HEALTH = BASE / "health.json"
EXPECT = Path("/etc/aidrax/hardware/expectations.json")

SEVERITY = {
    "GREEN": 0,
    "YELLOW": 1,
    "RED": 2
}

def load_json(path):
    try:
        return json.loads(path.read_text())
    except Exception as e:
        print(f"ERROR: cannot read {path}: {e}", file=sys.stderr)
        sys.exit(2)

def add_check(checks, name, status, message, evidence=None):
    item = {
        "name": name,
        "status": status,
        "message": message
    }
    if evidence:
        item["evidence"] = evidence
    checks.append(item)

inventory = load_json(LATEST)
expectations = load_json(EXPECT)

checks = []

# ------------------------------------------------------------
# Inventory integrity
# ------------------------------------------------------------
schema = inventory.get("schema_version")

if schema == "1.0":
    add_check(
        checks,
        "inventory_schema",
        "GREEN",
        "Inventory schema valid",
        schema
    )
else:
    add_check(
        checks,
        "inventory_schema",
        "RED",
        "Unexpected or missing inventory schema",
        str(schema)
    )

# ------------------------------------------------------------
# TPM
# ------------------------------------------------------------
tpm = inventory.get("security", {}).get("tpm", "unknown")
tpm_required = expectations.get("expectations", {}).get(
    "tpm_required", False
)

if tpm == "present":
    add_check(
        checks,
        "tpm",
        "GREEN",
        "TPM detected"
    )
elif tpm_required:
    add_check(
        checks,
        "tpm",
        "RED",
        "TPM required but not detected"
    )
else:
    add_check(
        checks,
        "tpm",
        "YELLOW",
        "TPM not detected"
    )

# ------------------------------------------------------------
# Secure Boot
# ------------------------------------------------------------
secure_boot = inventory.get(
    "security", {}
).get("secure_boot", "unknown")

secure_boot_required = expectations.get(
    "expectations", {}
).get("secure_boot_required", False)

secure_lower = str(secure_boot).lower()

if "enabled" in secure_lower:
    add_check(
        checks,
        "secure_boot",
        "GREEN",
        "Secure Boot enabled",
        secure_boot
    )

elif "disabled" in secure_lower:
    status = "RED" if secure_boot_required else "YELLOW"

    add_check(
        checks,
        "secure_boot",
        status,
        "Secure Boot disabled",
        secure_boot
    )

else:
    add_check(
        checks,
        "secure_boot",
        "YELLOW",
        "Secure Boot state unknown",
        secure_boot
    )

# ------------------------------------------------------------
# Fingerprint
# ------------------------------------------------------------
usb_text = inventory.get("raw", {}).get("usb", "")
pci_text = inventory.get("raw", {}).get("pci", "")

fingerprint_patterns = [
    r"fingerprint",
    r"biometric",
    r"validity",
    r"06cb:",
    r"138a:"
]

fingerprint_detected = any(
    re.search(pattern, usb_text, re.IGNORECASE)
    or re.search(pattern, pci_text, re.IGNORECASE)
    for pattern in fingerprint_patterns
)

fingerprint_expected = expectations.get(
    "expectations", {}
).get("fingerprint_expected", False)

if fingerprint_detected:
    add_check(
        checks,
        "fingerprint",
        "GREEN",
        "Fingerprint hardware detected"
    )

elif fingerprint_expected:
    add_check(
        checks,
        "fingerprint",
        "YELLOW",
        "Fingerprint hardware expected but not detected by OS"
    )

else:
    add_check(
        checks,
        "fingerprint",
        "GREEN",
        "No fingerprint requirement configured"
    )

# ------------------------------------------------------------
# fwupd status
# ------------------------------------------------------------
fwupd_devices = inventory.get(
    "raw", {}
).get("fwupd_devices", "")

failure_patterns = [
    r"nicht korrekt aktualisierte geräte",
    r"updateerror",
    r"failed to run update",
    r"aktualisierungsfehler",
    r"failed"
]

fwupd_failure = any(
    re.search(pattern, fwupd_devices, re.IGNORECASE)
    for pattern in failure_patterns
)

if fwupd_failure:
    add_check(
        checks,
        "firmware_history",
        "YELLOW",
        "Firmware update history contains a failure or warning"
    )
else:
    add_check(
        checks,
        "firmware_history",
        "GREEN",
        "No firmware failure detected in current inventory"
    )

# ------------------------------------------------------------
# BIOS basic presence
# ------------------------------------------------------------
bios_version = inventory.get("bios", {}).get("version", "")

if bios_version:
    add_check(
        checks,
        "bios",
        "GREEN",
        "BIOS version detected",
        bios_version
    )
else:
    add_check(
        checks,
        "bios",
        "RED",
        "BIOS version unavailable"
    )

# ------------------------------------------------------------
# Overall status
# ------------------------------------------------------------
overall = "GREEN"

for check in checks:
    if SEVERITY[check["status"]] > SEVERITY[overall]:
        overall = check["status"]

result = {
    "schema_version": "1.0",
    "module": "AO-029B",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "node": inventory.get("node", {}).get("hostname", "unknown"),
    "overall_status": overall,
    "checks": checks
}

tmp = HEALTH.with_suffix(".json.tmp")

tmp.write_text(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
)

tmp.replace(HEALTH)

print(f"AO-029B: {overall}")
print(f"Health: {HEALTH}")

for check in checks:
    print(
        f"{check['status']:6} "
        f"{check['name']}: "
        f"{check['message']}"
    )
PY

chmod 0755 "$BIN"

echo "=== AO-029B INSTALL ==="
"$BIN"

echo
echo "=== JSON VALIDATION ==="
python3 -m json.tool "$BASE/health.json" >/dev/null
echo "JSON: VALID"

echo
echo "=== HEALTH FILE ==="
ls -lh "$BASE/health.json"
