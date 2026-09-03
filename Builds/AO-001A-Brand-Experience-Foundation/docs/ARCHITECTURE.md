# AO-001A Architecture

AO-001A is a provider-neutral, in-process contract. It adds no authority and
does not become a lifecycle owner.

```text
approved asset supply → BrandCatalog ── asset declarations ──┐
                                                             ├→ approved UI adapter
lifecycle event       → ExperienceEngine ── inert cue ───────┘
```

`BrandCatalog` validates identifiers, type, relative POSIX path and SHA-256
metadata. It never reads a file, verifies media bytes, downloads content, or
chooses a renderer. Byte verification belongs to the later approved asset
materialization stage.

`ExperienceEngine` accepts the complete fixed lifecycle vocabulary and returns
`ExperienceCue(status="PENDING_ADAPTER")`. A cue has no execution path. HERMES
may later transport approved lifecycle events, but AO-001A neither imports nor
publishes to HERMES. CapabilityRuntime remains the lifecycle authority; AIDRAX
retains orchestration and the Owner Gate remains outside this artifact.
