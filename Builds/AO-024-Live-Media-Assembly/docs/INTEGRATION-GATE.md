# AO-024 Integration Gate

## Reused inputs

- AO-022: configured rootfs with `vmlinuz-6.8.0-31-generic` and its initrd.
- AO-023: the immutable `live-desktop` default and owner-gated installation.
- AO-014/AO-016: the only approved provenance for signed EFI inputs.
- AO-001A: the hash-bound spectral-dragon wallpaper.

## Required before materialization

1. Materialize both signed EFI files from the AO-016 closure and verify their
   hashes against AO-014/AO-015 evidence.
2. Resolve, configure and audit a display-manager/desktop package closure in a
   fresh isolated AO-022 rootfs copy. The current rootfs has no `sddm` binary.
3. Define and validate `AIDRAX_DESKTOP_COMMAND`; the supplied session adapter
   fails closed rather than guessing a desktop command.
4. Only then create a dedicated ISO-materialization contract, including the
   boot-image layout and a VM boot/visible-session acceptance run.

## Explicit non-actions

AO-024 neither runs `mksquashfs`, `xorriso`, GRUB, SDDM, nor any network,
mount, firmware, Secure-Boot-key, installer, or storage operation. It is an
integration-ready adapter and input gate, not a bootable ISO claim.
