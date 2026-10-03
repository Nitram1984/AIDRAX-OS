#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

python3 -m py_compile "$ROOT/app/app.py"

test -f "$ROOT/app/templates/index.html"
test -f "$ROOT/app/static/style.css"

echo "AO-028C-01 VALIDATION: GREEN"
