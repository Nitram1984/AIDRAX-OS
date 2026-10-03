#!/usr/bin/env bash
set -u

OUTDIR="/var/lib/aidrax/inventory"
TMPDIR="$(mktemp -d)"
HOST="$(hostname)"
TS="$(date --iso-8601=seconds)"

cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

mkdir -p "$TMPDIR"

dmidecode -t system > "$TMPDIR/dmi-system.txt" 2>/dev/null || true
dmidecode -t bios > "$TMPDIR/dmi-bios.txt" 2>/dev/null || true
fwupdmgr get-devices > "$TMPDIR/fwupd-devices.txt" 2>/dev/null || true
fwupdmgr get-updates > "$TMPDIR/fwupd-updates.txt" 2>/dev/null || true
lsusb > "$TMPDIR/lsusb.txt" 2>/dev/null || true
lspci -nnk > "$TMPDIR/lspci.txt" 2>/dev/null || true
lsblk -J -o NAME,TYPE,SIZE,FSTYPE,MODEL,SERIAL,TRAN,MOUNTPOINTS > "$TMPDIR/lsblk.json" 2>/dev/null || true

BIOS_VENDOR="$(dmidecode -s bios-vendor 2>/dev/null || true)"
BIOS_VERSION="$(dmidecode -s bios-version 2>/dev/null || true)"
BIOS_DATE="$(dmidecode -s bios-release-date 2>/dev/null || true)"
SYS_VENDOR="$(dmidecode -s system-manufacturer 2>/dev/null || true)"
SYS_PRODUCT="$(dmidecode -s system-product-name 2>/dev/null || true)"
SYS_VERSION="$(dmidecode -s system-version 2>/dev/null || true)"
KERNEL="$(uname -r)"
ARCH="$(uname -m)"

SECUREBOOT="unknown"
if command -v mokutil >/dev/null 2>&1; then
  SECUREBOOT="$(mokutil --sb-state 2>/dev/null | tr '\n' ' ' | sed 's/[[:space:]]*$//')"
fi

TPM="absent"
if [ -e /dev/tpm0 ] || [ -e /dev/tpmrm0 ]; then
  TPM="present"
fi

python3 - <<PY
import json
from pathlib import Path

def read(path):
    p = Path(path)
    return p.read_text(errors="replace") if p.exists() else ""

data = {
    "schema_version": "1.0",
    "collector": "AO-029A",
    "timestamp": ${TS@Q},
    "node": {
        "hostname": ${HOST@Q},
        "architecture": ${ARCH@Q},
        "kernel": ${KERNEL@Q},
    },
    "system": {
        "manufacturer": ${SYS_VENDOR@Q},
        "product_name": ${SYS_PRODUCT@Q},
        "version": ${SYS_VERSION@Q},
    },
    "bios": {
        "vendor": ${BIOS_VENDOR@Q},
        "version": ${BIOS_VERSION@Q},
        "release_date": ${BIOS_DATE@Q},
    },
    "security": {
        "secure_boot": ${SECUREBOOT@Q},
        "tpm": ${TPM@Q},
    },
    "raw": {
        "fwupd_devices": read("$TMPDIR/fwupd-devices.txt"),
        "fwupd_updates": read("$TMPDIR/fwupd-updates.txt"),
        "usb": read("$TMPDIR/lsusb.txt"),
        "pci": read("$TMPDIR/lspci.txt"),
    }
}

try:
    data["storage"] = json.loads(read("$TMPDIR/lsblk.json"))
except Exception:
    data["storage"] = {}

Path("$TMPDIR/latest.json").write_text(
    json.dumps(data, indent=2, ensure_ascii=False)
)
PY

echo
echo "=== AO-029A PREVIEW ==="
cat "$TMPDIR/latest.json"

echo
echo "=== VALIDATION ==="
python3 -m json.tool "$TMPDIR/latest.json" >/dev/null \
  && echo "JSON: VALID" \
  || echo "JSON: INVALID"

echo
echo "Collector test complete."
echo "No persistent system changes were made."
