"""Deterministic local discovery of provider-neutral capability manifests."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from aidrax_core.capabilities.manifest import CapabilityManifest
from aidrax_core.config import Config
from aidrax_core.errors import CapabilityDiscoveryError


class CapabilityDiscovery:
    """Discover and validate canonical manifests from explicit local sources."""

    def __init__(self, sources: Sequence[str | Path]) -> None:
        """Create a discovery boundary over deterministic files or directories."""
        if not isinstance(sources, Sequence) or isinstance(sources, (str, bytes)):
            raise CapabilityDiscoveryError("capability discovery sources must be an array of paths")
        normalized = []
        for source in sources:
            if not isinstance(source, (str, Path)) or not str(source).strip():
                raise CapabilityDiscoveryError("capability discovery sources must be non-empty paths")
            normalized.append(Path(source))
        if len({str(path) for path in normalized}) != len(normalized):
            raise CapabilityDiscoveryError("capability discovery sources must not contain duplicates")
        self._sources = tuple(sorted(normalized, key=lambda path: str(path)))

    @classmethod
    def from_config(cls, config: Config) -> "CapabilityDiscovery":
        """Build discovery from the existing shared capabilities configuration."""
        sources = config.get("discovery_directories", [])
        if not isinstance(sources, list) or any(not isinstance(item, str) for item in sources):
            raise CapabilityDiscoveryError("capabilities.discovery_directories must be an array of strings")
        return cls(sources)

    def discover(self) -> list[CapabilityManifest]:
        """Return manifests sorted by capability ID after complete validation."""
        manifests = []
        identifiers: set[str] = set()
        for path in self._manifest_paths():
            manifest = self._load_manifest(path)
            if manifest.capability_id in identifiers:
                raise CapabilityDiscoveryError(f"duplicate discovered capability id: {manifest.capability_id}")
            identifiers.add(manifest.capability_id)
            manifests.append(manifest)
        return sorted(manifests, key=lambda manifest: manifest.capability_id)

    def _manifest_paths(self) -> list[Path]:
        """Resolve every configured source into one stable manifest-file order."""
        paths = []
        for source in self._sources:
            if source.is_file():
                paths.append(source)
                continue
            if source.is_dir():
                paths.extend(
                    sorted(
                        (path for path in source.rglob("*.json") if path.is_file()),
                        key=lambda path: str(path),
                    )
                )
                continue
            raise CapabilityDiscoveryError(f"capability discovery source does not exist: {source}")
        return sorted(paths, key=lambda path: str(path))

    @staticmethod
    def _load_manifest(path: Path) -> CapabilityManifest:
        """Read and validate exactly one local manifest file."""
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except OSError as error:
            raise CapabilityDiscoveryError(f"cannot read capability manifest: {path}", cause=error) from error
        except json.JSONDecodeError as error:
            raise CapabilityDiscoveryError(f"invalid capability manifest JSON: {path}", cause=error) from error
        if not isinstance(value, dict):
            raise CapabilityDiscoveryError(f"capability manifest root must be an object: {path}")
        return CapabilityManifest.from_mapping(value)
