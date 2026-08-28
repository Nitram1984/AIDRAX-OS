# CA-014 Dependency Graph

```text
T-014-01 Configuration-root policy
   ├── T-014-02 Recoverable pipeline transition
   │      └── T-014-04 Contract verifier depth
   └── T-014-03 HERMES capacity and error semantics
          └── T-014-04 Contract verifier depth

T-014-04 ──┐
T-014-02 ──┼── T-014-05 Failure/recovery/rollback/bounded-load tests
T-014-03 ──┘       ├── T-014-06 Logging redaction policy
                     └── T-014-07 CI execution definition

T-014-08 Namespace assessment (independent, review-only)
```

## Existing Runtime Dependency Graph

```text
CLI → ARGUS → ATLAS → Config + Logging
CLI → Integration → ATLAS + HERMES → Config + Logging
CLI → CoreRuntime → Config + Logging
```

The CA-013 graph is acyclic. CA-014 tasks must preserve this direction and may not create a dependency from Core, ATLAS or HERMES back into CLI or Integration.
