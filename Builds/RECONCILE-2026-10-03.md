# AIDRAX OS Reconcile — 2026-10-03

Canonical target: HQ /mnt/DATA2/Projects/AIDRAX-OS
Recovered source host: AM AIDRAX-mobile

Recovered build families:
- AO-028A-01 through AO-028A-08
- AO-028B-01 through AO-028B-08
- AO-028C-01
- AIDRAX AO-029A/B/C/D installer and collector sources
- AO-030 design staging, Crystal decoration and lockscreen source
- Evolution Engine Build 006 functional reconstructed source
- Evolution Control Build 006 reconstructed source

Sanitization:
- __pycache__ and *.pyc excluded
- runtime databases, WAL/SHM files and owner-token material excluded
- AO-028C SHA256SUMS regenerated against the source-only recovered artifact
- host runtime symlinks and live state are not archived as source

Governance:
- autonomous production deployment remains disabled
- Owner Gate remains required for critical actions
- this reconcile archives and validates source; it does not auto-apply recovered builds to HQ
