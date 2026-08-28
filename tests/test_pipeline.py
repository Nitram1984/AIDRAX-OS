import json
import pytest

from aidrax_core.errors import PipelineError
from aidrax_core.config import Config
from atlas.registry import Registry
from hermes.bus import EventBus
from integration.pipeline import integrate


def raising_policy_config(tmp_path):
    path = tmp_path / "hermes-raise.json"
    path.write_text(
        '{"queue":"memory","capacity":256,"overflow_policy":"reject","subscriber_failure_policy":"raise","subscriber_timeout_seconds":null}',
        encoding="utf-8",
    )
    return Config(path)


def test_pipeline(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    delivered = []
    bus = EventBus(raising_policy_config(tmp_path))
    bus.subscribe("component.discovered", delivered.append)
    registry = Registry(tmp_path / "registry" / "components.json")

    assert integrate([{"name":"x","path":"/x"}], registry, bus) == 1
    assert registry.load()["components"] == [{"id": "x", "path": "/x", "status": "DISCOVERED"}]
    assert delivered == [{"component": "x"}]
    assert json.loads((tmp_path / "reports" / "events.json").read_text(encoding="utf-8")) == {
        "events": [{"event": "component.discovered", "component": "x"}]
    }


def test_pipeline_rolls_back_durable_state_after_subscriber_failure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry = Registry(tmp_path / "registry" / "components.json")
    registry.save({"components": [{"id": "previous", "path": "/previous"}]})
    report_path = tmp_path / "reports" / "events.json"
    report_path.parent.mkdir()
    report_path.write_text('{"events": [{"event": "previous"}]}\n', encoding="utf-8")
    bus = EventBus(raising_policy_config(tmp_path))

    def raising_subscriber(_: object) -> None:
        raise RuntimeError("subscriber failed")

    bus.subscribe("component.discovered", raising_subscriber)

    with pytest.raises(PipelineError) as error:
        integrate([{"name": "next", "path": "/next"}], registry, bus)

    assert error.value.status() == {
        "status": "failed",
        "code": "pipeline",
        "message": "integration failed during publish",
        "recovered": False,
        "phase": "publish",
    }
    assert registry.load()["components"] == [{"id": "previous", "path": "/previous", "status": "DISCOVERED"}]
    assert json.loads(report_path.read_text(encoding="utf-8")) == {"events": [{"event": "previous"}]}


def test_pipeline_recovers_after_a_prior_failure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry = Registry(tmp_path / "registry" / "components.json")
    failing_bus = EventBus(raising_policy_config(tmp_path))
    failing_bus.subscribe("component.discovered", lambda _: (_ for _ in ()).throw(RuntimeError("failed")))

    with pytest.raises(PipelineError):
        integrate([{"name": "alpha", "path": "/alpha"}], registry, failing_bus)

    assert integrate([{"name": "alpha", "path": "/alpha"}], registry, EventBus()) == 1
    assert registry.load()["components"] == [{"id": "alpha", "path": "/alpha", "status": "DISCOVERED"}]
