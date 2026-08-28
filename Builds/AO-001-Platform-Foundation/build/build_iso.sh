#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f "$ROOT/installer/iso-builder-contract.json" ]]; then
  echo "AO-001 ISO gate: NOT BUILT. An approved ISO builder contract is required; see docs/ISO-ROADMAP.md." >&2
  exit 2
fi
printf 'ISO builder contract detected; implementation belongs to AO-007.\n'
