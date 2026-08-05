#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

python3 -m compileall -q src tests
python3 -m pytest -q

printf '%s\n' "GREEN: CA-011R1 ARGUS validation passed."
