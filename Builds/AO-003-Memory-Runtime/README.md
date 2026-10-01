# AIDRAX OS — AO-003 Memory Runtime

**Release:** AO-003.0.0-alpha.1

AO-003 provides local durable memory: an append-only JSONL journal, stable
entries, namespace-scoped recall, and tombstones for deliberate forgetting.
It is standalone and has no provider, embedding, cloud, or network dependency.

- Data stays in an explicit local operator-supplied path.
- ATLAS records runtime identity; HERMES carries audit events; ARGUS consumes evidence.
- No account, analytics, synchronization, credentials, or secret store.

Run `./build/verify_release.sh`, then `./build/package_release.sh`.
