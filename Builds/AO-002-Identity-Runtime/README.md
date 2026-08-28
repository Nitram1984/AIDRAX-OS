# AIDRAX OS — AO-002 Identity Runtime

**Release:** AO-002.0.0-alpha.1
**Status:** local runtime foundation, ready for architecture review

AO-002 supplies the identity boundary missing from AO-001: immutable local
principals, finite roles, explicit action policies, and in-memory sessions.
It is standalone and does not modify the existing AIDRAX application code.

## Security boundary

- Local only: no network, cloud, provider integration, account sync, or tokens.
- A principal ID is a stable lowercase dotted identifier, not a provider ID.
- Roles are finite; permissions are policy decisions, never self-granted.
- Sessions retain no credentials and are intentionally non-persistent.
- ATLAS and HERMES are passed in as adapters; ARGUS can consume the emitted
  redacted event payloads as audit evidence.

## Quick start

```bash
./build/verify_release.sh
./build/build_release.sh
./build/package_release.sh
```

The package is an engineering build, not a login system or production access
control service. Integration into the main runtime needs a separate contract
and owner-approved migration.
