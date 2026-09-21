# AO-024 — Live Media Assembly

AO-024 is the offline assembly boundary between the AO-022 configured rootfs,
the AO-023 live-desktop policy, and a future owner-gated ISO materialization.

It provides a real SDDM theme, a fail-closed desktop-session adapter, and validates kernel,
initrd and signed EFI input locations. It does not create an ISO, download
packages, mount a host filesystem, install GRUB, alter firmware, or write a
storage device.

## Current gate

The AO-022 rootfs supplies kernel and initrd. Signed EFI binaries must be
materialized from the AO-014/AO-016 verified closure into a hash-bound input
directory before ISO materialization may be enabled. The rootfs also does not
currently contain SDDM, so deployment of the theme remains blocked until an
SDDM package closure is configured and audited in an isolated rootfs copy.

Run `./build/verify_release.sh` for structural validation.
