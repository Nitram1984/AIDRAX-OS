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
    "etc/aidrax/ai-core/evolution.json",
    "etc/aidrax/ai-core/scoring.json",
    "etc/aidrax/ai-core/skill-learning.json",
    "etc/aidrax/ai-core/proposals.json",
    "etc/aidrax/ai-core/sandbox.json",
    "etc/aidrax/ai-core/self-healing.json",
    "etc/aidrax/ai-core/local-learning.json",
    "etc/aidrax/ai-core/evolution-controller.json",
    "etc/aidrax/ai-core/owner-gate.json"
]

errors = []

for rel in required:
    path = root / rel

    if not path.exists():
        errors.append(f"missing: {rel}")
        continue

    try:
        json.loads(path.read_text())
    except Exception as exc:
        errors.append(f"invalid-json: {rel}: {exc}")

controller = json.loads(
    (root / "etc/aidrax/ai-core/evolution-controller.json").read_text()
)

learning = json.loads(
    (root / "etc/aidrax/ai-core/local-learning.json").read_text()
)

healing = json.loads(
    (root / "etc/aidrax/ai-core/self-healing.json").read_text()
)

if controller.get("autonomous_production_deploy") is not False:
    errors.append("autonomous production deployment must remain disabled")

if learning.get("training_enabled") is not False:
    errors.append("local model training must remain disabled")

if healing.get("auto_repair") is not False:
    errors.append("automatic repair must remain disabled")

if errors:
    print("AO-028B FINAL VALIDATION: RED")
    for error in errors:
        print(" -", error)
    raise SystemExit(1)

print("AO-028B FINAL VALIDATION: GREEN")
print()
print("Observation       : GREEN")
print("Quality Scoring   : GREEN")
print("Skill Learning    : GREEN")
print("Proposal Engine   : GREEN")
print("Sandbox           : GREEN")
print("Self-Healing      : GREEN")
print("Learning Pipeline : GREEN")
print("Owner Gate        : GREEN")
print("Auto Deploy       : DISABLED")
print("Model Training    : DISABLED")
PY
