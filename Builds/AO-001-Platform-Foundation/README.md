# AIDRAX OS — AO-001 Platform Foundation

**Release:** AO-001.0.0-alpha.1
**Status:** Foundation artifact — ready for architecture review
**Scope:** Standalone, non-destructive platform-build package

AO-001 provides the canonical starting layout for AIDRAX OS. It is deliberately
separate from an existing source checkout: unpack it beside a repository or use
it to initialise a new controlled workspace. It does not replace application
code, generate an ISO, install packages, or modify the host.

## Foundation decisions

- **ATLAS** is the sole persistent registry authority.
- **HERMES** is the canonical event bus.
- **ARGUS** observes health, policy, and runtime evidence.
- The platform boot path is explicit, ordered, and observable.
- Release outputs are reproducible from tracked source plus an emitted manifest.
- ISO production remains a gated future capability; its script refuses to claim
  success until a builder contract is supplied.

## Quick start

```bash
./build/verify_release.sh
./build/build_release.sh
./build/package_release.sh
```

Expected outputs are created under `dist/` (ignored by Git): a staged release,
a provenance manifest, SHA-256 checksum, and ZIP archive. Run
`./build/build_iso.sh` only to validate the ISO prerequisite gate; AO-001 does
not pretend to build an ISO.

## Directory layout

```text
AO-001-Platform-Foundation/
├── build/          deterministic release, packaging, verification, ISO gate
├── docs/           lifecycle, release, development, and ISO decisions
├── platform/       boot order and platform contract
├── src/aidrax_os/  minimal importable platform boundary
├── tests/          no-dependency contract tests
├── manifest.json   release identity and required artifacts
└── CHANGELOG.md
```

## Acceptance evidence

`verify_release.sh` checks the manifest, required layout, executable scripts,
Python syntax, import boundary, and unit tests. A GREEN verification proves the
scaffold is internally consistent—not that an installer or ISO exists.

## Safety and rollback

All generated files stay in `dist/`. Delete that directory to remove generated
output. The source artifact is otherwise self-contained and makes no system,
network, service, or repository mutations.
