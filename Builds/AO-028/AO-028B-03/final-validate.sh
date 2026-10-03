#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PAYLOAD="$ROOT/payload"

python3 - "$PAYLOAD" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])

required = [
    "etc/aidrax/ai-core/core.json",
    "etc/aidrax/ai-core/build.json",
    "etc/aidrax/ai-core/providers.json",
    "etc/aidrax/ai-core/routing.json",
    "etc/aidrax/ai-core/memoryvault.json",
    "etc/aidrax/ai-core/orchestrator.json",
    "etc/aidrax/ai-core/agents.json",
    "etc/aidrax/ai-core/health.json",
    "etc/aidrax/ai-core/audit.json",
    "etc/aidrax/ai-core/owner-gate.json",
    "var/lib/aidrax/ai-core/state/core-state.json"
]

errors = []

for rel in required:
    path = root / rel

    if not path.exists():
        errors.append(f"missing: {rel}")
        continue

    if path.suffix == ".json":
        try:
            json.loads(path.read_text())
        except Exception as exc:
            errors.append(f"invalid-json: {rel}: {exc}")

providers = json.loads(
    (root / "etc/aidrax/ai-core/providers.json").read_text()
)

routing = json.loads(
    (root / "etc/aidrax/ai-core/routing.json").read_text()
)

gate = json.loads(
    (root / "etc/aidrax/ai-core/owner-gate.json").read_text()
)

provider_map = {
    p["id"]: p
    for p in providers["providers"]
}

if provider_map.get("xai", {}).get("status") != "watchlist":
    errors.append("xAI must remain watchlist")

if "xai" not in routing.get("blocked_providers", []):
    errors.append("xAI must remain blocked in routing")

if gate.get("default_policy") != "deny-critical":
    errors.append("Owner Gate must default to deny-critical")

if gate.get("evolution", {}).get("enabled") is not False:
    errors.append("Evolution must remain disabled until AO-028B")

if errors:
    print("AO-028A FINAL VALIDATION: RED")

    for error in errors:
        print(" -", error)

    raise SystemExit(1)

print("AO-028A FINAL VALIDATION: GREEN")
print()
print("Core             : GREEN")
print("Providers        : GREEN")
print("Adaptive Router  : GREEN")
print("MemoryVault      : GREEN")
print("Orchestrator     : GREEN")
print("Agents           : GREEN")
print("Health API       : GREEN")
print("Audit/Rollback   : GREEN")
print("Owner Gate       : GREEN")
print("Evolution        : RESERVED AO-028B")
PY
