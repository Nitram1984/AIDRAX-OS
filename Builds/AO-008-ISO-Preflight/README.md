# AIDRAX OS — AO-008 ISO Preflight

AO-008 ist die owner-gated, nicht-destruktive Entscheidungsvorstufe für eine spätere AIDRAX-OS-ISO. Es erzeugt **keine ISO** und führt keine Bootloader-, Firmware-, Datenträger- oder Secure-Boot-/MOK-Änderung aus.

Das Ziel ist verbindlich in `docs/ISO-TARGET-CONTRACT.json` definiert: Ubuntu 24.04 LTS Minimal amd64, UEFI-only, Secure Boot standardmäßig aktiv und ausschließlich signierte Ubuntu-/Microsoft-Bootkette. Zusätzliche Schlüssel erfordern eine aktuelle Owner-Freigabe und eine spätere manuelle MOK-Registrierung.

## Preflight ausführen

```bash
python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 src/aidrax_iso_preflight/preflight.py --report build-output/preflight-report.json
```

Ohne explizite Owner-Freigaben ist das erwartete Ergebnis `BLOCKED`. Eine Freigabedatei ist ein lokales JSON-Objekt mit ausschließlich den Boolean-Schlüsseln `iso_build`, `signing_procedure`, `mok_registration` und `hardware_boot_test`; fehlende oder `false`-Werte blockieren.

```bash
PYTHONPATH=src python3 src/aidrax_iso_preflight/preflight.py \
  --owner-gates /pfad/zu/owner-gates.json --report build-output/preflight-report.json
```

Der Bericht enthält keine Geheimnisse und meldet Architektur, UEFI-Policy, Toolchain, Arbeitsbereich, Key-Gate und Owner-Gates. `BLOCKED` ist ein gültiges, sicheres Resultat.

## Release-Artefakt

```bash
python3 build/verify_release.py
python3 build/build_release.py
python3 build/verify_release.py --archive build-output/AO-008-ISO-Preflight.zip
(cd build-output && sha256sum -c AO-008-ISO-Preflight.zip.sha256)
```

Der Build erzeugt ausschließlich ein ZIP, einen SHA-256-Nachweis und einen Datei-Manifestbericht in `build-output/`. Diese Artefakte sind von Git ausgeschlossen.
