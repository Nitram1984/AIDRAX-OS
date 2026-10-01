[Deutsch](#deutsch) · [English](#english)

## Deutsch

# Mitarbeit an AIDRAX OS

AIDRAX OS befindet sich in einer geschlossenen Alpha-Phase. Besprich größere Änderungen mit [@Nitram1984](https://github.com/Nitram1984), bevor du Zeit in die Umsetzung investierst. Die Übernahme eines Beitrags ist nicht garantiert.

## Vor dem Erstellen eines Issues

- Suche in bestehenden Issues und Pull Requests nach ähnlichen Themen.
- Nutze die Vorlage für Fehlermeldungen, Verbesserungsvorschläge oder allgemeine Fragen.
- Schreibe auf Deutsch oder Englisch und behandle pro Issue ein Thema.
- Entferne Zugangsdaten, personenbezogene Daten und vertrauliche Informationen aus Protokollen und Bildschirmfotos.
- Beachte den [Verhaltenskodex](CODE_OF_CONDUCT.md).
- Melde Sicherheitslücken vertraulich gemäß [SECURITY.md](SECURITY.md), niemals in einem öffentlichen Issue oder Pull Request.

## Änderungen vorschlagen

1. Beschreibe das Problem und das gewünschte Verhalten in einem Issue. Stimme den Umfang größerer Änderungen mit dem Projektverantwortlichen ab.
2. Arbeite auf einem eigenen Branch auf Basis des aktuellen Zielbranches.
3. Halte Änderungen überschaubar. Vermeide sachfremde Umstrukturierungen und generierte Dateien.
4. Aktualisiere die betroffene Dokumentation und ergänze bei Verhaltensänderungen aussagekräftige Tests.
5. Öffne einen Pull Request mit einer Zusammenfassung, Verweisen auf zugehörige Issues, Prüfergebnissen und bekannten Einschränkungen.

Richte die Python-Umgebung gemäß [README.md](README.md) ein und führe `./scripts/verify.sh` aus. Jede Änderung muss kompilieren, dokumentiert sein und bei Verhaltensänderungen aussagekräftige Tests enthalten; vermeide Platzhalterimplementierungen. Gib keine Tests als bestanden an, die du nicht ausgeführt hast. Prüfe bei Dokumentationsänderungen Links, Dateipfade, Formatierung und die Darstellung der Vorlagen. Für betroffene Bausteine unter `Builds/` führe zusätzlich deren dokumentierte Prüfungen aus.

## Prüfung und Lizenzierung

Gehe konstruktiv auf Rückmeldungen ein. Der Projektverantwortliche entscheidet, welche Beiträge zum aktuellen Alpha-Stand passen. Feste Prüf- oder Antwortzeiten werden nicht zugesagt.

Während der geschlossenen Alpha bleiben gemäß [LICENSE](LICENSE) alle Rechte vorbehalten. Kläre die Lizenzierung vor umfangreichen Codebeiträgen mit dem Projektverantwortlichen. Reiche nur Inhalte ein, zu deren Weitergabe du berechtigt bist, und kennzeichne fremde Bestandteile einschließlich ihrer vorhandenen Lizenz.

---

## English

# Contributing to AIDRAX OS

AIDRAX OS is in closed alpha. Please discuss significant changes with [@Nitram1984](https://github.com/Nitram1984) before investing time in implementation. Acceptance of a contribution is not guaranteed.

## Before opening an issue

- Search existing issues and pull requests for related work.
- Use the bug report, feature request, or general question template.
- Write in German or English and keep each issue focused on one topic.
- Remove credentials, personal information, and confidential data from logs and screenshots.
- Follow the [code of conduct](CODE_OF_CONDUCT.md).
- Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md), never in a public issue or pull request.

## Proposing a change

1. Describe the problem and intended behavior in an issue. Agree on the scope of larger changes with the maintainer.
2. Work on a dedicated branch based on the current target branch.
3. Keep changes focused; avoid unrelated refactoring and generated files.
4. Update relevant documentation and add meaningful tests when behavior changes.
5. Open a pull request with a summary, related issue links, verification results, and any limitations.

Set up the Python environment as described in [README.md](README.md) and run `./scripts/verify.sh`. Every change must compile, be documented, and include meaningful tests for behavior changes; avoid placeholder implementations. Do not claim tests passed if they were not run. For documentation changes, check links, file paths, formatting, and template rendering. Also run the documented verification for affected components under `Builds/`.

## Review and licensing

Respond constructively to review feedback. The maintainer decides what fits the current alpha scope; no review or response time is guaranteed.

All rights are reserved during closed alpha under [LICENSE](LICENSE). Discuss licensing with the maintainer before submitting substantial code. Only submit material you are authorized to contribute, and identify any third-party material and its existing license.
