# AO-025 r12 — SDDM Xorg Launch Trace

## Status

`INTEGRATION IN PROGRESS`

## Finding

The r11 guest reached `graphical.target` and started SDDM, but did not expose
an Xorg or greeter process in the observed runtime path. A direct, in-guest
Xorg invocation did start with the r11 VESA configuration. The unresolved
boundary is therefore SDDM's display-server hand-off.

## Isolated correction

The r12 rootfs keeps the verified VESA driver and configures SDDM's X11 server
path explicitly through `/usr/local/lib/aidrax/aidrax-xorg-launch`. The wrapper
records only the Xorg argument vector in the volatile guest path
`/run/aidrax/xorg-launch.log`, then `exec`s `/usr/lib/xorg/Xorg`.

No host package, host service, USB medium, predecessor rootfs, or production
configuration is changed. r11 remains the rollback baseline.

## Acceptance

r12 is accepted only after a QEMU screenshot shows the AIDRAX desktop and the
guest trace proves that SDDM invoked Xorg. Structural checks and a started SDDM
unit are insufficient.
