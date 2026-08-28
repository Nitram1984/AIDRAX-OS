# CA-013 Contract Report

**Build:** Closed Alpha CA-013  
**Branch:** `closed-alpha`  
**Status:** GREEN

## Contract Inventory

| Vertrag | Version | Klassifikation | Öffentliche Implementierung |
|---|---:|---|---|
| CapabilityContract | 1.0.0 | Public boundary | Keine; die Grenze garantiert das Fehlen einer Capability-API in CA-013. |
| ProviderContract | 1.0.0 | Public boundary | Keine; keine Provider- oder Modellintegration. |
| RegistryContract | 1.0.0 | Public | `atlas`, plus kompatibles `argus.write_registry`. |
| RuntimeContract | 1.0.0 | Public | `CoreRuntime`, `EventBus`. |
| ConfigurationContract | 1.0.0 | Public | `Config`, `ConfigurationError`. |
| LoggingContract | 1.0.0 | Public | `StructuredFormatter`, `configure_logging`, `get_logger`. |
| CLIContract | 1.0.0 | Public | Fünf installierte Konsolenbefehle. |
| PipelineContract | 1.0.0 | Public | `integration.integrate`. |

Alle Verträge liegen in [`docs/contracts`](contracts). `CONTRACT_MANIFEST.json` enthält ihren maschinenprüfbaren Bestand.

## Public APIs

| Modul | Exporte | Vertrag |
|---|---|---|
| `aidrax_core.config` | `Config`, `ConfigurationError` | Configuration 1.0.0 |
| `aidrax_core.logging` | `StructuredFormatter`, `configure_logging`, `get_logger` | Logging 1.0.0 |
| `aidrax_core.runtime` | `CoreRuntime` | Runtime 1.0.0 |
| `argus` | `scan`, `write_registry` | Registry 1.0.0 |
| `atlas` | `Registry`, `RegistryError`, `normalize_component`, `validate_registry` | Registry 1.0.0 |
| `hermes` | `EventBus` | Runtime 1.0.0 |
| `integration` | `integrate` | Pipeline 1.0.0 |

Die öffentlichen CLI-Namen sind `aidrax-core`, `aidrax-events`, `aidrax-integrate`, `aidrax-registry` und `aidrax-scan`.

## Internal APIs

- Attribute `CoreRuntime.modules`, `EventBus.queue` und `EventBus.subscribers`.
- Konkrete ATLAS-Dateioperationen, temporäre Persistenzdateien und Reportpfade.
- Logger-Handler, Zeitstempelpräzision und Reihenfolge der JSON-Felder.
- Python-Module unter `cli`; allein ihre in `pyproject.toml` abgebildeten Konsolenbefehle sind öffentlich.
- Konfigurationswerte innerhalb der bestehenden JSON-Dateien.

CA-013 enthält keine Experimental- oder Deprecated-Schnittstelle. Die Klassifikationsregeln sind in [contracts/README.md](contracts/README.md) festgelegt.

## Compatibility Matrix

| Schnittstelle | CA-012 | CA-013 | Kompatibilität |
|---|---|---|---|
| `Registry`, `scan`, `write_registry`, `integrate(projects)` | vorhanden | unverändert, dokumentiert | Vollständig |
| `CoreRuntime`, `EventBus` | vorhanden | unverändert, dokumentiert | Vollständig |
| `Config`, Logging-API | vorhanden | unverändert, dokumentiert | Vollständig |
| CLI-Konsolenbefehle | vorhanden | unverändert, dokumentiert | Vollständig |
| Paket-/Core-Version | inkonsistent | `0.13.0a1` synchronisiert | Korrektur ohne API-Bruch |

`scripts/verify_contracts.py` erzwingt die exakt dokumentierten Exportlisten, die CLI-Zuordnung sowie die Versionsgleichheit zwischen Paket, Core und Manifest. Damit gibt es keine parallele oder widersprüchliche Vertragsquelle.

## Version Matrix

| Artefakt | Version |
|---|---:|
| Paket `aidrax-os` | 0.13.0a1 |
| `aidrax_core.__version__` | 0.13.0a1 |
| Contract Manifest | 1.0.0 |
| Acht Einzelverträge | jeweils 1.0.0 |

## Breaking Change Analysis

Keine Breaking Changes festgestellt. CA-013 ergänzt ausschließlich Dokumentation und Prüfung. Die Korrektur der internen Core-Versionskonstante stellt Konsistenz mit der bestehenden Paketversion her. Es wurden keine Provider, Capability-APIs, Modellabhängigkeiten oder Architekturpfade eingeführt.

## Verification

```text
CONTRACT_VALIDATION_GREEN
19 passed
CA-013_VERIFICATION_GREEN
```

Die Pipeline prüft Bytecode-Kompilierung, Imports, Contract Manifest, API-Kompatibilität, isolierte Smoke-Tests, pytest, Wheel-Build und Registry-Validierung.

## Remaining Technical Debt

- HERMES bleibt bewusst ein nicht persistenter In-Memory-Bus ohne konfiguriertes Kapazitätslimit.
- Konfigurationsdateien haben noch keine eigene datenformatbezogene Versionskennung.
- Die lokale Verifikation ist CI-fähig, aber der gelieferte Checkout enthält keine externe CI-Ausführungsdefinition.

## Recommendations for CA-014

CA-014 sollte nur nach Architektur- und Owner-Freigabe einen der verbleibenden Contract-Bereiche erweitern: etwa formale Konfigurationsschema-Versionierung oder CI-Einbindung der bestehenden Verifikation. Capability- oder Providerintegration ist keine automatische Fortsetzung dieses Builds.
