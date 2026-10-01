# CA-012 Stabilization Report

**Build:** Closed Alpha CA-012  
**Status:** GREEN  
**Scope:** Stabilisierung der vorhandenen AIDRAX-OS-Komponenten ohne neue Capabilities, Provider oder Architekturänderungen.

## Modified files

| Bereich | Geänderte Dateien | Ergebnis |
|---|---|---|
| Registry | `src/atlas/registry.py`, `src/atlas/__init__.py`, `src/argus/scanner.py`, `src/integration/pipeline.py` | ATLAS ist der einzige Komponenten-Persistenzpfad. ARGUS behält `write_registry` als kompatible Delegation auf ATLAS. |
| Runtime-Grundlagen | `src/aidrax_core/config/*`, `src/aidrax_core/logging/*`, `src/aidrax_core/runtime/*` | Gemeinsame JSON-Konfiguration, opt-in strukturierte JSON-Logs und typisierter Runtime-Kern. |
| Ereignisse | `src/hermes/bus.py`, `src/hermes/__init__.py` | HERMES liest seine bestehende Konfiguration, prüft Eingaben und loggt strukturierte Laufzeitereignisse. |
| CLI | `src/cli/*` | Alle fünf Befehle verwenden explizite `main`-Entrypoints; Imports führen keine Ausführung oder Dateischreibung mehr aus. |
| Packaging und Betrieb | `pyproject.toml`, `installer/install.sh`, `scripts/verify.sh`, `.gitignore` | Installierbares Python-3.12-Paket, deklarierte Testabhängigkeit, saubere Laufzeitartefakte und reproduzierbare Verifikation. |
| Tests und Dokumentation | `tests/*`, `README.md`, `docs/BUILD.md`, `CHANGELOG.md` | 18 Tests für Registry, Logger, Konfiguration, Runtime, HERMES, Pipeline und CLI; Dokumentation beschreibt CA-012. |

## Engineering rationale

CA-011 hatte drei voneinander getrennte Schreibpfade für `registry/components.json`. CA-012 zentralisiert Validierung, Normalisierung und atomisches Schreiben in `atlas.Registry`. Der vorhandene ARGUS-Aufruf `write_registry(projects, out)` bleibt als delegierende Schnittstelle bestehen; historische Scanner-Einträge mit `name` werden beim Schreiben zu kanonischen `id`-Einträgen normalisiert.

Alle bisherigen CLI-Dateien führten beim Import Demo- oder Schreiboperationen aus. Sie sind nun echte Kommando-Einstiegspunkte mit Caller-Eingaben. Die neuen `project.scripts` referenzieren diese Funktionen; Provider- oder Capabilitylogik wurde nicht ergänzt.

Konfiguration wird ausschließlich über `aidrax_core.config.Config` gelesen. Logging wird ausschließlich über `aidrax_core.logging` erzeugt und liefert JSON-Zeilen mit Zeitstempel, Level, Logger, Ereignis und fachlichen Feldern.

## Verification

Die Verifikation lief mit Python 3.12.3 in einer isolierten temporären Umgebung.

| Prüfung | Ergebnis |
|---|---|
| `python -m compileall -q src tests` | GREEN |
| Importvalidierung aller Runtime- und CLI-Module | GREEN, keine erzeugten Dateien beim Import |
| Isolierter Registry-/HERMES-/Pipeline-Smoke-Test | GREEN |
| `python -m pytest` | GREEN, 18 bestanden |
| Registry-Formatprüfung | GREEN |
| Wheel-Build mit `pip wheel --no-build-isolation --no-deps .` | GREEN |
| Installierte CLI-Entrypoints | GREEN |
| `./scripts/verify.sh` | `CA-012_VERIFICATION_GREEN` |

## Risk assessment

- **Registry-Migration:** Niedrig. Der öffentliche ARGUS-Schreibaufruf bleibt erhalten; ATLAS akzeptiert alte `name`-Einträge und minimale historische `id`-Einträge.
- **Logging:** Niedrig. Logging ist beim Import inaktiv; nur explizite CLI-Ausführung konfiguriert den `aidrax`-Logger.
- **CLI:** Niedrig bis mittel. Der Import von CLI-Dateien erzeugt keine früheren Demo-Artefakte mehr. Nutzer, die die Dateien direkt als Skript gestartet haben, erhalten weiterhin eine Ausführung über den `__main__`-Guard.
- **Packaging:** Niedrig. Das Paket hat keine Runtime-Abhängigkeiten. `pytest` ist bewusst nur als Test-Extra deklariert.

## Compatibility impact

Bestehende Modulnamen, `CoreRuntime.register`, `CoreRuntime.status`, `EventBus.subscribe`, `EventBus.publish`, `EventBus.pending`, `Registry.load`, `Registry.save`, `Registry.add`, `scan`, `write_registry` und `integrate(projects)` bleiben nutzbar.

Die Registry ist nun bei neuen Scanner- und Pipeline-Schreibvorgängen kanonisch als `id`, `path`, `status` aufgebaut. Alte Komponenten mit ausschließlich `id` bleiben lesbar. Der einzige bewusst entfernte Effekt ist nicht vertragsfähiges Demo-Verhalten beim CLI-Import.

## Remaining technical debt

- HERMES ist weiterhin ein unpersistierter Closed-Alpha-In-Memory-Bus ohne Kapazitätsgrenze; die bestehende Konfiguration definiert keine Grenze.
- Komponenten- und Ereignisverträge sind zur Laufzeit validiert, aber noch nicht als eigenständige versionierte Schemaartefakte dokumentiert.
- Der Checkout wurde als Build-Artefakt ohne bestehende Git-Historie geliefert; CA-012 initialisiert daher erst den geforderten lokalen Commit-Verlauf.
- Eine CI-Ausführungsumgebung ist nicht im gelieferten Checkout konfiguriert. Die lokale Verifikationspipeline ist aber dafür bestimmt, unverändert in CI aufgerufen zu werden.

## Recommendation for CA-013

CA-013 sollte erst nach Architekturfreigabe die existierenden Verträge versioniert dokumentieren und die CA-012-Verifikation in die vorgegebene CI-Umgebung überführen. Neue Capability-, Provider- oder Entscheidungslogik ist nicht Teil dieser Engineering-Empfehlung.
