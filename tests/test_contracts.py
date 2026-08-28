import copy
import runpy
import subprocess
import sys
from pathlib import Path

import pytest


def test_contract_manifest_matches_public_interfaces():
    project_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/verify_contracts.py"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "CONTRACT_VALIDATION_GREEN"


def test_contract_verifier_rejects_signature_drift():
    project_root = Path(__file__).resolve().parents[1]
    verifier = runpy.run_path(project_root / "scripts" / "verify_contracts.py")
    manifest = verifier["load_json"](project_root / "docs" / "contracts" / "CONTRACT_MANIFEST.json")
    drifted_manifest = copy.deepcopy(manifest)
    drifted_manifest["api_signatures"][0]["parameters"] = ["self", "unexpected"]

    with pytest.raises(ValueError, match="parameter mismatch"):
        verifier["validate_manifest"](drifted_manifest)


def test_contract_verifier_rejects_document_version_drift(tmp_path):
    verifier = runpy.run_path(Path(__file__).resolve().parents[1] / "scripts" / "verify_contracts.py")
    document = tmp_path / "PipelineContract.md"
    document.write_text("# Pipeline Contract 1.0.0\n", encoding="utf-8")

    with pytest.raises(ValueError, match="contract document version mismatch"):
        verifier["validate_document_version"](document, "PipelineContract", "1.0.1")
