# AIDRAX OS — AO-009 ISO Builder Environment

AO-009 bereitet eine reproduzierbare, isolierte Ubuntu-24.04-LTS-Minimal-amd64-Builder-Umgebung und die Boot-Testmatrix vor. Es erzeugt oder startet keinen Container/Builder und erstellt keine ISO, Testmedien, Schlüssel oder MOK-Einträge.

Der maschinenlesbare Vertrag verlangt einen immutablen Base-Image-Digest, eine APT-Snapshot-Quelle, Paket-Lockdatei und `SOURCE_DATE_EPOCH`, bevor ein späterer Builder als `READY` gelten kann. Ohne die drei Owner-Gates ist das sichere Resultat `BLOCKED`.

```bash
PYTHONPATH=src python3 src/aidrax_iso_builder_environment/preflight.py --report build-output/builder-preflight.json
python3 -m unittest discover -s tests -v
python3 build/verify_release.py
python3 build/build_release.py
python3 build/verify_release.py --archive build-output/AO-009-ISO-Builder-Environment.zip
(cd build-output && sha256sum -c AO-009-ISO-Builder-Environment.zip.sha256)
```

Eine spätere Gate-Datei ist ein lokales JSON-Objekt mit `builder_environment`, `package_source_lock` und `boot_test_preparation`, jeweils Boolean `true`. Sie autorisiert ausschließlich die Planungsentscheidung, keine Ausführung.
