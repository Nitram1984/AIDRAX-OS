# Governance

AIDRAX bleibt Orchestrator und finale Kontrollinstanz. Dieses Paket darf nur additiv integriert werden.

- Der Installer ersetzt niemals kanonische Dateien und benötigt für jede Mutation `AIDRAX_OWNER_APPROVED=YES`.
- Änderungen an ATLAS-, HERMES- oder Capability-Verträgen benötigen Owner-Review, Tests und Rollback-Nachweis.
- Keine Cloud, Netzwerkberechtigung, Konten, Telemetrie, Provider-SDKs, dynamische Imports oder Secret-Ablage.
- Ein lokales grünes Ergebnis ersetzt weder Hosted-CI noch einen Owner-Releaseentscheid.

Rollback: Die additive Integration ist ein separater Ordner `ao-001-full` im Zielcheckout. Er kann nach Owner-Freigabe entfernt werden, ohne kanonische Dateien wiederherstellen zu müssen.
