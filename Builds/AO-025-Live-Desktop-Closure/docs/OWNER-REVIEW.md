# AO-025 Owner Review

The owner authorizes isolated integration of the SDDM/Xorg/Openbox desktop
closure into a fresh AO-022 rootfs copy. This authorization never permits a
host package install, host service start, firmware change, disk write, or
automatic installer action.

Release approval requires all of the following evidence:

1. Package bytes are materialized from signed Ubuntu metadata and installed
   only inside the isolated rootfs copy.
2. `dpkg --audit` is clean and `sddm`, Xorg, Openbox, Tk and NetworkManager
   are present in that copy.
3. The SDDM autologin/session files and the visible AIDRAX dashboard are
   installed in that copy.
4. A later ISO/VM stage must prove boot and visible session separately.
