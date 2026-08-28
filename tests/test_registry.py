import json

import pytest

from atlas.registry import Registry, RegistryError

def test_registry(tmp_path):
    reg=Registry(tmp_path/"components.json")
    reg.add({"id":"x"})
    assert len(reg.load()["components"])==1


def test_registry_normalizes_scanner_component_and_rejects_duplicates(tmp_path):
    registry = Registry(tmp_path / "components.json")
    registry.save({"components": [{"name": "alpha", "path": "/projects/alpha"}]})

    assert registry.load() == {
        "components": [{"id": "alpha", "path": "/projects/alpha", "status": "DISCOVERED"}]
    }

    with pytest.raises(RegistryError, match="duplicate component id"):
        registry.save({"components": [{"id": "alpha"}, {"id": "alpha"}]})


def test_registry_rejects_invalid_json(tmp_path):
    path = tmp_path / "components.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(RegistryError, match="invalid registry JSON"):
        Registry(path).load()
