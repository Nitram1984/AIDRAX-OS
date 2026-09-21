# AO-027 Architecture Closure

Status: GREEN — Phase 2 decisions frozen for AO-027.

## Provider authorization

Provider execution remains deny-by-default whenever `owner_gate_required()` is true. `ProviderRuntime` accepts only an explicit authorization hook; absence or rejection of that hook blocks execution with `ProviderAuthorizationError`. No provider may infer approval from configuration, provider identity, network availability, or a stored secret.

## Secret boundary

Provider secrets are runtime-only. `EnvironmentSecretResolver` maps a provider ID and secret name to an explicit environment variable and returns the value only to the provider composition layer. Secret values are not written to capability manifests, `providers.json`, ATLAS, HERMES, logs, metadata, status objects, or Git.

Local Ollama requires no secret and remains localhost/advisory-only. External/cloud providers remain disabled until a provider-specific adapter declares its required secrets and owner-gated actions.

## HERMES durability decision

HERMES remains synchronous and in-memory for AO-027. This is an intentional transport boundary, not an unresolved implementation defect. Durable component/capability state belongs to ATLAS; durable conversational memory belongs to the Memory Runtime. Provider requests must not rely on HERMES queue persistence for correctness or recovery.

## Namespace decision

The legacy top-level packages `atlas`, `hermes`, `argus`, `integration`, and `cli` remain compatibility exports for AO-027. Renaming them inside the current alpha line would create avoidable import breakage. New OS composition code belongs under `aidrax_os.*`; new AI/provider code belongs under `aidrax_ai.*`. A namespace migration, if required, must use a compatibility bridge and a major-release contract change.

## Versioning decision

Core contract/package compatibility remains `0.15.0a2`. Platform progression is tracked separately in `platform-version.json`; AO-027 is `AO-027.0.0-alpha.1`. This prevents the historical CA core version from being misrepresented as the platform build number while preserving contract-verifier compatibility.

## Repository/build-output decision

Generated rootfs trees, ISO images, package caches, and other materialized build products are local evidence and must not be committed as source. Source contracts, scripts, manifests, tests, and concise evidence records may be tracked. Large build products remain reproducible outputs and are covered by repository ignore rules.

## Closed items

- restart-safe provider rebinding: CLOSED via `ProviderCatalog` + explicit `ProviderFactory`
- provider authorization boundary: CLOSED, deny-by-default
- secret retrieval boundary: CLOSED, runtime-only resolver
- HERMES durability: CLOSED by explicit architectural decision for AO-027
- namespace collision: CLOSED as accepted compatibility policy for the current alpha line
- platform/core version ambiguity: CLOSED by split platform/core versioning
