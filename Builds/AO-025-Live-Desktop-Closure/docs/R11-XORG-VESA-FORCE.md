# AO-025 r11 — Xorg VESA Force

## Status

**READY_FOR_ISOLATED_VM_RETEST**

## Finding

The r10 VM still showed a black X11 terminal after SDDM reached
`graphical.target`. The rootfs contains `vesa_drv.so`, but Xorg's automatic
selection first probes `modesetting`, which previously found no device in the
QEMU environment.

## Isolated correction

The r11 rootfs contains `/etc/X11/xorg.conf.d/20-qemu-vesa.conf`, which
explicitly selects the already hash-verified VESA driver for QEMU standard
VGA. No package, host, ISO predecessor, or source rootfs is modified.

## Acceptance required

The r11 ISO must visibly reach the AIDRAX session in an isolated QEMU VM.
