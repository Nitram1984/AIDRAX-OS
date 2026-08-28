# AIDRAX OS – Engineering Report vor CA-012

**Prüfdatum:** 15. August 2026  
**Prüfbereich:** gesamter aktiver Checkout `AIDRAX_OS/CA-011-FINAL`  
**Status:** Implementierung nicht begonnen

## Umfang und Methode

Der Checkout enthält 29 versionierte Dateien: 13 Python-Quellmodule, fünf Testmodule, fünf Konfigurationsdateien, drei Dokumentationsdateien, zwei Shell-Skripte und `pyproject.toml`. Historische ZIP-Pakete neben dem Checkout gehören nicht zur aktiven Quellbasis und wurden nicht als parallel zu pflegender Code behandelt.

Geprüft wurden alle Python-Module per AST-Analyse, die gesamte Quell- und Testbasis per Bytecode-Kompilierung, Imports und Kernverhalten mit einem isolierten Smoke-Test sowie das vorhandene Verifikationsskript.

## Baseline-Validierung

| Prüfung | Ergebnis | Aussage |
|---|---|---|
| `python3 -m compileall -q src tests` | erfolgreich | Alle Python-Dateien sind syntaktisch kompilierbar. |
| Isolierter Import-/Verhaltens-Smoke-Test | erfolgreich | Scanner, Registry, CoreRuntime, EventBus und Config können im einfachen Erfolgsfall geladen und verwendet werden. |
| Isolierter Pipeline-Smoke-Test | erfolgreich | Die Pipeline erzeugt bei gültigem Eingang ihre zwei JSON-Artefakte. |
| `sh scripts/verify.sh` | erfolgreich | Das vorhandene Skript prüft nur zwei Dateien auf Syntax. |
| `PYTHONPATH=src python3 -m pytest -q` | nicht ausführbar | `pytest` ist in der Laufzeitumgebung nicht installiert; die Tests wurden daher nicht durch den vorgesehenen Runner ausgeführt. |

Ein GREEN aus `scripts/verify.sh` ist kein Projekt-GREEN: Es validiert weder Tests noch Imports, Packaging, Konfiguration, Installation oder die ARGUS/ATLAS/Integration.

## Doppelte Logik

### D-01: Registry-Serialisierung ist doppelt implementiert

- `argus.scanner.write_registry` erzeugt `{"components": ...}` und schreibt JSON nach `registry/components.json`.
- `atlas.registry.Registry.save` erstellt Verzeichnisse und serialisiert ebenfalls JSON nach einem Registry-Pfad.
- `integration.pipeline.integrate` erstellt den gleichen Zielordner und schreibt erneut eine Komponentenliste in dieselbe Datei.

Folge: Drei Implementierungen besitzen unterschiedliche Standardpfade und Serialisierungsdetails. Änderungen an Encoding, Fehlerbehandlung, atomarem Schreiben oder Schema müssten dreifach erfolgen. CA-012 sollte eine vorhandene Registry-Schreibschnittstelle als alleinigen Persistenzpfad verwenden, ohne ein neues Format einzuführen.

### D-02: Registry-Format wird widersprüchlich erzeugt

- Scanner-Einträge verwenden `name` und `path`.
- Pipeline-Einträge verwenden `id`, `path` und `status`.
- `Registry.add` akzeptiert jedes Mapping ungeprüft.

Folge: Dieselbe Datei kann strukturell inkompatible Komponenten enthalten. Dies ist keine Architekturfrage, sondern ein Integritätsfehler an einer bereits vorhandenen Schnittstelle.

## Toter oder nicht integrierter Code

| Befund | Evidenz | Auswirkung |
|---|---|---|
| `aidrax_core.logging.logger` | Es gibt keine Referenz auf `log` außerhalb des Moduls. | Logging-Konfiguration wird nicht im System verwendet. |
| `Config` | Es gibt keine Produktionsreferenz auf `Config`; nur der Smoke-Test nutzt sie. | Die fünf JSON-Konfigurationen steuern den Laufzeitpfad nicht. |
| CLI-Dateien | Kein `project.scripts`-Eintrag und keine Import-Absicherung. | Es existieren keine installierbaren Befehle; Import löst sofort Aktionen aus. |
| `config/argus.json`, `atlas.json`, `hermes.json`, `integration.json` | Ihre Werte werden von keinem Produktionsmodul geladen. | Konfiguration ist derzeit Dokumentation, nicht Systemverhalten. |

Diese Befunde sind nicht automatisch zu löschen: Vor einer Entfernung muss die CA-012-Anforderung bestimmen, ob die Teile aktiviert oder gezielt außer Betrieb genommen werden sollen.

## Unfertige oder nicht produktionsreife Module

### U-01: Installation ist funktionslos

`installer/install.sh` führt ausschließlich `echo install` aus. Es installiert weder das Paket noch Konfigurationen, Verzeichnisse oder einen ausführbaren Einstiegspunkt. Für Closed Alpha ist damit kein reproduzierbarer Installationsweg vorhanden.

