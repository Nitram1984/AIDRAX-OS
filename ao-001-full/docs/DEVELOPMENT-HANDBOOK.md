# Entwicklungshandbuch

1. In einem separaten Arbeitsverzeichnis entpacken und `python3 build/verify_release.py` ausführen.
2. Nur über dokumentierte Contracts an ATLAS, HERMES und `CapabilityRuntime` anbinden.
3. Für jede Zustandsänderung Unit-, Fehler- und Recovery-Tests ergänzen.
4. Geheimnisse weder in JSON, Logs, Manifeste noch Testfixtures schreiben.
5. Vor Integration: `installer/install.sh --dry-run --target …`, Diff-Prüfung, Owner-Freigabe und danach `--apply`.

Die Runtime-Modelle hier sind absichtlich in-process und seiteneffektfrei. Sie sind kein Ersatz für den kanonischen CapabilityRuntime.
