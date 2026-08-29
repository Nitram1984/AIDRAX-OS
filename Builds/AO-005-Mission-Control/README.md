# AIDRAX OS — AO-005 Mission Control

AO-005 is a read-only mission-control boundary. It composes status from injected ATLAS, HERMES, and ARGUS adapters into a deterministic snapshot and records operator requests as owner-gated proposals.

It does not persist registry data, deliver events, own capability lifecycle, or execute actions. A proposal is evidence for a later, explicitly approved orchestrator action; it is never an execution request by itself.
