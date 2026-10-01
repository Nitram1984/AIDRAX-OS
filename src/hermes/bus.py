"""In-memory HERMES event transport for the Closed Alpha runtime."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Mapping
from time import monotonic
from typing import Any

from aidrax_core.config import Config, ConfigurationError
from aidrax_core.errors import (
    QueueOverflowError,
    RuntimeTypeError,
    RuntimeValidationError,
    SubscriberFailureError,
    SubscriberTimeoutError,
)
from aidrax_core.logging import get_logger

EventHandler = Callable[[Mapping[str, Any]], None]
_OVERFLOW_POLICIES = frozenset({"reject", "drop_oldest"})
_SUBSCRIBER_FAILURE_POLICIES = frozenset({"continue", "raise"})


class EventBus:
    """Publish structured events with bounded, policy-driven in-memory delivery."""

    def __init__(self, config: Config | None = None) -> None:
        """Create a configured in-memory bus without import-time side effects."""
        configuration = config if config is not None else Config.for_component("hermes")
        settings = configuration.load()
        queue_type = settings.get("queue", "memory")
        if queue_type != "memory":
            raise ConfigurationError("Closed Alpha supports only the 'memory' HERMES queue")
        self._capacity = self._positive_integer(settings.get("capacity", 256), "capacity")
        self._overflow_policy = self._policy(
            settings.get("overflow_policy", "reject"), _OVERFLOW_POLICIES, "overflow_policy"
        )
        self._subscriber_failure_policy = self._policy(
            settings.get("subscriber_failure_policy", "continue"),
            _SUBSCRIBER_FAILURE_POLICIES,
            "subscriber_failure_policy",
        )
        self._subscriber_timeout_seconds = self._timeout(settings.get("subscriber_timeout_seconds"))
        self.queue: deque[tuple[str, Mapping[str, Any]]] = deque()
        self.subscribers: dict[str, list[EventHandler]] = {}
        self._logger = get_logger("hermes.bus")

    @staticmethod
    def _positive_integer(value: object, name: str) -> int:
        """Validate one positive integer HERMES setting."""
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ConfigurationError(f"HERMES {name} must be a positive integer")
        return value

    @staticmethod
    def _policy(value: object, accepted: frozenset[str], name: str) -> str:
        """Validate one finite policy setting."""
        if not isinstance(value, str) or value not in accepted:
            accepted_values = ", ".join(sorted(accepted))
            raise ConfigurationError(f"HERMES {name} must be one of: {accepted_values}")
        return value

    @staticmethod
    def _timeout(value: object) -> float | None:
        """Validate the optional synchronous subscriber deadline."""
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ConfigurationError("HERMES subscriber_timeout_seconds must be a positive number or null")
        return float(value)

    def subscribe(self, event: str, handler: EventHandler) -> None:
        """Register a callable handler for one non-empty event name."""
        if not isinstance(event, str) or not event.strip():
            self._logger.error("subscription_failed", extra={"event": "hermes.subscription_failed"})
            raise RuntimeValidationError("event must be a non-empty string")
        if not callable(handler):
            self._logger.error("subscription_failed", extra={"event": "hermes.subscription_failed"})
            raise RuntimeTypeError("handler must be callable")
        self.subscribers.setdefault(event, []).append(handler)

    def publish(self, event: str, payload: Mapping[str, Any]) -> None:
        """Queue and deliver one event according to explicit overflow and failure policies."""
        self._validate_event(event, payload)
        self._reserve_capacity(event)
        self.queue.append((event, payload))
        for handler in self.subscribers.get(event, []):
            self._deliver(event, handler, payload)
        self._logger.info(
            "event_published",
            extra={
                "event": event,
                "pending": self.pending(),
                "subscriber_count": len(self.subscribers.get(event, [])),
            },
        )

    def _validate_event(self, event: str, payload: Mapping[str, Any]) -> None:
        """Validate the stable publish input contract before changing queue state."""
        if not isinstance(event, str) or not event.strip():
            self._logger.error("event_publish_failed", extra={"event": "hermes.event_publish_failed"})
            raise RuntimeValidationError("event must be a non-empty string")
        if not isinstance(payload, Mapping):
            self._logger.error("event_publish_failed", extra={"event": "hermes.event_publish_failed"})
            raise RuntimeTypeError("payload must be a mapping")

    def _reserve_capacity(self, event: str) -> None:
        """Apply the configured explicit overflow policy before appending an event."""
        if self.pending() < self._capacity:
            return
        if self._overflow_policy == "drop_oldest":
            dropped_event, _ = self.queue.popleft()
            self._logger.warning(
                "event_dropped",
                extra={"event": "hermes.event_dropped", "dropped_event": dropped_event, "next_event": event},
            )
            return
        self._logger.error(
            "queue_overflow",
            extra={"event": "hermes.queue_overflow", "capacity": self._capacity, "next_event": event},
        )
        raise QueueOverflowError(f"HERMES queue capacity reached: {self._capacity}")

    def _deliver(self, event: str, handler: EventHandler, payload: Mapping[str, Any]) -> None:
        """Deliver to one subscriber and apply the configured failure policy."""
        started_at = monotonic()
        try:
            handler(payload)
            elapsed = monotonic() - started_at
            if self._subscriber_timeout_seconds is not None and elapsed > self._subscriber_timeout_seconds:
                raise SubscriberTimeoutError(
                    f"subscriber exceeded {self._subscriber_timeout_seconds} seconds for event: {event}"
                )
        except BaseException as error:
            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise
            self._logger.error(
                "subscriber_failed",
                extra={
                    "event": "hermes.subscriber_failed",
                    "failure_code": error.code.value if isinstance(error, SubscriberTimeoutError) else "subscriber_failure",
                    "policy": self._subscriber_failure_policy,
                },
            )
            if self._subscriber_failure_policy == "raise":
                if isinstance(error, SubscriberTimeoutError):
                    raise
                raise SubscriberFailureError(f"subscriber failed for event: {event}", cause=error) from error

    def pending(self) -> int:
        """Return the number of events retained by this bounded in-memory bus."""
        return len(self.queue)
