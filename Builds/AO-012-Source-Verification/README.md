# AIDRAX OS — AO-012 Source Verification

AO-012 prüft lokale, bereits beschaffte Quellen gegen einen kanonischen AO-011-Lock. Es lädt nichts nach, löst keine URLs auf und importiert keine Schlüssel. Der Artefaktindex referenziert ausschließlich reguläre Dateien relativ zu einem expliziten Artefaktwurzelpfad; Symlinks und Pfadausbrüche werden blockiert.

```bash
PYTHONPATH=src python3 src/aidrax_source_verification/verify.py \
  --lock /pfad/zu/approved-builder-lock.json \
  --artifact-root /pfad/zu/verified-sources \
  --artifact-index /pfad/zu/artifact-index.json \
  --owner-gates /pfad/zu/owner-gates.json
```

Der Index benötigt `base_image_manifest`, `apt_release` sowie je einen Eintrag für `xorriso`, `squashfs-tools` und `grub-efi-amd64-bin`. `VERIFIED` entsteht nur mit bytegenauen Hash-Treffern und den Owner-Gates `verify_local_sources` sowie `review_verification_report`.
