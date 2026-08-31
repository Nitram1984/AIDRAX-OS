# AIDRAX OS — AO-018 Rootfs Runtime Closure

AO-018 resolves the complete `Pre-Depends`/`Depends` closure of the exact
kernel and initramfs packages defined in AO-017 from the immutable Ubuntu
24.04 snapshot. It only creates and verifies metadata locks; no package bytes
are fetched or installed and no rootfs or ISO is built.

```bash
python3 build/resolve.py --index ../AO-015-Signed-Boot-Closure-Lock/build-output/noble-main-amd64-Packages.gz --write-lock
python3 build/verify_release.py --index ../AO-015-Signed-Boot-Closure-Lock/build-output/noble-main-amd64-Packages.gz
```
