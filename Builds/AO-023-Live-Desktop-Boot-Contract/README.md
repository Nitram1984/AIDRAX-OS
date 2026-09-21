# AO-023 — Live Desktop Boot Contract

The approved first-ISO behavior is **live-desktop-first**: successful UEFI boot
opens the AIDRAX Desktop without changing persistent storage. Installation is
an explicit, separately owner-gated action. Recovery is a separate boot-menu
entry. This package creates no ISO and invokes no bootloader, disk or host API.

Run `./build/verify_release.sh` to validate the contract.
