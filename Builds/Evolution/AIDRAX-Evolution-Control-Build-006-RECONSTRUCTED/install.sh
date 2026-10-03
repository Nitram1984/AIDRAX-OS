#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
DST="$HOME/AIDRAX/Evolution-Control-Build-006"
mkdir -p "$HOME/AIDRAX" "$HOME/.config/systemd/user"
rm -rf "$DST"; cp -a "$SRC" "$DST"
cp "$DST/systemd/aidrax-evolution.service" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now aidrax-evolution.service
echo "Open: http://127.0.0.1:18321/dashboard/"
