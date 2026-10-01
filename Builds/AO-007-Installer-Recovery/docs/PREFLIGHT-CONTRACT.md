# Preflight Contract

The caller must provide an exact `/dev/...` target, non-empty model and serial, a verified backup reference, and a rollback reference. `InstallerPreflight.assess()` returns `BLOCKED` until all safety facts and a current Owner-Gate approval are present. It performs no host I/O and accepts no partition layout, shell command, or write operation.

A later executor must independently re-identify the target immediately before writing, verify the backup, and record a recovery result through AIDRAX. AO-007 is only the controlled decision boundary.
