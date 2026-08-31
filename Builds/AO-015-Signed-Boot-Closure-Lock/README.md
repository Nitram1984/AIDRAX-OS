# AIDRAX OS — AO-015 Signed Boot Closure Lock

AO-015 resolves the Ubuntu 24.04 amd64 `Pre-Depends` and `Depends` closure
required by the AO-014 signed UEFI bootstrap packages.  Every selected package
is pinned to the same immutable Ubuntu snapshot by filename, version, size and
SHA-256.  UEFI amd64 alternatives are resolved deterministically.

It only verifies package-index metadata and optional downloaded package bytes.
It does **not** install packages, produce an ISO, alter Secure Boot/MOK state,
touch firmware, or write a disk.

Commands:

```bash
python3 build/resolve_closure.py --fetch-index --write-lock
python3 build/verify_release.py
python3 build/build_release.py
python3 build/verify_release.py --archive build-output/AO-015-Signed-Boot-Closure-Lock.zip
```

The lock is an input to a later rootfs and ISO recipe.  It is not evidence that
the signed boot chain has been assembled or booted.
