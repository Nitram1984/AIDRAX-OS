# Logging Contract 1.0.1

**Classification:** Public  
**Stability:** Stable

Module `aidrax_core.logging` exports `StructuredFormatter`, `configure_logging`, `get_logger`, `REDACTION_POLICY_VERSION`, `REDACTED_VALUE`, `is_sensitive_field`, and `redact_log_value`. Importing the module does not configure logging. `configure_logging(level="INFO", stream=None)` explicitly configures the isolated `aidrax` logger and returns it. `get_logger(component)` returns an `aidrax.<component>` logger.

`StructuredFormatter` produces one JSON object per record with `timestamp`, `level`, `logger`, and `message`; caller-supplied non-private `extra` fields are included. Redaction policy 1.0 deterministically replaces values of `api_key`, `authorization`, `cookie`, `password`, `private_key`, `secret`, `session_token`, `token` and equivalent normalized names with `[REDACTED]`, including nested mappings and sequences. Typical `key=value` secret forms in messages are also masked. Callers must still avoid putting secrets into free-form prose without a field name. Handler identity, exact timestamp format precision, and field ordering are internal.
