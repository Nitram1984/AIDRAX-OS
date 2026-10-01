# ISO Roadmap

## AO-001 boundary

This release establishes the release method and safety gate for later ISO work.
`build/build_iso.sh` exits with status 2 until an approved builder contract
exists. This prevents a false ISO-success claim.

## AO-007 prerequisites

1. Approved base distribution and architecture matrix.
2. Reproducible package lock and source-mirror policy.
3. Installer partitioning, encryption, recovery, and rollback contracts.
4. Secure-boot/signing decision with protected key handling.
5. Hardware boot test matrix and immutable verification report.

AO-007 is complete only after a reproducible ISO is checksummed, booted in the
agreed matrix, and validated through platform health and recovery paths.
