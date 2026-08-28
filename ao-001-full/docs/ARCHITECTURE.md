# Architektur

AO-001 folgt der aktuellen kanonischen Closed-Alpha-Architektur. Die Abhängigkeitsrichtung ist strikt: administrative Adapter → `CapabilityRuntime` → Verträge/Abhängigkeiten plus Infrastrukturadapter. ATLAS und HERMES importieren weder Runtime noch CLI.

| Bereich | Verantwortlichkeit | Grenze |
| --- | --- | --- |
| ATLAS | einzige dauerhafte Component-Registry, atomisch | keine Factory- oder Runtime-Logik |
| HERMES | strukturierte, begrenzte In-Memory-Ereignisse | kein zweiter Zustandsspeicher |
| CapabilityRuntime | Discovery, Validierung, Reihenfolge, Lifecycle, Rollback | einzige Lifecycle-Instanz |
| AO-001 Runtime | testbares Zustandsmodell und Integrationsvertrag | keine Dienste, Provider oder Prozesse |

Manifeste enthalten keine Secrets. Berechtigungen werden als Plattform-Policy entschieden (`requested ∩ granted`) und fehlende zwingende Berechtigungen blockieren vor Factory-Ladung. Ein späterer Provider braucht einen separaten owner-freigegebenen Vertrag.
