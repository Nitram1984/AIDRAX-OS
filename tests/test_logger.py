import io
import json

from aidrax_core.logging import REDACTED_VALUE, configure_logging, get_logger, is_sensitive_field


def test_structured_logger_emits_json_payload():
    stream = io.StringIO()
    configure_logging(stream=stream)

    get_logger("test").info("completed", extra={"event": "test.completed", "count": 1})

    payload = json.loads(stream.getvalue())
    assert payload["event"] == "test.completed"
    assert payload["count"] == 1
    assert payload["message"] == "completed"


def test_structured_logger_redacts_sensitive_values_recursively():
    stream = io.StringIO()
    configure_logging(stream=stream)

    get_logger("test").info(
        "authorization=Bearer-unsafe",
        extra={
            "api_key": "unsafe-key",
            "metadata": {"client_secret": "unsafe-secret", "trace_id": "trace-1"},
            "items": [{"token": "unsafe-token"}],
        },
    )

    payload = json.loads(stream.getvalue())
    assert payload["message"] == "authorization=[REDACTED]"
    assert payload["api_key"] == REDACTED_VALUE
    assert payload["metadata"] == {"client_secret": REDACTED_VALUE, "trace_id": "trace-1"}
    assert payload["items"] == [{"token": REDACTED_VALUE}]
    assert is_sensitive_field("access_token")
    assert not is_sensitive_field("trace_id")
