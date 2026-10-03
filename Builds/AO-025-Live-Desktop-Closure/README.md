# AO-025 — Live Desktop Closure

AO-025 integrates a hash-recorded Ubuntu desktop package closure into a new,
isolated AO-022 rootfs copy. It supplies SDDM autologin, an X11/Openbox
session, and a visible AIDRAX dashboard. It does not create or write an ISO,
mount host paths, change firmware, or run an installer.

`build/build_iso.sh` is a rootless, explicit final materialization step. It
uses only the verified AO-013 base ISO and the isolated AO-025 rootfs; it never
downloads, mounts host filesystems, installs host packages, or writes storage.
