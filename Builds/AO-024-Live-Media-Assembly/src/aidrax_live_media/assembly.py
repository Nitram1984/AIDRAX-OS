"""Offline-only live-media staging plan for AO-024.

This module deliberately prepares no ISO and runs no bootloader command.
It validates exactly which signed EFI and rootfs inputs must be supplied to a
separate, owner-gated ISO materialization step.
"""
from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Mapping


class MissingInputError(ValueError):
    """Raised when immutable materialization inputs are incomplete."""


@dataclass(frozen=True)
class AssemblyPlan:
    rootfs: Path
    efi_root: Path
    kernel: str
    initrd: str
    efi_required: tuple[str, ...]
    efi_sha256: Mapping[str, str]

    @classmethod
    def from_contract(cls, payload: Mapping[str, object], rootfs: Path, efi_root: Path) -> "AssemblyPlan":
        """Create a plan after validating AO-024's non-destructive contract."""
        if payload.get("schema_version") != 1 or payload.get("boot_entry") != "live-desktop":
            raise ValueError("AO-024 requires AO-023 live-desktop semantics")
        prohibited = set(payload.get("prohibited_actions", []))
        required_prohibitions = {"network_download", "host_mount", "storage_write", "bootloader_install", "automatic_install"}
        if not required_prohibitions.issubset(prohibited):
            raise ValueError("AO-024 safety contract is incomplete")
        rootfs_contract = payload.get("rootfs")
        efi_required = payload.get("efi_required")
        if not isinstance(rootfs_contract, dict) or not isinstance(efi_required, list):
            raise ValueError("AO-024 media contract is malformed")
        expected_hashes = payload.get("efi_sha256")
        if not isinstance(expected_hashes, dict) or set(expected_hashes) != set(efi_required):
            raise ValueError("AO-024 requires hash-bound EFI inputs")
        return cls(rootfs, efi_root, str(rootfs_contract["kernel"]), str(rootfs_contract["initrd"]), tuple(str(item) for item in efi_required), {str(name): str(value) for name, value in expected_hashes.items()})

    def missing_inputs(self) -> tuple[str, ...]:
        """Return every kernel, initrd, and signed-EFI file not supplied."""
        expected = [(self.rootfs, self.kernel), (self.rootfs, self.initrd)]
        expected.extend((self.efi_root, item) for item in self.efi_required)
        return tuple(relative for base, relative in expected if not (base / relative).is_file())

    def assert_ready_for_iso_materialization(self) -> None:
        """Fail closed until all immutable inputs are present locally."""
        missing = self.missing_inputs()
        if missing:
            raise MissingInputError("missing immutable inputs: " + ", ".join(missing))
        mismatches = [relative for relative, expected in self.efi_sha256.items() if hashlib.sha256((self.efi_root / relative).read_bytes()).hexdigest() != expected]
        if mismatches:
            raise MissingInputError("EFI hash mismatch: " + ", ".join(mismatches))
