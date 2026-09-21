# AO-025 r10 — Greeter Compatibility Fix

## Status

**READY_FOR_ISOLATED_VM_RETEST**

## Finding

The r9 rootfs contained the VESA Xorg fallback, but the visible VM terminal
remained black. A direct `sddm-greeter` test showed that the active AO-025
theme requested a missing multimedia service and could not create an OpenGL
context in the virtual renderer. A later SDDM configuration file also replaced
the intended AIDRAX autologin values with empty values.

## Isolated correction

- The r10 rootfs theme uses its bundled fallback image and does not require
  video or QtMultimedia for authentication.
- `QT_QUICK_BACKEND=software` is set for the SDDM greeter.
- The later configuration file retains display and theme settings but no longer
  clears `User=aidrax` and `Session=aidrax`.

## Boundary

The r10 rootfs is a separate complete copy of r9. Existing r8 and r9 images,
rootfs copies, and source evidence remain unchanged. r10 performs no host
package installation, service activation, firmware operation, disk write, or
network access from the VM.

## Acceptance required

The r10 ISO must visibly reach the AIDRAX autologin session and dashboard in
an isolated VM. Structural results are not functional acceptance.
