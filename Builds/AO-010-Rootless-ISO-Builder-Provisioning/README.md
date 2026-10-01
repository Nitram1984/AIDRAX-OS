# AIDRAX OS — AO-010 Rootless ISO Builder Provisioning

AO-010 erzeugt nach nachweisbarer Owner-Freigabe einen **lokalen Build-Kontext** für einen späteren rootless Podman-ISO-Builder. Es startet keinen Container, zieht kein Image, installiert keine Pakete und erzeugt keine ISO.

Der Provisionierer verlangt einen konkreten, unveränderlichen Ubuntu-24.04-amd64-Image-Digest, eine HTTPS-APT-Snapshot-Quelle sowie eine Paket-Lockliste. Die Eingabedateien gehören außerhalb dieses Releases und enthalten keine Secrets.

```bash
python3 -m unittest discover -s tests -v
python3 build/verify_release.py
PYTHONPATH=src python3 src/aidrax_rootless_iso_builder/provision.py \
  --lock /pfad/zu/approved-builder-lock.json \
  --owner-gates /pfad/zu/owner-gates.json \
  --output-dir /tmp/ao-010-context --dry-run
```

`--apply` schreibt erst nach erfolgreicher Prüfung den Kontext in ein leeres Zielverzeichnis. Der ausgegebene Podman-Plan fordert `--network=none`, `--userns=keep-id`, `--security-opt=no-new-privileges`, keine Host-Mounts und keine Geräteweitergabe. Er ist deklarativ: seine spätere Ausführung benötigt einen separaten Owner-Gate.

```bash
python3 build/build_release.py
python3 build/verify_release.py --archive build-output/AO-010-Rootless-ISO-Builder-Provisioning.zip
(cd build-output && sha256sum -c AO-010-Rootless-ISO-Builder-Provisioning.zip.sha256)
```
