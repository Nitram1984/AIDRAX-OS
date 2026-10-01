#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; VERSION="$(tr -d '\r\n' < "$ROOT/VERSION")"; STAGE="$ROOT/dist/stage/AIDRAX-OS-$VERSION"; ARCHIVE="$ROOT/dist/AIDRAX-OS-$VERSION.zip"
[[ -d "$STAGE" ]] || "$ROOT/build/build_release.sh"; mkdir -p "$ROOT/dist"; rm -f "$ARCHIVE" "$ARCHIVE.sha256"
(cd "$(dirname "$STAGE")" && zip -qr "$ARCHIVE" "$(basename "$STAGE")")
(cd "$ROOT/dist" && sha256sum "$(basename "$ARCHIVE")" > "$(basename "$ARCHIVE").sha256")
printf 'Package: %s\n' "$ARCHIVE"
