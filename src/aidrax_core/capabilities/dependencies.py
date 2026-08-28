"""Deterministic capability dependency graph validation and ordering."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from aidrax_core.capabilities.manifest import CapabilityManifest
from aidrax_core.errors import CapabilityDependencyError


class DependencyResolver:
    """Validate exact dependency versions and produce stable topological orders."""

    def resolve(self, manifests: Sequence[CapabilityManifest]) -> list[CapabilityManifest]:
        """Resolve every supplied manifest with dependencies before dependents."""
        manifest_map = self._manifest_map(manifests)
        ordered: list[CapabilityManifest] = []
        visited: set[str] = set()
        visiting: set[str] = set()
        for capability_id in sorted(manifest_map):
            self._visit(capability_id, manifest_map, visited, visiting, ordered)
        return ordered

    def resolve_for(
        self, capability_id: str, manifests: Mapping[str, CapabilityManifest]
    ) -> list[CapabilityManifest]:
        """Resolve one manifest and its transitive dependencies from a managed set."""
        if capability_id not in manifests:
            raise CapabilityDependencyError(f"missing capability dependency: {capability_id}")
        ordered: list[CapabilityManifest] = []
        self._visit(capability_id, manifests, set(), set(), ordered)
        return ordered

    @staticmethod
    def _manifest_map(manifests: Sequence[CapabilityManifest]) -> dict[str, CapabilityManifest]:
        """Index a proposed batch while rejecting duplicate identities."""
        manifest_map = {manifest.capability_id: manifest for manifest in manifests}
        if len(manifest_map) != len(manifests):
            raise CapabilityDependencyError("duplicate capability id in dependency graph")
        return manifest_map

    def _visit(
        self,
        capability_id: str,
        manifests: Mapping[str, CapabilityManifest],
        visited: set[str],
        visiting: set[str],
        ordered: list[CapabilityManifest],
    ) -> None:
        """Visit a graph node once while rejecting missing, cyclic, or stale dependencies."""
        if capability_id in visited:
            return
        if capability_id in visiting:
            raise CapabilityDependencyError(f"cyclic dependency detected at capability: {capability_id}")
        try:
            manifest = manifests[capability_id]
        except KeyError as error:
            raise CapabilityDependencyError(f"missing capability dependency: {capability_id}") from error
        visiting.add(capability_id)
        for dependency in manifest.dependencies:
            try:
                dependency_manifest = manifests[dependency.capability_id]
            except KeyError as error:
                raise CapabilityDependencyError(
                    f"missing capability dependency: {dependency.capability_id}"
                ) from error
            if dependency_manifest.version != dependency.version:
                raise CapabilityDependencyError(
                    f"dependency version mismatch for {dependency.capability_id}: "
                    f"expected {dependency.version}, found {dependency_manifest.version}"
                )
            self._visit(dependency.capability_id, manifests, visited, visiting, ordered)
        visiting.remove(capability_id)
        visited.add(capability_id)
        ordered.append(manifest)
