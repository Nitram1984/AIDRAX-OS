# Registry Contract 1.0.2

**Classification:** Public  
**Stability:** Stable

Module `atlas` exports `Registry`, `RegistryError`, `normalize_component`, and `validate_registry`. `Registry(path=None, config=None)` is the only persistent component-registry implementation. `load()` returns a registry object with `components`; absent files return `{"components": []}`. `save(data)` atomically persists a validated registry. `add(component)` appends one validated component and rejects duplicate IDs.

Canonical components contain `id`; `path` and `status` are optional for historical compatibility. When `path` exists and `status` is omitted, status becomes `DISCOVERED`. Legacy scanner input using `name` is normalized to `id` at the persistence boundary. A component may additionally contain `health` and a JSON-object `capability` record. These optional additive fields are owned by the Capability Contract and preserve all historical scanner records. `restore(data)` is the public recovery operation used by a higher-level transition: it restores a complete prior registry or removes a registry that was previously absent. Invalid registry content or persistence raises `RegistryError`, a classified `RuntimeFailure` and `ValueError` subclass.

`argus.write_registry(projects, out)` is public compatibility API but is a delegating adapter, not a second persistence contract.
