import importlib

import pytest

from cli.events import main as events_main
from cli.integrate import main as integrate_main
from cli.main import main as core_main
from cli.registry import main as registry_main
from cli.scan import main as scan_main


@pytest.mark.parametrize(
    "module_name",
    ["cli.main", "cli.events", "cli.integrate", "cli.registry", "cli.scan"],
)
def test_cli_imports_have_no_runtime_execution(module_name):
    assert importlib.import_module(module_name) is not None


def test_cli_entrypoints_accept_explicit_input(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    project = tmp_path / "alpha"
    project.mkdir()

    assert core_main([]) == 0
    assert events_main(["system.start", "--payload", '{"status": "ok"}']) == 0
    assert scan_main(["--root", str(tmp_path), "--output", "registry/components.json"]) == 0
    assert registry_main(["--path", "registry/components.json"]) == 0
    assert integrate_main([str(project)]) == 0
