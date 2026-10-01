import runpy
from pathlib import Path


def test_ci_workflow_delegates_to_canonical_verification():
    project_root = Path(__file__).resolve().parents[1]
    validator = runpy.run_path(project_root / "scripts" / "verify_ci_workflow.py")

    validator["validate_workflow"]()
