# Development Handbook

## Working rule

Develop in independently reviewable slices. A change begins with a contract,
keeps authority boundaries intact, and ends with executed evidence.

## Authority boundaries

| Concern | Canonical owner | Rule |
| --- | --- | --- |
| persistent registry | ATLAS | no parallel registry |
| events | HERMES | no side-channel lifecycle bus |
| policy and health evidence | ARGUS | observations are immutable evidence |
| capability lifecycle | CapabilityRuntime | discovery, activation, rollback live here |

## Required change evidence

1. State the affected contract and compatibility impact.
2. Run focused tests and `./build/verify_release.sh`.
3. Record the result in the change or release notes.
4. Do not claim a service, desktop, installer, or ISO works without executing its acceptance path.

Generated output belongs in `dist/`; it must not be committed. Secrets belong
outside the repository and are referenced, never embedded in source or reports.
