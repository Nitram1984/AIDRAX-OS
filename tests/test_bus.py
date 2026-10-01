import time

import pytest

from aidrax_core.config import Config, ConfigurationError
from aidrax_core.errors import (
    QueueOverflowError,
    RuntimeTypeError,
    RuntimeValidationError,
    SubscriberFailureError,
    SubscriberTimeoutError,
)
from hermes.bus import EventBus


def hermes_config(tmp_path, **settings):
    path = tmp_path / "hermes.json"
    defaults = {
        "queue": "memory",
        "capacity": 2,
        "overflow_policy": "reject",
        "subscriber_failure_policy": "continue",
        "subscriber_timeout_seconds": None,
    }
    defaults.update(settings)
    path.write_text(str(defaults).replace("'", '"').replace("None", "null"), encoding="utf-8")
    return Config(path)


def test_publish():
    bus = EventBus()
    bus.publish("x", {})
    assert bus.pending() == 1


def test_publish_delivers_structured_payload():
    bus = EventBus()
    delivered = []
    bus.subscribe("ready", delivered.append)

    bus.publish("ready", {"status": "ok"})

    assert delivered == [{"status": "ok"}]


def test_runtime_bus_contract_failures_are_classified():
    bus = EventBus()

    with pytest.raises(RuntimeValidationError):
        bus.publish("", {})
    with pytest.raises(RuntimeTypeError):
        bus.publish("ready", [])


def test_queue_overflow_rejects_without_event_loss(tmp_path):
    bus = EventBus(hermes_config(tmp_path, capacity=1))
    bus.publish("first", {"sequence": 1})

    with pytest.raises(QueueOverflowError) as error:
        bus.publish("second", {"sequence": 2})

    assert error.value.status()["code"] == "queue_overflow"
    assert list(bus.queue) == [("first", {"sequence": 1})]


def test_explicit_drop_oldest_policy_records_new_event(tmp_path):
    bus = EventBus(hermes_config(tmp_path, capacity=1, overflow_policy="drop_oldest"))
    bus.publish("first", {"sequence": 1})
    bus.publish("second", {"sequence": 2})

    assert list(bus.queue) == [("second", {"sequence": 2})]


def test_subscriber_failure_isolated_by_continue_policy(tmp_path):
    bus = EventBus(hermes_config(tmp_path, subscriber_failure_policy="continue"))
    delivered = []

    def failing_handler(_: object) -> None:
        raise RuntimeError("subscriber failure")

    bus.subscribe("ready", failing_handler)
    bus.subscribe("ready", delivered.append)

    bus.publish("ready", {"status": "recovered"})

    assert delivered == [{"status": "recovered"}]
    assert bus.pending() == 1


def test_subscriber_failure_propagates_with_explicit_policy(tmp_path):
    bus = EventBus(hermes_config(tmp_path, subscriber_failure_policy="raise"))
    bus.subscribe("ready", lambda _: (_ for _ in ()).throw(RuntimeError("subscriber failure")))

    with pytest.raises(SubscriberFailureError) as error:
        bus.publish("ready", {})

    assert error.value.status()["code"] == "subscriber_failure"
    assert bus.pending() == 1


def test_subscriber_timeout_is_classified(tmp_path):
    bus = EventBus(
        hermes_config(tmp_path, subscriber_failure_policy="raise", subscriber_timeout_seconds=0.001)
    )
    bus.subscribe("ready", lambda _: time.sleep(0.01))

    with pytest.raises(SubscriberTimeoutError) as error:
        bus.publish("ready", {})

    assert error.value.status()["code"] == "subscriber_timeout"


def test_corrupted_hermes_configuration_is_rejected(tmp_path):
    with pytest.raises(ConfigurationError):
        EventBus(hermes_config(tmp_path, capacity=0))
