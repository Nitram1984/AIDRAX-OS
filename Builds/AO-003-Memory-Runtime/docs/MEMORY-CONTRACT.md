# Memory Contract

`MemoryRuntime` accepts a local journal path plus injected ATLAS and HERMES adapters.
`remember()` appends an immutable entry; `recall()` filters active entries; `forget()` appends a tombstone.
Start reconstructs active entries by replaying the journal.

Audit events expose IDs, namespaces and tags only, not memory content. This is neither an embedding index nor a secret vault.