### U-02: Packaging ist unvollständig

`pyproject.toml` enthält nur Name und Version. Es fehlen mindestens Python-Versionsgrenze, Build-Backend, Paketfindung, Testkonfiguration und deklarierte Kommando-Einstiegspunkte. Die Testimporte funktionieren nur mit manuell gesetztem `PYTHONPATH=src`.

### U-03: CLI-Module sind Demo-Ausführung, keine CLI

`src/cli/events.py`, `integrate.py`, `main.py`, `registry.py` und `scan.py` führen beim Import unmittelbar Funktionen aus. `integrate.py` erzeugt explizit den fiktiven Eintrag `demo` unter `/tmp/demo`; `registry.py` schreibt `demo.core` in die Standardregistry. Das verletzt die Vorgabe gegen Demo-Code und kann beim Import Dateien verändern.

### U-04: Pipeline ist nicht eingebunden

`integration.pipeline.integrate` erzeugt Komponenten- und Eventdateien, publiziert das Ereignis aber nicht über HERMES. Sie verwendet auch nicht die ATLAS-Registryklasse. Der Name "Integration" entspricht damit nicht dem derzeitigen Verhalten.

### U-05: Fehlende Vertrags- und Fehlerbehandlung

Scanner, Registry, Bus, CoreRuntime und Pipeline nehmen untypisierte Dictionaries beziehungsweise beliebige Werte entgegen. Ungültiges JSON, fehlende Schlüssel, doppelte Komponenten, defekte Subscriber und Schreibfehler werden weder fachlich abgegrenzt noch getestet.

### U-06: EventBus ist minimal und nicht abgesichert

Der Bus speichert alle veröffentlichten Ereignisse dauerhaft in einer unbeschränkten In-Memory-Deque, obwohl die Konfiguration `hermes.json` nicht gelesen wird. Handler-Ausnahmen brechen die Veröffentlichung ab; es gibt keine Ereignisstruktur, keine Abmeldung und keine definierte Fehlersemantik.

### U-07: Dokumentation ist Build-fragmentiert

README, BUILD und CHANGELOG beschreiben ausschließlich P04/HERMES, obwohl Scanner, Registry, Core und Pipeline im Checkout enthalten sind. Die Dokumentation ist keine zuverlässige Betriebs- oder Entwicklerreferenz.

## Testabdeckung und CI-Bereitschaft

Die fünf Tests decken nur Positivpfade ab: einen Publish, eine Registrierung, einen leeren Scan und eine Pipeline-Rückgabe. Sie prüfen weder Artefaktinhalte noch Fehlerfälle, Subscriber-Aufrufe, Konfiguration, Installierbarkeit, CLI-Verhalten oder die Kooperation der Subsysteme.

Es gibt keine deklarierte Testabhängigkeit und keine CI-Konfiguration. Die vorhandene Verifikation kompiliert nur `hermes.bus` und `cli.events`; sie lässt den Großteil der aktiven Python-Basis unberührt.

## Priorisierte technische Schuld

1. **Hoch:** Demo- und Import-Seiteneffekte der CLI-Module entfernen beziehungsweise in echte, deklarierte Entrypoints überführen.
2. **Hoch:** Eine alleinige Registry-Persistenzschnittstelle verwenden und ein bestehendes Komponentenformat verbindlich validieren.
3. **Hoch:** Reproduzierbares Packaging, Installations- und Testverfahren herstellen; ohne dieses ist Closed-Alpha-Build-Integrität nicht nachweisbar.
4. **Mittel:** Konfigurationen durch die jeweiligen Komponenten laden oder ungenutzte Konfiguration nach freigegebener Produktentscheidung entfernen.
5. **Mittel:** Typisierte, validierte Eingabe- und Ereignisverträge ergänzen; negative Tests hinzufügen.
6. **Mittel:** EventBus-Fehler- und Kapazitätsverhalten anhand der bestehenden `hermes.json`-Absicht implementieren.
7. **Niedrig:** Dokumentation auf den tatsächlichen Systemumfang aktualisieren und API-Dokumentation aus den stabilisierten Verträgen ableiten.

## CA-012-Empfehlung

CA-012 sollte ausschließlich den bestehenden Closed-Alpha-Kern stabilisieren: Packaging, sichere CLI-Grenzen, Registry-Integration, Konfigurationsanbindung, Fehlerverträge und reproduzierbare Tests. Neue Capabilities, neue Provider, neue UI oder eine Änderung der AIDRAX-Architektur sind nicht Teil dieser Engineering-Empfehlung.

## Freigabegrenze vor Implementierung

Für eine konkrete CA-012-Änderung ist eine priorisierte Freigabe erforderlich, welche der oben genannten Stabilisierungspunkte in den Build aufgenommen werden. Die Empfehlung setzt keine Produkt- oder Architekturentscheidung voraus, ersetzt diese aber auch nicht.
