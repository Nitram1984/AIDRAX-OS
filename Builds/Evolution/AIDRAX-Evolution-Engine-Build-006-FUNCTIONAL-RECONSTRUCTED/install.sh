#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
DST="$HOME/AIDRAX/Evolution-Engine-Build-006"
mkdir -p "$HOME/AIDRAX" "$HOME/.config/systemd/user"
rm -rf "$DST"
cp -a "$SRC" "$DST"
cp "$DST/systemd/aidrax-evolution.service" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now aidrax-evolution.service
sleep 1
echo
echo "=== HEALTH ==="
curl -s http://127.0.0.1:18321/health || true
echo
echo "=== OWNER TOKEN ==="
python3 -m aidrax_evolution owner-token
echo
echo "Dashboard: http://127.0.0.1:18321/dashboard/"
