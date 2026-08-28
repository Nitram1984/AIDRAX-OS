# CA-015 Risk Matrix

| Risk | Likelihood | Impact | Control | Verification / rollback |
| --- | --- | --- | --- | --- |
| Reserved contracts are reinterpreted without a major executable contract revision. | Medium | High | Require T-015-01 owner/architecture gate and manifest version approval. | Contract verifier rejects undocumented exports; revert contract amendment. |
| Markdown contract label and manifest version drift undermines the contract inventory. | Certain | Medium | Make title/manifest parity a T-015-01 validation rule before capability changes. | Dedicated mismatch fixture fails verification; correct only the approved contract version. |
| A second capability registry is introduced. | Medium | High | Require ATLAS-only persistence and reject direct manifest writes. | Registry integration tests; restore canonical document. |
| Provider-specific imports leak into core runtime. | Medium | High | Enforce dependency graph and provider-free core import tests. | Import validation; remove adapter from core boundary. |
| Dependency cycle or incompatible version creates partial activation. | Medium | High | Validate complete graph before persistence/loading; topological ordering. | Cycle/incompatibility tests; restore captured record. |
| Permission escalation through manifest values. | Medium | Critical | Explicit platform grant policy; requested permissions never self-grant. | Denied-permission test; no factory loading occurs. |
| Lifecycle event leaks secrets or provider identity. | Low | Critical | Central redaction, minimal event payload schema, no secrets in manifests. | Structured-log/event redaction tests; remove event emission. |
| HERMES publication failure is misreported as rollback. | Medium | Medium | Preserve CA-014 publish-failure semantics in lifecycle contract. | Subscriber failure tests; durable record remains inspectable. |
| Activation cleanup is incomplete. | Medium | High | Define idempotent cleanup hook and recovery result. | Forced activation failure test; state/registry assertions. |
| Shutdown failure prevents independent cleanup. | Medium | Medium | Reverse topological iteration with aggregate result. | Multiple-capability shutdown failure test. |
| Manifest schema changes break installed packages. | Low | High | Schema/runtime semver compatibility and clean-wheel verification. | Wheel tests; retain prior schema reader until migration is approved. |

Residual risk is controlled only when lifecycle, registry, event, and contract tests run through the canonical verification pipeline. No provider implementation is necessary to test these controls.
