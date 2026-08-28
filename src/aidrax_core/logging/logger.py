"""Structured, opt-in runtime logging for AIDRAX OS."""

from __future__ import annotations

import json
import logging
import re
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any, TextIO

_STANDARD_RECORD_FIELDS = frozenset(logging.makeLogRecord({}).__dict__)
REDACTION_POLICY_VERSION = "1.0"
REDACTED_VALUE = "[REDACTED]"
_SENSITIVE_FIELD_NAMES = frozenset(
    {
        "api_key",
        "apikey",
        "authorization",
        "credential",
        "credentials",
        "cookie",
        "password",
        "passwd",
        "private_key",
        "secret",
        "session_token",
        "token",
    }
)
_MESSAGE_SECRET_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|authorization|cookie|password|passwd|private[_-]?key|secret|session[_-]?token|token)\s*[:=]\s*([^\s,;]+)"
)


def is_sensitive_field(field_name: object) -> bool:
    """Classify one structured field name according to the central redaction policy."""
    if not isinstance(field_name, str):
        return False
    normalized = field_name.strip().lower().replace("-", "_")
    return normalized in _SENSITIVE_FIELD_NAMES or normalized.endswith(
        ("_api_key", "_authorization", "_cookie", "_password", "_passwd", "_private_key", "_secret", "_session_token", "_token")
    )


def redact_log_value(field_name: object, value: Any) -> Any:
    """Recursively redact values when their field name is classified as sensitive."""
    if is_sensitive_field(field_name):
        return REDACTED_VALUE
    if isinstance(value, Mapping):
        return {str(key): redact_log_value(key, nested_value) for key, nested_value in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [redact_log_value(field_name, nested_value) for nested_value in value]
    return value


def _redact_message(message: str) -> str:
    """Mask common key-value secret forms while leaving operational text useful."""
    return _MESSAGE_SECRET_PATTERN.sub(lambda match: f"{match.group(1)}={REDACTED_VALUE}", message)


class StructuredFormatter(logging.Formatter):
    """Render runtime records as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialize standard metadata and explicitly supplied structured fields."""
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": _redact_message(record.getMessage()),
        }
        payload.update(
            {
                key: value
                for key, value in record.__dict__.items()
                if key not in _STANDARD_RECORD_FIELDS and not key.startswith("_")
            }
        )
        redacted_payload = {
            key: redact_log_value(key, value)
            for key, value in payload.items()
        }
        return json.dumps(redacted_payload, ensure_ascii=False, default=str, sort_keys=True)


def configure_logging(level: str = "INFO", stream: TextIO | None = None) -> logging.Logger:
    """Configure and return the isolated AIDRAX runtime logger."""
    logger = logging.getLogger("aidrax")
    logger.setLevel(level.upper())
    logger.propagate = False
    logger.handlers.clear()
    handler = logging.StreamHandler(stream if stream is not None else sys.stderr)
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)
    return logger


def get_logger(component: str) -> logging.Logger:
    """Return a component logger without configuring global logging on import."""
    return logging.getLogger(f"aidrax.{component}")
