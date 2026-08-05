# AIDRAX OS

Closed Alpha · Development Branch

## CA-011R1 — ARGUS Foundation

CA-011R1 establishes the first operational AIDRAX OS component: **ARGUS Project Discovery**.

ARGUS scans the configured AIDRAX project root, identifies real software projects from supported build manifests and writes a deterministic JSON component registry.

### Supported project markers

- `pyproject.toml`
- `package.json`
- `Cargo.toml`
- `go.mod`
- `pom.xml`
- `build.gradle`
- `docker-compose.yml`
- `compose.yml`
- `CMakeLists.txt`

### Run

```bash
python3 -m aidrax_os.argus \
  --root /mnt/DATA2/Projects \
  --output runtime/argus-project-registry.json
```

After installation, the command is also available as:

```bash
aidrax-argus --root /mnt/DATA2/Projects
```

### Validate

```bash
bash scripts/verify-ca011r1.sh
```

The validation compiles the Python source and runs the complete ARGUS test suite.

## Governance

- Closed Alpha
- Owner-Gate remains authoritative
- No automatic deployment
- No destructive project operations
- ARGUS discovery is read-only; only its generated registry output is written
