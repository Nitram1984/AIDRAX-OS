#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 - "$root" <<'PY'
import json
import pathlib
import py_compile
import sys

root = pathlib.Path(sys.argv[1])
manifest = json.loads((root / "manifest.json").read_text())
missing = [name for name in manifest["required_paths"] if not (root / name).is_file()]
if missing:
    raise SystemExit("missing manifest paths: " + ", ".join(missing))
config = json.loads((root / "config/desktop-closure.json").read_text())
required = {"sddm", "xserver-xorg", "xserver-xorg-video-vesa", "openbox", "python3-tk"}
if not required.issubset(config["requested_packages"]):
    raise SystemExit("desktop package contract incomplete")
if "host_package_install" not in config["prohibited_actions"]:
    raise SystemExit("host package installation must remain prohibited")
py_compile.compile(str(root / "desktop/aidrax-dashboard.py"), doraise=True)
launcher = root / "desktop/aidrax-xorg-launch"
if not launcher.read_text().endswith('exec /usr/lib/xorg/Xorg "$@"\n'):
    raise SystemExit("SDDM Xorg launcher contract is incomplete")
pet = json.loads((root / "desktop/pets/aidrax-draco-standard/pet.json").read_text())
if pet.get("spriteVersionNumber") != 2 or pet.get("spritesheetPath") != "spritesheet.webp":
    raise SystemExit("Draco v2 pet contract is incomplete")
print("AO-025_STRUCTURAL_GREEN")
PY
