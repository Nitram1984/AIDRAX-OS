# AIDRAX OS — AO-016 Signed Boot Package Materialization

AO-016 fetches the 68 package bytes specified by the AO-015 signed-boot
closure lock from the immutable Ubuntu 24.04 snapshot. Downloads are written
atomically and accepted only when their SHA-256 and byte size match the copied
closure lock.

It never calls `apt`, `dpkg`, `debootstrap`, Podman, an ISO builder, MOK tools,
firmware tools, or disk-writing tools. The result is an offline package set for
a later, separately approved rootfs/ISO recipe.

```bash
python3 build/import_lock.py --from-ao015 ../AO-015-Signed-Boot-Closure-Lock/docs/SIGNED-BOOT-CLOSURE-LOCK.json
python3 build/materialize.py --fetch
python3 build/verify_release.py --packages-dir build-output/packages
python3 build/build_release.py
```
