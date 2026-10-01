# Roadmap

| Phase | Ergebnis | Gate |
| --- | --- | --- |
| AO-001 | additive Plattformbasis, Verträge, sichere Tooling-Skelette | dieses Paket plus Owner-Review |
| AO-002 | Bootstrap-Integration gegen bestätigte Core-Contracts | keine Überschreibung, Recovery-Test |
| AO-003 | CapabilityRuntime-Erweiterung nach CA-015 | Provider-freie Lifecycle-, Rollback- und CI-Nachweise |
| AO-004 | Installations- und ISO-Pipeline | freigegebenes Rootfs, Bootkette, Signatur und Hardwaretest |

AO-001 implementiert bewusst keine Provider, keine externe Ausführung und kein Produktions-ISO. Das entspricht der aktuellen CA-015-Phasenfolge: Vertragsgate vor Lifecycle-Code, danach Betrieb/Verifikation, dann Extensibility Review.
