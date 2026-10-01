# AIDRAX OS — AO-011 Supply-Chain Lock

AO-011 akzeptiert nur ein vom Owner vorgelegtes, vollständig pinndes Quellenmanifest und erzeugt daraus optional einen kanonischen Lock für AO-010. Es lädt keine Artefakte und prüft daher keine Signaturen gegen Netzwerkquellen; die benötigten Hashes und unabhängigen Prüfbelege müssen Bestandteil des Eingabemanifests sein.

```bash
python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 src/aidrax_supply_chain_lock/lock.py \
  --manifest /pfad/zu/approved-supply-input.json \
  --owner-gates /pfad/zu/owner-gates.json --dry-run
```

`--apply --output /neuer/pfad/approved-builder-lock.json` schreibt nur eine vorher nicht vorhandene Lock-Datei. Ein gültiger Lock enthält exakt das Ubuntu-24.04-Minimal-amd64-Ziel, den OCI-Image-Digest, den APT-Snapshot samt Release-Hash und hash-gebundene Versionen für `xorriso`, `squashfs-tools` sowie `grub-efi-amd64-bin`.

AO-011 ist keine Beschaffungs-, Vertrauensanker- oder Signatur-Engine. Die spätere, unabhängige Artefakt- und Signaturprüfung bleibt Owner-gated.
