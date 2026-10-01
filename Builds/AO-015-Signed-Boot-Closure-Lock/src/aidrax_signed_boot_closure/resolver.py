"""Resolve a deterministic Debian binary-package dependency closure offline."""
from __future__ import annotations

import gzip
import hashlib
import json
import re
from collections import deque
from pathlib import Path
from typing import Any


DEPENDENCY_FIELDS = ("Pre-Depends", "Depends")
VERSION_RE = re.compile(r"\s*\([^)]*\)")


def sha256(path: Path) -> str:
    """Return the SHA-256 digest for a regular local file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_packages(index_path: Path) -> dict[str, dict[str, str]]:
    """Parse one pinned Debian Packages index for amd64 and architecture-all packages."""
    raw = gzip.open(index_path, "rt", encoding="utf-8").read() if index_path.suffix == ".gz" else index_path.read_text()
    packages: dict[str, dict[str, str]] = {}
    for stanza in raw.strip().split("\n\n"):
        fields: dict[str, str] = {}
        previous = ""
        for line in stanza.splitlines():
            if line.startswith((" ", "\t")) and previous:
                fields[previous] += "\n" + line[1:]
            elif ": " in line:
                previous, value = line.split(": ", 1)
                fields[previous] = value
        if fields.get("Architecture") in {"amd64", "all"} and "Package" in fields:
            if fields["Package"] in packages:
                raise ValueError(f"duplicate package in pinned index: {fields['Package']}")
            packages[fields["Package"]] = fields
    return packages


def _name(term: str) -> str:
    """Strip version and architecture qualifiers from one dependency alternative."""
    return VERSION_RE.sub("", term).strip().split(":", 1)[0]


def _alternatives(value: str) -> list[list[str]]:
    """Convert a Debian dependency expression into ordered alternative groups."""
    groups: list[list[str]] = []
    for group in value.split(","):
        options = [_name(item) for item in group.split("|") if _name(item)]
        if options:
            groups.append(options)
    return groups


def _choose(options: list[str], packages: dict[str, dict[str, str]], preferences: dict[str, str]) -> str:
    """Choose an explicit target-compatible alternative present in the pinned index."""
    key = "|".join(options)
    preferred = preferences.get(key)
    if preferred and preferred in options and preferred in packages:
        return preferred
    for option in options:
        if option in packages:
            return option
    raise ValueError(f"unresolvable dependency alternatives: {key}")


def resolve(index_path: Path, contract: dict[str, Any]) -> dict[str, Any]:
    """Resolve all Pre-Depends and Depends for the contract roots without installing them."""
    packages = parse_packages(index_path)
    roots = contract["root_packages"]
    for name, version in roots.items():
        if name not in packages or packages[name].get("Version") != version:
            raise ValueError(f"root package mismatch: {name}")
    selected: dict[str, dict[str, str]] = {}
    queue = deque(roots)
    while queue:
        name = queue.popleft()
        if name in selected:
            continue
        package = packages.get(name)
        if not package:
            raise ValueError(f"missing selected package: {name}")
        selected[name] = package
        for field in DEPENDENCY_FIELDS:
            for options in _alternatives(package.get(field, "")):
                chosen = _choose(options, packages, contract["alternative_preferences"])
                if chosen not in selected:
                    queue.append(chosen)
    artifacts = []
    for name in sorted(selected):
        package = selected[name]
        required = ("Version", "Filename", "Size", "SHA256")
        if any(key not in package for key in required):
            raise ValueError(f"incomplete index metadata: {name}")
        artifacts.append({"name": name, "version": package["Version"], "filename": package["Filename"], "size": int(package["Size"]), "sha256": package["SHA256"]})
    return {
        "build_id": contract["build_id"],
        "status": "VERIFIED_METADATA_CLOSURE_ONLY",
        "packages_index": {"sha256": sha256(index_path), "source_url": contract["snapshot"]["packages_url"]},
        "root_packages": roots,
        "artifacts": artifacts,
        "limitations": ["No package bytes are installed by this lock.", "No signed ISO boot chain has been assembled or booted."]
    }


def verify_lock(index_path: Path, contract: dict[str, Any], lock: dict[str, Any], artifacts_dir: Path | None = None) -> dict[str, Any]:
    """Verify the committed closure against the pinned index and optional package bytes."""
    expected = resolve(index_path, contract)
    checks = [{"name": "packages-index", "status": "VERIFIED" if expected["packages_index"]["sha256"] == contract["snapshot"]["packages_sha256"] else "BLOCKED"}, {"name": "closure-lock", "status": "VERIFIED" if expected["artifacts"] == lock.get("artifacts") and lock.get("status") == "VERIFIED_METADATA_CLOSURE_ONLY" else "BLOCKED"}]
    if artifacts_dir:
        for item in expected["artifacts"]:
            candidate = artifacts_dir / Path(item["filename"]).name
            status = "VERIFIED" if candidate.is_file() and sha256(candidate) == item["sha256"] else "BLOCKED"
            checks.append({"name": item["name"], "status": status})
    return {"status": "VERIFIED" if all(item["status"] == "VERIFIED" for item in checks) else "BLOCKED", "checks": checks}


def dump_json(value: dict[str, Any], path: Path) -> None:
    """Write canonical JSON suitable for a reviewable, deterministic source lock."""
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
