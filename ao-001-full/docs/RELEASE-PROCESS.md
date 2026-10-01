# Release-Prozess

1. Sauberen Paketstand prüfen: `python3 build/verify_release.py`.
2. `./build/package_release.sh` erzeugt und testet das ZIP.
3. SHA-256, `unzip -tqq` und den Release-Manifestbericht archivieren.
4. Die Owner-Freigabe umfasst Contracts, Sicherheit, Rollback und Hosted-CI.
5. Erst anschließend darf ein Release als freigegeben bezeichnet werden.

Das Artefakt trägt keine Versionsbehauptung über den kanonischen Checkout und verändert keine Git-Historie.
