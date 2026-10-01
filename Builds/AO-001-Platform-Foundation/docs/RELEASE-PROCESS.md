# Release Process

## Preconditions

- Reviewed source state and an approved release version.
- No secret values, credentials, or host-specific runtime state.
- Executed verification evidence.

## Local release path

```bash
./build/verify_release.sh
./build/build_release.sh
./build/package_release.sh
unzip -tq dist/AIDRAX-OS-*.zip
(cd dist && sha256sum -c AIDRAX-OS-*.zip.sha256)
```

The package contains source and `release-manifest.json`, whose inventory binds
every foundation file to a SHA-256 digest.

GREEN means the package is internally consistent. It does not certify an ISO,
installer, production deployment, or hardware boot.
