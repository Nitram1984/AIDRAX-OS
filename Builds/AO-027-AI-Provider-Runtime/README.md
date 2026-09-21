# AO-027 — AI Provider Runtime

**Release:** AO-027.0.0-alpha.1
**Status:** GREEN_WITH_HOST_ENV_NOTE
**Scope:** Canonical AIDRAX OS AI/provider integration.

AO-027 turns the existing `aidrax_ai` provider stubs into a deterministic runtime.
It adds provider identity, capability-collision protection, lifecycle and health,
owner-gated execution hooks, restart-safe explicit rebinding, and a canonical
CapabilityRuntime adapter.

The first active backend is `ollama-local`, restricted to localhost and advisory
execution. It exposes `ai.chat` through `llama3.2:latest` and `ai.code` through
`qwen2.5-coder:7b`. No provider can mutate host state through this build.

External/cloud providers remain disabled until separately configured with an
explicit authorization boundary and secret-handling contract.
