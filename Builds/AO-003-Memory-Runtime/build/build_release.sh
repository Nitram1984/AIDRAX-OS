#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '\r\n' < "$ROOT/VERSION")"
STAGE="$ROOT/dist/stage/AIDRAX-OS-$VERSION"
"$ROOT/build/verify_release.sh"
rm -rf "$STAGE"
mkdir -p "$STAGE"
for entry in README.md CHANGELOG.md VERSION manifest.json build docs src tests; do cp -a "$ROOT/$entry" "$STAGE/"; done
find "$STAGE" -type d -name __pycache__ -prune -exec rm -rf {} +
python3 "$ROOT/build/manifest.py" > "$STAGE/release-manifest.json"
printf 'Staged release: %s\n' "$STAGE"
