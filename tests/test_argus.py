from __future__ import annotations

import json
from pathlib import Path

import pytest

from aidrax_os.argus import build_registry, discover_projects, write_registry


def test_discovers_real_project_markers_and_stops_at_project_root(tmp_path: Path) -> None:
    alpha = tmp_path / "Alpha"
    alpha.mkdir()
    (alpha / "pyproject.toml").write_text("[project]\nname='alpha'\n", encoding="utf-8")

    nested = alpha / "nested"
    nested.mkdir()
    (nested / "package.json").write_text("{}\n", encoding="utf-8")

    beta = tmp_path / "Beta"
    beta.mkdir()
    (beta / "Cargo.toml").write_text("[package]\nname='beta'\n", encoding="utf-8")

    records = discover_projects(tmp_path)

    assert [record.name for record in records] == ["Alpha", "Beta"]
    assert records[0].markers == ("pyproject.toml",)
    assert records[1].markers == ("Cargo.toml",)


def test_ignores_dependency_and_build_directories(tmp_path: Path) -> None:
    project = tmp_path / "Gamma"
    project.mkdir()
    (project / "go.mod").write_text("module example/gamma\n", encoding="utf-8")

    ignored = tmp_path / "node_modules" / "FakeProject"
    ignored.mkdir(parents=True)
    (ignored / "package.json").write_text("{}\n", encoding="utf-8")

    records = discover_projects(tmp_path)

    assert [record.name for record in records] == ["Gamma"]


def test_build_registry_uses_expected_schema(tmp_path: Path) -> None:
    project = tmp_path / "Delta"
    project.mkdir()
    (project / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.20)\n", encoding="utf-8")

    registry = build_registry(tmp_path)

    assert registry["schema"] == "aidrax.ca011r1.argus.registry.v1"
    assert registry["project_count"] == 1
    assert registry["root"] == str(tmp_path.resolve())
    assert registry["projects"][0]["name"] == "Delta"


def test_write_registry_replaces_output_atomically(tmp_path: Path) -> None:
    output = tmp_path / "runtime" / "registry.json"
    registry = {
        "schema": "aidrax.ca011r1.argus.registry.v1",
        "generated_at": "2026-08-05T00:00:00+00:00",
        "root": str(tmp_path),
        "project_count": 0,
        "projects": [],
    }

    write_registry(registry, output)

    assert json.loads(output.read_text(encoding="utf-8")) == registry
    assert not output.with_suffix(".json.tmp").exists()


def test_missing_root_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        discover_projects(tmp_path / "missing")
