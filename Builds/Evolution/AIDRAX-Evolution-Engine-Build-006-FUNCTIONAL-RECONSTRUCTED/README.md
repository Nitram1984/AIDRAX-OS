# AIDRAX Evolution Engine Build 006 — Functional Reconstruction

This is a functional reconstruction of the earlier HQ Build 006, based on prior project records.

## Preserved Build-006 behavior

- Version 0.6.0 / Schema 6
- `python3 -m aidrax_evolution serve`
- `127.0.0.1:18321`
- `/health`
- `/dashboard/`
- SQLite runtime DB: `runtime/aidrax_evolution.db`
- Owner token: `runtime/owner-token.txt`
- Read-only source scan
- Secret redaction
- Prompt-injection detection
- SHA-256 deduplication
- Import preview / quarantine
- First Owner approval -> learning queue
- Second Owner approval -> permanent memory + XP
- Audit trail
- Manual reflection
- `AUTO_APPLY=false`
- `AUTO_SCAN=false`
- Owner-Gate required

## Install on AM

```bash
unzip AIDRAX-Evolution-Engine-Build-006-FUNCTIONAL-RECONSTRUCTED.zip
cd AIDRAX-Evolution-Engine-Build-006-FUNCTIONAL-RECONSTRUCTED
./install.sh
```

Then open:

`http://127.0.0.1:18321/dashboard/`

This is a functional reconstruction, not a byte-for-byte recovery of the original HQ source tree.
