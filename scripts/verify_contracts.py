#!/usr/bin/env python3
"""Validate the CA-014 public-contract manifest against the installed source tree."""

from __future__ import annotations

import importlib
import inspect
import json
import re
import sys
import tomllib
import builtins
from pathlib import Path
from typing import Any

SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "docs" / "contracts" / "CONTRACT_MANIFEST.json"


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON-object manifest."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("contract manifest root must be an object")
    return value


def validate_manifest(manifest: dict[str, Any]) -> None:
    """Validate versioned documents, exported APIs, and console command mappings."""
    if not SEMVER.fullmatch(str(manifest.get("manifest_version", ""))):
        raise ValueError("manifest_version must be semantic versioning")
    contracts = manifest.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        raise ValueError("contracts must be a non-empty array")
    names: set[str] = set()
    for contract in contracts:
        if not isinstance(contract, dict):
            raise ValueError("each contract must be an object")
        name = contract.get("name")
        document = contract.get("document")
        if not isinstance(name, str) or name in names:
            raise ValueError("contract names must be unique strings")
        if not isinstance(document, str) or not (MANIFEST_PATH.parent / document).is_file():
            raise ValueError(f"missing contract document for {name}")
        if not SEMVER.fullmatch(str(contract.get("version", ""))):
            raise ValueError(f"invalid semantic version for {name}")
        validate_document_version(MANIFEST_PATH.parent / document, name, str(contract["version"]))
        names.add(name)

    for module_name, expected_exports in manifest.get("python_exports", {}).items():
        module = importlib.import_module(module_name)
        actual_exports = list(getattr(module, "__all__", []))
        if actual_exports != expected_exports:
            raise ValueError(f"public export mismatch for {module_name}")

    for specification in manifest.get("api_signatures", []):
        if not isinstance(specification, dict):
            raise ValueError("each API signature contract must be an object")
        target = resolve_target(specification["target"])
        signature = inspect.signature(target)
        parameters = list(signature.parameters)
        if parameters != specification["parameters"]:
            raise ValueError(f"parameter mismatch for {specification['target']}")
        if normalize_annotation(signature.return_annotation) != specification["return_type"]:
            raise ValueError(f"return type mismatch for {specification['target']}")

    validate_status_objects(manifest["status_objects"])
    validate_exception_contracts(manifest["exception_contracts"])

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    if project["version"] != manifest["package_version"]:
        raise ValueError("package version does not match contract manifest")
    if project["scripts"] != manifest["cli_commands"]:
        raise ValueError("CLI command mapping does not match contract manifest")
    core = importlib.import_module("aidrax_core")
    if core.__version__ != manifest["package_version"]:
        raise ValueError("aidrax_core version does not match contract manifest")


def resolve_target(target_name: str) -> object:
    """Resolve a documented module attribute without maintaining duplicate import maps."""
    parts = target_name.split(".")
    for separator in range(len(parts), 0, -1):
        try:
            target: object = importlib.import_module(".".join(parts[:separator]))
        except ModuleNotFoundError:
            continue
        for attribute in parts[separator:]:
            target = getattr(target, attribute)
        return target
    raise ValueError(f"cannot resolve API target: {target_name}")


def validate_document_version(path: Path, contract_name: str, version: str) -> None:
    """Require each contract title to match its manifest version exactly."""
    first_line = path.read_text(encoding="utf-8").splitlines()[0] if path.is_file() else ""
    if not first_line.startswith("# ") or first_line.rsplit(" ", maxsplit=1)[-1] != version:
        raise ValueError(f"contract document version mismatch for {contract_name}")


def normalize_annotation(annotation: object) -> str:
    """Normalize postponed and concrete annotations for contract comparison."""
    if annotation is inspect.Signature.empty:
        return ""
    value = annotation if isinstance(annotation, str) else str(annotation)
    return value.strip("'")


def validate_status_objects(specification: dict[str, Any]) -> None:
    """Check runtime and classified failure status objects against their contract shape."""
    core = importlib.import_module("aidrax_core")
    runtime_status = importlib.import_module("aidrax_core.runtime").CoreRuntime().status()
    if set(runtime_status) != set(specification["runtime"]):
        raise ValueError("runtime status keys do not match contract")
    if not isinstance(runtime_status["modules"], list) or not isinstance(runtime_status["count"], int):
        raise ValueError("runtime status value types do not match contract")
    failure_status = core.RuntimeFailure(core.RuntimeFailureCode.VALIDATION, "contract").status()
    if set(failure_status) != set(specification["failure"]):
        raise ValueError("failure status keys do not match contract")
    if failure_status["status"] != specification["failure"]["status"]:
        raise ValueError("failure status value does not match contract")
    if not isinstance(failure_status["code"], str) or not isinstance(failure_status["message"], str):
        raise ValueError("failure status string values do not match contract")
    if not isinstance(failure_status["recovered"], bool):
        raise ValueError("failure status recovered value does not match contract")
    pipeline_status = core.PipelineError("contract", "contract").status()
    if set(pipeline_status) != set(failure_status) | set(specification["pipeline_failure"]):
        raise ValueError("pipeline failure status keys do not match contract")
    if not isinstance(pipeline_status["phase"], str):
        raise ValueError("pipeline failure phase does not match contract")
    capabilities = importlib.import_module("aidrax_core.capabilities")
    manifest = capabilities.CapabilityManifest.from_mapping(
        {
            "id": "aidrax.contract",
            "name": "Contract capability",
            "version": "1.0.0",
            "description": "Contract validation capability",
            "author": "AIDRAX",
            "dependencies": [],
            "permissions": [],
            "health": "UNKNOWN",
            "priority": 0,
            "supported_interfaces": ["aidrax.capability.v1"],
        }
    )
    capability_status = capabilities.CapabilityStatus.create(
        manifest, capabilities.CapabilityState.REGISTERED, capabilities.CapabilityHealth.UNKNOWN
    ).as_dict()
    if set(capability_status) != set(specification["capability"]):
        raise ValueError("capability status keys do not match contract")
    for key, expected_type in specification["capability"].items():
        expected = getattr(builtins, expected_type)
        if not isinstance(capability_status[key], expected):
            raise ValueError(f"capability status type does not match contract for {key}")


def validate_exception_contracts(specification: dict[str, list[str]]) -> None:
    """Ensure classified public errors retain their promised base exception compatibility."""
    core = importlib.import_module("aidrax_core")
    for exception_name, base_names in specification.items():
        exception_type = getattr(core, exception_name)
        for base_name in base_names:
            expected_base = getattr(core, base_name, None) or getattr(builtins, base_name)
            if not issubclass(exception_type, expected_base):
                raise ValueError(f"exception compatibility mismatch for {exception_name}")


def main() -> int:
    """Run the contract validation command."""
    try:
        validate_manifest(load_json(MANIFEST_PATH))
    except (OSError, ValueError, json.JSONDecodeError, KeyError) as error:
        print(f"CONTRACT_VALIDATION_FAILED: {error}", file=sys.stderr)
        return 1
    print("CONTRACT_VALIDATION_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
