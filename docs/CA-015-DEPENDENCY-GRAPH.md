# CA-015 Dependency Graph

## Existing Baseline

```text
CLI ──> CoreRuntime ──> Config + Logging
CLI ──> Integration ──> ATLAS Registry + HERMES EventBus
ARGUS ───────────────> ATLAS Registry
ATLAS/HERMES ────────> Config + Errors + Logging
```

## Proposed Capability Direction

```text
CLI (optional internal adapter)
            |
            v
    CapabilityRuntime
      /      |       \\
     v       v        v
 Contracts  Graph   Infrastructure ports
                      |       |       |
                      v       v       v
                   Config   ATLAS   HERMES + Logging
                      |
                      v
              approved capability settings

Factory Resolver --> capability implementation instance
```

## Required Acyclic Rules

1. `contracts` and graph validation import no infrastructure adapter or capability implementation.
2. `CapabilityRuntime` may depend on injected ATLAS, HERMES, config, logging, clock, and resolver interfaces.
3. ATLAS, HERMES, Config, Logging, and Errors must never import `CapabilityRuntime`, CLI, or an adapter.
4. An adapter/factory is loaded only after manifest validation; importing core packages must not import provider SDKs.
5. A capability implementation may consume its granted runtime context but may not mutate ATLAS or HERMES internals directly.

## Task Dependencies

```text
T-015-01 Contract gate
    └── T-015-02 Domain model
          ├── T-015-03 ATLAS representation
          └── T-015-04 Dependency graph
                └── T-015-05 Lifecycle coordinator
                      ├── T-015-06 Events and logging
                      └── T-015-07 Configuration / optional CLI
                            └── T-015-08 Verification and CI
                                  └── T-015-09 Provider-free extensibility review
```
