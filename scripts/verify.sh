#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
python_bin=${PYTHON_BIN:-python3}
export PYTHONPATH="${project_root}/src${PYTHONPATH:+:${PYTHONPATH}}"

cd "${project_root}"
"${python_bin}" -m compileall -q src tests scripts
"${python_bin}" scripts/verify_contracts.py
"${python_bin}" scripts/verify_ci_workflow.py
"${python_bin}" - <<'PY'
from aidrax_core.config import Config
from aidrax_core.capabilities import (
    CapabilityDiscovery,
    CapabilityFactory,
    CapabilityManifest,
    CapabilityRuntime,
    DependencyResolver,
)
from aidrax_core.logging import StructuredFormatter, configure_logging, get_logger
from aidrax_core.runtime import CoreRuntime
from argus.scanner import scan, write_registry
from atlas.registry import Registry, validate_registry
from cli.events import main as events_main
from cli.integrate import main as integrate_main
from cli.main import main as core_main
from cli.registry import main as registry_main
from cli.scan import main as scan_main
from hermes.bus import EventBus
from integration.pipeline import integrate

assert Config().load() == {}
assert Config.for_component("capabilities").load() == {"granted_permissions": [], "discovery_directories": []}
assert CapabilityDiscovery is not None
assert CapabilityFactory is not None
assert DependencyResolver is not None
assert CapabilityRuntime is not None
assert CapabilityManifest.from_mapping({
    "id": "aidrax.verification", "name": "Verification", "version": "1.0.0",
    "description": "Verification manifest", "author": "AIDRAX", "dependencies": [],
    "permissions": [], "health": "UNKNOWN", "priority": 0,
    "supported_interfaces": ["aidrax.capability.v1"],
}).capability_id == "aidrax.verification"
assert StructuredFormatter is not None
assert configure_logging() is not None
assert get_logger("verification") is not None
assert CoreRuntime().status() == {"modules": [], "count": 0}
assert scan(root="/definitely-not-present") == []
assert callable(write_registry)
assert Registry is not None
assert validate_registry({"components": []}) == {"components": []}
assert EventBus().pending() == 0
assert callable(integrate)
assert all(callable(command) for command in (events_main, integrate_main, core_main, registry_main, scan_main))
print("IMPORT_VALIDATION_GREEN")
PY
"${python_bin}" - <<'PY'
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from atlas.registry import Registry
from hermes.bus import EventBus
from integration.pipeline import integrate

with TemporaryDirectory() as directory:
    original_directory = Path.cwd()
    os.chdir(directory)
    bus = EventBus()
    delivered = []
    bus.subscribe("component.discovered", delivered.append)
    registry = Registry("registry/components.json")
    assert integrate([{"name": "alpha", "path": "/workspace/alpha"}], registry, bus) == 1
    assert registry.load() == {"components": [{"id": "alpha", "path": "/workspace/alpha", "status": "DISCOVERED"}]}
    assert delivered == [{"component": "alpha"}]
    assert Path("reports/events.json").is_file()
    os.chdir(original_directory)
print("SMOKE_TESTS_GREEN")
PY
"${python_bin}" -m pytest
wheel_directory=$(mktemp -d /tmp/aidrax-ca013-wheel-XXXXXX)
"${python_bin}" -m pip wheel --no-deps --wheel-dir "${wheel_directory}" .
wheel_path=$(find "${wheel_directory}" -maxdepth 1 -type f -name '*.whl' -print -quit)
test -n "${wheel_path}"
installation_directory=$(mktemp -d /tmp/aidrax-ca014-install-XXXXXX)
"${python_bin}" -m venv "${installation_directory}/venv"
env -u PYTHONPATH "${installation_directory}/venv/bin/pip" install --disable-pip-version-check --no-deps --force-reinstall "${wheel_path}"
env -u PYTHONPATH "${installation_directory}/venv/bin/python" - <<'PY'
from aidrax_core.config import Config

assert Config.for_component("argus").load() == {"scan_root": "/mnt/DATA2/Projects"}
assert Config.for_component("atlas").load() == {"registry": "registry/components.json"}
assert Config.for_component("hermes").load() == {
    "queue": "memory",
    "capacity": 256,
    "overflow_policy": "reject",
    "subscriber_failure_policy": "continue",
    "subscriber_timeout_seconds": None,
}
assert Config.for_component("integration").load() == {"mode": "closed-alpha"}
assert Config.for_component("capabilities").load() == {"granted_permissions": [], "discovery_directories": []}
assert Config().load() == {}
print("INSTALLATION_CONFIG_GREEN")
PY
"${python_bin}" - <<'PY'
from pathlib import Path

from atlas.registry import Registry

registry = Registry(Path("registry/components.json"))
if registry.path.exists():
    registry.load()
print("REGISTRY_VALIDATION_GREEN")
PY
printf '%s\n' "CA-015_P1_VERIFICATION_GREEN"
