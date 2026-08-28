# Build-003.1 Routing-Integration

**Status:** Additiv integriert, noch nicht produktiv aktiviert.  
**Quelle:** `/home/maddin/Downloads/AIDRAX_OS_Architekturvision_Build-003.1_SERUS_VALIDATED.zip`

## Übernommen

- deterministische, capability-basierte Node-Auswahl;
- die sechs Health-Zustände und sichere Sperre nicht routbarer Nodes;
- Owner-Gate vor geschützten Dispatches;
- Retry mit derselben Job-ID und node-lokaler Circuit Breaker;
- HERMES-kompatible Lifecycle-Ereignisse.

## Bewusste Anpassung

Der Referenz-`CoreState` wurde nicht übernommen. `NodeRouter` in
`src/aidrax_core/routing.py` fordert stattdessen einen `RoutingState`-Adapter
und einen `EventSink`. Damit bleibt ATLAS Eigentümer der späteren persistenten
State-Implementierung und HERMES Eigentümer der Ereigniszustellung.

## Offene Produktions-Gates

1. ATLAS-Adapter für Jobs, Assignments und Leases mit Transaktionen.
2. HERMES-Event-Schema als veröffentlichter Contract.
3. Signierte Node-Identitäten und Capability-Claims.
4. Worker-seitige Resultat-Idempotenz, Recovery-Probes und Audit-Aufbewahrung.
5. Owner-Freigabe vor Aktivierung realer Node-Agenten.
