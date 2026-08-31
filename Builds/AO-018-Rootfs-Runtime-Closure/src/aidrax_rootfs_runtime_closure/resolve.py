"""Offline Debian package closure resolver for AO-017 rootfs runtime inputs."""
from __future__ import annotations

import gzip
import hashlib
import json
import re
from collections import deque
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    """Return a file digest without invoking package tools."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def packages(index: Path) -> dict[str, dict[str, str]]:
    """Parse the pinned binary Packages index."""
    raw = gzip.open(index, "rt", encoding="utf-8").read()
    result = {}
    for stanza in raw.strip().split("\n\n"):
        fields: dict[str, str] = {}; previous = ""
        for line in stanza.splitlines():
            if line.startswith((" ", "\t")) and previous:
                fields[previous] += "\n" + line[1:]
            elif ": " in line:
                previous, value = line.split(": ", 1); fields[previous] = value
        if fields.get("Architecture") in {"amd64", "all"} and fields.get("Package"):
            if fields["Package"] in result:
                raise ValueError(f"duplicate package: {fields['Package']}")
            result[fields["Package"]] = fields
    return result


def dependency_groups(value: str) -> list[list[str]]:
    """Parse dependency alternatives, excluding version predicates."""
    answer = []
    for group in value.split(","):
        choices = [re.sub(r"\s*\([^)]*\)", "", value).strip().split(":", 1)[0] for value in group.split("|")]
        if choices and choices != [""]:
            answer.append(choices)
    return answer


def provider_catalog(catalog: dict[str, dict[str, str]]) -> dict[str, list[str]]:
    """Map virtual package names to the deterministic real providers in this index."""
    providers: dict[str, list[str]] = {}
    for package, fields in catalog.items():
        for group in dependency_groups(fields.get("Provides", "")):
            for virtual in group:
                providers.setdefault(virtual, []).append(package)
    return providers


def closure(index: Path, contract: dict[str, Any]) -> dict[str, Any]:
    """Resolve deterministic transitive package metadata from contract roots."""
    catalog = packages(index); providers = provider_catalog(catalog); selected = {}; queue = deque(contract["root_packages"])
    for name, version in contract["root_packages"].items():
        if catalog.get(name, {}).get("Version") != version:
            raise ValueError(f"root mismatch: {name}")
    while queue:
        name = queue.popleft()
        if name in selected:
            continue
        package = catalog.get(name)
        if not package:
            raise ValueError(f"missing dependency: {name}")
        selected[name] = package
        for field in ("Pre-Depends", "Depends"):
            for options in dependency_groups(package.get(field, "")):
                key = "|".join(options); preferred = contract["alternative_preferences"].get(key)
                candidates = [(item, item) for item in options if item in catalog]
                candidates.extend((item, providers[item][0]) for item in options if item in providers)
                choice = preferred if preferred in options and preferred in catalog else (next((real for requested, real in candidates if requested == preferred), None) if preferred else (candidates[0][1] if candidates else None))
                if not choice:
                    raise ValueError(f"unresolvable alternatives: {key}")
                queue.append(choice)
    artifacts = [{"name": name, "version": data["Version"], "filename": data["Filename"], "size": int(data["Size"]), "sha256": data["SHA256"]} for name, data in sorted(selected.items())]
    return {"build_id": "AO-018", "status": "VERIFIED_METADATA_CLOSURE_ONLY", "packages_index": {"sha256": sha256(index), "source_url": contract["snapshot"]["packages_url"]}, "root_packages": contract["root_packages"], "artifacts": artifacts, "limitations": ["No package bytes were downloaded.", "No rootfs or ISO was created."]}


def write_lock(lock: dict[str, Any], path: Path) -> None:
    """Write canonical lock JSON."""
    path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n")
