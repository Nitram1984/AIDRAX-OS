import pytest

from aidrax_core.config import Config, ConfigurationError


def test_config_loads_json_object(tmp_path):
    path = tmp_path / "runtime.json"
    path.write_text('{"enabled": true}', encoding="utf-8")

    assert Config(path).load() == {"enabled": True}
    assert Config(path).get("missing", "fallback") == "fallback"


def test_config_rejects_non_object_json(tmp_path):
    path = tmp_path / "runtime.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="JSON object"):
        Config(path).load()


def test_explicit_missing_configuration_remains_empty(tmp_path):
    assert Config(tmp_path / "missing.json").load() == {}


def test_configuration_directory_environment_has_deterministic_precedence(tmp_path, monkeypatch):
    (tmp_path / "hermes.json").write_text('{"queue": "memory", "source": "environment"}', encoding="utf-8")
    monkeypatch.setenv("AIDRAX_CONFIG_DIR", str(tmp_path))

    assert Config.for_component("hermes").load()["source"] == "environment"


def test_packaged_defaults_are_available_without_checkout_path(monkeypatch):
    monkeypatch.delenv("AIDRAX_CONFIG_DIR", raising=False)
    monkeypatch.setattr(Config, "_resolve_default_path", staticmethod(lambda _: None))

    assert Config.for_component("hermes").load() == {
        "queue": "memory",
        "capacity": 256,
        "overflow_policy": "reject",
        "subscriber_failure_policy": "continue",
        "subscriber_timeout_seconds": None,
    }
    assert Config.for_component("capabilities").load() == {
        "granted_permissions": [],
        "discovery_directories": [],
    }
