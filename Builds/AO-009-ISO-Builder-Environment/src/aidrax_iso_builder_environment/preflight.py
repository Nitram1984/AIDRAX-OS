"""Read-only prerequisite assessment for the future AO-009 builder environment."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Mapping


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs" / "BUILDER-ENVIRONMENT-CONTRACT.json"
BOOT_PLAN_PATH = ROOT / "docs" / "BOOT-TEST-PREPARATION.json"
REQUIRED_TOOLS = ("podman", "xorriso", "mksquashfs", "grub-mkstandalone")


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class BuilderPreflightResult:
    status: str
    checks: tuple[Check, ...]
    builder_contract: dict[str, object]
    boot_test_plan: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "checks": [asdict(check) for check in self.checks],
            "builder_contract": self.builder_contract,
            "boot_test_plan": self.boot_test_plan,
        }


class BuilderEnvironmentPreflight:
    """Assess only. No command is executed, and no host resource is changed."""

    def __init__(
        self,
        contract_path: Path = CONTRACT_PATH,
        boot_plan_path: Path = BOOT_PLAN_PATH,
        command_exists: Callable[[str], str | None] = shutil.which,
        architecture: Callable[[], str] = platform.machine,
    ) -> None:
        self.contract_path = contract_path
        self.boot_plan_path = boot_plan_path
        self.command_exists = command_exists
        self.architecture = architecture

    def assess(self, owner_gates: Mapping[str, object] | None = None) -> BuilderPreflightResult:
        contract = self._load_json(self.contract_path)
        plan = self._load_json(self.boot_plan_path)
        checks = (
            self._contract_check(contract),
            self._architecture_check(),
            self._toolchain_check(),
            self._containment_check(contract),
            self._boot_plan_check(plan),
            self._owner_gate_check(contract, owner_gates),
        )
        status = "READY" if all(check.status == "READY" for check in checks) else "BLOCKED"
        return BuilderPreflightResult(status, checks, contract, plan)

    @staticmethod
    def _load_json(path: Path) -> dict[str, object]:
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError(f"JSON object required: {path}")
        return document

    @staticmethod
    def _contract_check(contract: Mapping[str, object]) -> Check:
        target = contract.get("target", {})
        reproducibility = contract.get("reproducibility", {})
        prohibited = contract.get("prohibited_actions", {})
        expected = (
            target == {"distribution": "Ubuntu", "release": "24.04 LTS", "flavour": "Minimal", "architecture": "amd64"}
            and reproducibility.get("base_image_digest_required") is True
            and reproducibility.get("apt_snapshot_required") is True
            and reproducibility.get("package_lock_required") is True
            and reproducibility.get("network_after_resolution") == "disabled"
            and reproducibility.get("build_timestamp") == "SOURCE_DATE_EPOCH-required"
            and all(value is False for value in prohibited.values())
        )
        return Check("builder_contract", "READY" if expected else "BLOCKED", "Ubuntu 24.04 Minimal amd64 reproducibility contract")

    def _architecture_check(self) -> Check:
        actual = self.architecture().lower()
        return Check("architecture", "READY" if actual in {"amd64", "x86_64"} else "BLOCKED", f"detected={actual}; required=amd64")

    def _toolchain_check(self) -> Check:
        missing = [tool for tool in REQUIRED_TOOLS if not self.command_exists(tool)]
        return Check("builder_toolchain", "READY" if not missing else "BLOCKED", "all preparation tools present" if not missing else "missing=" + ",".join(missing))

    @staticmethod
    def _containment_check(contract: Mapping[str, object]) -> Check:
        containment = contract.get("containment", {})
        expected = {"builder_isolation": "ephemeral-rootless", "host_mounts": "none", "privileged_mode": False, "device_passthrough": False, "secret_mounts": False}
        return Check("containment", "READY" if containment == expected else "BLOCKED", "rootless ephemeral builder without host, device, or secret access")

    @staticmethod
    def _boot_plan_check(plan: Mapping[str, object]) -> Check:
        prohibited = {"firmware writes", "NVRAM writes", "MOK registration", "disk writes", "USB preparation"}
        valid = plan.get("execution") == "preparation-only" and prohibited.issubset(set(plan.get("prohibited_actions", [])))
        return Check("boot_test_preparation", "READY" if valid else "BLOCKED", "test matrix prepared; no test media or firmware action")

    @staticmethod
    def _owner_gate_check(contract: Mapping[str, object], owner_gates: Mapping[str, object] | None) -> Check:
        gates = owner_gates or {}
        required = contract.get("approval_requirements", [])
        missing = [gate for gate in required if gates.get(gate) is not True]
        return Check("owner_gates", "READY" if not missing else "BLOCKED", "all owner gates approved" if not missing else "unapproved=" + ",".join(missing))


def load_owner_gates(path: Path | None) -> Mapping[str, object]:
    if path is None:
        return {}
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("owner gate document must be a JSON object")
    return document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner-gates", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    result = BuilderEnvironmentPreflight().assess(load_owner_gates(args.owner_gates))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result.status)
    return 0 if result.status == "READY" else 2


if __name__ == "__main__":
    sys.exit(main())
