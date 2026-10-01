[Deutsch](#deutsch) · [English](#english)

## Deutsch

# AIDRAX OS

**Status: Geschlossene Alpha · In Entwicklung**

Dieses Repository begleitet die Entwicklung von AIDRAX OS. Das Projekt befindet sich in einer frühen, geschlossenen Alpha-Phase. Funktionen, Schnittstellen und Dokumentation können sich noch ändern.

## Einstieg

Dieses Repository enthält die Python-Engineering-Basis für AIDRAX OS: Core-Runtime, ARGUS-Projekterkennung, ATLAS-Registry, HERMES-Ereignisbus und Capability-Integration. Weitere Plattform- und ISO-Bausteine liegen unter `Builds/`. Dies ist keine produktionsreife Veröffentlichung und keine freigegebene installierbare OS-Version.

Für die lokale Engineering-Prüfung wird Python 3.12 oder neuer benötigt:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
./scripts/verify.sh
```

Die Prüfung umfasst Syntax, Verträge, Importe, Smoke-Tests, pytest, Wheel-Build und Installation in einer isolierten Umgebung. Sie ersetzt keine vollständige Prüfung aller Bausteine unter `Builds/`.

Fragen zum Alpha-Zugang oder zu geplanten Arbeiten kannst du über die [Vorlage für allgemeine Fragen](https://github.com/Nitram1984/AIDRAX-OS/issues/new/choose) stellen. Veröffentliche dabei keine vertraulichen Informationen.

## Rückmeldungen und Mitarbeit

Fehlermeldungen, Verbesserungen der Dokumentation und konkrete Vorschläge sind willkommen. Stimme größere Änderungen vor Beginn der Umsetzung mit dem Projektverantwortlichen ab.

- [Hinweise zur Mitarbeit](CONTRIBUTING.md)
- [Verhaltenskodex](CODE_OF_CONDUCT.md)
- [Fehler melden oder Verbesserung vorschlagen](https://github.com/Nitram1984/AIDRAX-OS/issues/new/choose)
- [Sicherheitsrichtlinie und vertrauliche Meldungen](SECURITY.md)

Issues und Pull Requests können auf Deutsch oder Englisch verfasst werden. Verantwortlich für das Projekt ist [@Nitram1984](https://github.com/Nitram1984).

## Lizenzstatus

Gemäß [LICENSE](LICENSE) bleiben während der geschlossenen Alpha alle Rechte vorbehalten. Die Paketmetadaten kennzeichnen das Projekt als proprietär; eine Open-Source-Lizenz wird derzeit nicht gewährt.

---

## English

# AIDRAX OS

**Status: Closed Alpha · Development**

This is the development repository for AIDRAX OS. The project is in an early, closed-alpha stage; features, interfaces, and documentation may change.

## Getting started

This repository contains the AIDRAX OS Python engineering baseline: core runtime, ARGUS project discovery, ATLAS registry, HERMES event bus, and capability integration. Additional platform and ISO components live under `Builds/`. This is not a production release or an approved installable OS image.

Local engineering verification requires Python 3.12 or newer:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
./scripts/verify.sh
```

Verification covers syntax, contracts, imports, smoke tests, pytest, wheel building, and installation in an isolated environment. It does not replace complete validation of every component under `Builds/`.

For questions about alpha access or planned work, open a general question using the [issue templates](https://github.com/Nitram1984/AIDRAX-OS/issues/new/choose). Do not include confidential information.

## Feedback and contributions

Bug reports, documentation improvements, and focused suggestions are welcome. Discuss substantial implementation changes with the maintainer before starting work.

- [Contribution guidelines](CONTRIBUTING.md)
- [Code of conduct](CODE_OF_CONDUCT.md)
- [Report a bug or suggest an improvement](https://github.com/Nitram1984/AIDRAX-OS/issues/new/choose)
- [Security policy and private vulnerability reporting](SECURITY.md)

Issues and pull requests may be written in German or English. The project maintainer is [@Nitram1984](https://github.com/Nitram1984).

## License status

Under [LICENSE](LICENSE), all rights are reserved during closed alpha. Package metadata identifies the project as proprietary; no open-source license is currently granted.
