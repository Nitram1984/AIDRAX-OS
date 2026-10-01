# AO-021 Rootfs Configuration

This stage runs package configuration only inside the generated AO-020 rootfs,
with network disabled and `policy-rc.d` denying service starts. It does not
touch the host package database, bootloader, firmware, or storage devices.
