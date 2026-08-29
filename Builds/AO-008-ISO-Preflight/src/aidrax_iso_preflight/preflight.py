"""Read-only, owner-gated prerequisite assessment for a future ISO build."""

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
CONTRACT_PATH = ROOT / "docs" / "ISO-TARGET-CONTRACT.json"
REQUIRED_TOOLS = ("xorriso", "mksquashfs", "grub-mkstandalone", "sbsign")
REQUIRED_GATES = ("iso_build", "signing_procedure", "mok_registration", "hardware_boot_test")
MINIMUM_WORKSPACE_BYTES = 20 * 1024**3


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class PreflightResult:
    status: str
    checks: tuple[Check, ...]
    contract: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {"status": self.status, "checks": [asdict(check) for check in self.checks], "contract": self.contract}


class IsoPreflight:
    """Assess prerequisites only; this class never invokes an ISO or key command."""

    def __init__(
        self,
        contract_path: Path = CONTRACT_PATH,
        command_exists: Callable[[str], str | None] = shutil.which,
        architecture: Callable[[], str] = platform.machine,
        uefi_present: Callable[[], bool] = lambda: Path("/sys/firmware/efi").is_dir(),
        free_space: Callable[[Path], int] = lambda path: shutil.disk_usage(path).free,
    ) -> None:
        self.contract_path = contract_path
        self.command_exists = command_exists
        self.architecture = architecture
        self.uefi_present = uefi_present
        self.free_space = free_space

    def assess(self, workspace: Path, owner_gates: Mapping[str, object] | None = None) -> PreflightResult:
        contract = self._load_contract()
        checks = (
            self._contract_check(contract),
            self._architecture_check(),
            self._uefi_check(),
            self._toolchain_check(),
            self._workspace_check(workspace),
            self._key_gate_check(contract),
            self._owner_gate_check(owner_gates),
        )
        status = "READY" if all(check.status == "READY" for check in checks) else "BLOCKED"
        return PreflightResult(status=status, checks=checks, contract=contract)

    def _load_contract(self) -> dict[str, object]:
        return json.loads(self.contract_path.read_text(encoding="utf-8"))

    @staticmethod
    def _contract_check(contract: Mapping[str, object]) -> Check:
        distribution = contract.get("distribution", {})
        boot = contract.get("boot", {})
        keys = contract.get("key_policy", {})
        expected = (
            distribution.get("name") == "Ubuntu"
            and distribution.get("release") == "24.04 LTS"
            and distribution.get("flavour") == "Minimal"
            and distribution.get("architecture") == "amd64"
            and boot.get("firmware") == "UEFI-only"
            and boot.get("secure_boot") == "enabled-by-default"
            and boot.get("trusted_boot_chain") == ["Ubuntu", "Microsoft"]
            and keys.get("automatic_key_enrolment") is False
            and keys.get("secure_boot_bypass") is False
        )
        return Check("iso_target_contract", "READY" if expected else "BLOCKED", "Ubuntu 24.04 LTS Minimal amd64 UEFI/Secure-Boot policy")

    def _architecture_check(self) -> Check:
        actual = self.architecture().lower()
        ready = actual in {"x86_64", "amd64"}
        return Check("architecture", "READY" if ready else "BLOCKED", f"detected={actual}; required=amd64")

    def _uefi_check(self) -> Check:
        present = self.uefi_present()
        return Check("uefi_policy", "READY" if present else "BLOCKED", "UEFI runtime detected" if present else "UEFI runtime not detected")

    def _toolchain_check(self) -> Check:
        missing = [tool for tool in REQUIRED_TOOLS if not self.command_exists(tool)]
        return Check("build_toolchain", "READY" if not missing else "BLOCKED", "all required tools present" if not missing else "missing=" + ",".join(missing))

    def _workspace_check(self, workspace: Path) -> Check:
        if not workspace.is_dir():
            return Check("workspace", "BLOCKED", f"not a directory: {workspace}")
        free = self.free_space(workspace)
        return Check("workspace", "READY" if free >= MINIMUM_WORKSPACE_BYTES else "BLOCKED", f"free_bytes={free}; required_bytes={MINIMUM_WORKSPACE_BYTES}")

    @staticmethod
    def _key_gate_check(contract: Mapping[str, object]) -> Check:
        keys = contract.get("key_policy", {})
        valid = keys.get("additional_keys") == "explicit-owner-approval-and-manual-MOK-registration"
        return Check("signing_and_key_gate", "READY" if valid else "BLOCKED", "manual MOK and explicit Owner-Gate required")

    @staticmethod
    def _owner_gate_check(owner_gates: Mapping[str, object] | None) -> Check:
        owner_gates = owner_gates or {}
        missing = [gate for gate in REQUIRED_GATES if owner_gates.get(gate) is not True]
        return Check("owner_gates", "READY" if not missing else "BLOCKED", "all required owner gates approved" if not missing else "unapproved=" + ",".join(missing))


def load_owner_gates(path: Path | None) -> Mapping[str, object]:
    if path is None:
        return {}
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("owner gate document must be a JSON object")
    return document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=ROOT)
    parser.add_argument("--owner-gates", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    result = IsoPreflight().assess(args.workspace, load_owner_gates(args.owner_gates))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result.status)
    return 0 if result.status == "READY" else 2


if __name__ == "__main__":
    sys.exit(main())
