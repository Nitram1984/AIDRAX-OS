# AO-025 r9 — VM Graphics Fix

## Status

**READY_FOR_ISOLATED_VM_RETEST**

## Finding

The r8 visible VM test reached `graphical.target`, but the graphical session
was black. The relevant Xorg evidence reported `No devices detected` and `no
screens found`. `udisks2.service` also failed during live boot, but it did not
block the graphical target and is not the cause of the black display.

## Isolated correction

A complete copy of the r8 rootfs was created as
`build-output/rootfs-ao025-desktop-20260914-r9`. Only that copy received the
following package:

| Package | Version | SHA-256 |
| --- | --- | --- |
| `xserver-xorg-video-vesa` | `1:2.6.0-1ubuntu0.1` | `6e19252a4fdafcc28b15bf3201abfff9bab339d3da91b7758de7b1ef1f9af652` |

The package provides `vesa_drv.so`, allowing Xorg to use the QEMU standard
VGA fallback. It has no additional dependencies beyond packages already in
the rootfs. `dpkg --audit` is clean after installation.

## Boundary

The r8 rootfs and all existing ISO files remain unchanged. The r9 builder
creates a new ISO and checksum only. No host packages or services, firmware,
storage device, installer, or network in the VM are changed.

## Acceptance required

The r9 ISO must boot in an isolated QEMU VM and visibly reach the intended
SDDM/AIDRAX session. Structural checks alone do not satisfy this acceptance.
