"""Pure validation boundary for governed AIDRAX brand assets."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Iterable, Mapping

_ALLOWED_KINDS = frozenset({"animation", "font", "image", "music", "sound", "theme", "wallpaper"})


@dataclass(frozen=True, slots=True)
class BrandAsset:
    """A declared asset reference; this contract neither opens nor renders it."""

    asset_id: str
    kind: str
    path: str
    sha256: str


class BrandCatalog:
    """Immutable validated catalog, intentionally independent of asset storage."""

    def __init__(self, assets: Iterable[BrandAsset] = ()) -> None:
        declared = tuple(assets)
        self._validate(declared)
        self._assets = declared

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "BrandCatalog":
        if payload.get("schema_version") != 1:
            raise ValueError("brand catalog schema_version must be 1")
        raw_assets = payload.get("assets")
        if not isinstance(raw_assets, list):
            raise ValueError("brand catalog assets must be a list")
        try:
            assets = tuple(BrandAsset(**item) for item in raw_assets if isinstance(item, dict))
        except TypeError as error:
            raise ValueError("each asset must declare asset_id, kind, path, and sha256") from error
        if len(assets) != len(raw_assets):
            raise ValueError("each asset must be an object")
        return cls(assets)

    def assets_for(self, kind: str) -> tuple[BrandAsset, ...]:
        if kind not in _ALLOWED_KINDS:
            raise ValueError("unsupported brand asset kind")
        return tuple(asset for asset in self._assets if asset.kind == kind)

    def all_assets(self) -> tuple[BrandAsset, ...]:
        return self._assets

    @staticmethod
    def _validate(assets: tuple[BrandAsset, ...]) -> None:
        seen: set[str] = set()
        for asset in assets:
            if not asset.asset_id or asset.asset_id in seen:
                raise ValueError("asset_id must be unique and non-empty")
            if asset.kind not in _ALLOWED_KINDS:
                raise ValueError("unsupported brand asset kind")
            path = PurePosixPath(asset.path)
            if path.is_absolute() or ".." in path.parts or asset.path in {"", "."}:
                raise ValueError("asset path must be a non-empty relative POSIX path")
            if len(asset.sha256) != 64 or any(char not in "0123456789abcdef" for char in asset.sha256):
                raise ValueError("asset sha256 must be 64 lowercase hexadecimal characters")
            seen.add(asset.asset_id)
