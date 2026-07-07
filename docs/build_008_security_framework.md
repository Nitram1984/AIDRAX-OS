# AIDRAX OS Build 008 – Security Framework

Status: ACTIVE until installed and tested on Ring 1 / AB.

## Scope
- Owner-Gate baseline
- RBAC baseline
- Policy Engine baseline
- Secret Manager: runtime environment only
- Audit Log baseline
- Security smoke test

## Governance
- No sudo without Owner approval.
- No destructive actions without Owner approval.
- Secrets must not be committed.
- Agents are advisory-only unless explicitly authorized.
