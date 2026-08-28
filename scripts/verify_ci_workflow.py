#!/usr/bin/env python3
"""Validate that CI invokes the canonical AIDRAX engineering verification command."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "verification.yml"
REQUIRED_SNIPPETS = (
    "actions/checkout@v4",
    "actions/setup-python@v5",
    'python-version: "3.12"',
    "-e '.[test]'",
    "run: ./scripts/verify.sh",
)


def validate_workflow() -> None:
    """Assert that the checked-in workflow delegates to the complete verification entrypoint."""
    content = WORKFLOW_PATH.read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in content]
    if missing:
        raise ValueError(f"CI workflow is missing required verification steps: {', '.join(missing)}")


def main() -> int:
    """Run CI workflow validation as an engineering verification stage."""
    try:
        validate_workflow()
    except (OSError, ValueError) as error:
        print(f"CI_WORKFLOW_VALIDATION_FAILED: {error}", file=sys.stderr)
        return 1
    print("CI_WORKFLOW_VALIDATION_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
