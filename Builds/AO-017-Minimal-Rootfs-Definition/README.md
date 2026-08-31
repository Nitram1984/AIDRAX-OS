# AIDRAX OS — AO-017 Minimal Rootfs Definition

AO-017 binds the custom Ubuntu 24.04.4 amd64 base rootfs and the exact kernel,
module and initramfs package inputs for the first AIDRAX OS rootfs. It creates
an immutable composition request only after all supplied bytes verify.

No archive is extracted, no Debian package is installed, and no container, ISO,
bootloader, MOK, firmware or disk action is performed.

```bash
python3 build/validate_inputs.py --source-root /home/maddin/AIDRAX-OS-AO-013-24-dual-path-20260829T174000Z/custom-rootfs
python3 build/prepare_composition.py --source-root /home/maddin/AIDRAX-OS-AO-013-24-dual-path-20260829T174000Z/custom-rootfs
python3 build/verify_release.py
```

The resulting request is input for a separate rootfs assembler. It is not a
rootfs, an ISO or a boot test.
