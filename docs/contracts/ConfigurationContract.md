# Configuration Contract 1.0.3

**Classification:** Public  
**Stability:** Stable

Module `aidrax_core.config` exports `Config` and `ConfigurationError`. `Config(path=None)` performs no I/O at construction. An explicit path preserves CA-013 behavior. Without one, `Config` and `for_component(component, config_directory=None)` resolve in this order: `AIDRAX_CONFIG_DIR`, the source-checkout `config/` directory determined from the package location, then packaged defaults. An explicit `config_directory` preserves the prior caller-controlled path behavior. This order never depends on the process working directory.

`load()` returns a JSON object or `{}` for an absent explicit file. `get(key, default=None)` returns a value or the supplied default. `require_mapping(key)` returns a mapping. Unreadable JSON, malformed JSON, non-object roots, invalid component names and invalid required mappings raise `ConfigurationError`, a classified `RuntimeFailure` and `ValueError` subclass. The stable component files are `argus.json`, `atlas.json`, `capabilities.json`, `hermes.json`, `integration.json`, and `settings.json`; their existing keys are internal configuration data, not independent Python APIs. `capabilities.json` provides the `granted_permissions` and `discovery_directories` arrays used by the Capability Contract.
