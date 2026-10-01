# AIDRAX OS — AO-020 Isolated Rootfs Assembly

AO-020 builds an isolated payload rootfs from the verified Ubuntu base archive
and AO-019 runtime package bytes. It uses `dpkg-deb --fsys-tarfile` only to
extract package payloads; it does not run package scripts, `chroot`, services,
containers or image tools.

The output is not bootable: initramfs generation, package configuration,
bootloader layout, squashfs and ISO generation remain subsequent stages.
