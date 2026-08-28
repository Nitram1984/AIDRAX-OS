"""Deterministic, capability-aware node routing for AIDRAX OS.

This module is adapted from the Build-003.1 architecture reference.  It owns
neither persistent state nor event delivery: callers provide the canonical
state adapter (ATLAS-backed in production) and the HERMES event sink.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet, Mapping, Optional, Protocol, Sequence


class HealthState(str, Enum):
    """Verified availability state of a node agent."""

    READY = "READY"
    DEGRADED = "DEGRADED"
    UNREACHABLE = "UNREACHABLE"
    RECOVERING = "RECOVERING"
    OFFLINE = "OFFLINE"
    QUARANTINED = "QUARANTINED"


ROUTABLE_STATES = frozenset({HealthState.READY, HealthState.DEGRADED})


@dataclass(frozen=True)
class Node:
    """One node candidate with its verified capability claim."""

    node_id: str
    health: HealthState
    capabilities: FrozenSet[str]
    load: int = 0


@dataclass(frozen=True)
class Job:
    """A logical job whose ID is its idempotency boundary."""

    job_id: str
    required_capability: str
    owner_approved: bool = False
    protected_action: bool = False


class RoutingState(Protocol):
    """State boundary to be backed by the canonical persistent core state."""

    def register(self, job_id: str) -> bool:
        """Create the job once and return whether this call created it."""
        ...

    def status(self, job_id: str) -> str:
        """Return the authoritative lifecycle status for one job."""
        ...

    def set_status(self, job_id: str, status: str) -> None:
        """Persist one validated lifecycle transition."""
        ...

    def assignment(self, job_id: str) -> Optional[str]:
        """Return the node holding the authoritative assignment, if any."""
        ...

    def assign(self, job_id: str, node_id: str) -> None:
        """Persist the selected node for the job."""
        ...


class EventSink(Protocol):
    """Minimal HERMES-compatible event publishing boundary."""

    def publish(self, event: str, payload: Mapping[str, object]) -> None:
        """Publish a structured routing lifecycle event."""
        ...


@dataclass
class CircuitBreaker:
    """Node-local breaker that prevents immediate re-dispatch after failures."""

    failure_threshold: int = 3
    cooldown_ticks: int = 2
    failures: int = 0
    open_until: int = 0

    def allows(self, tick: int) -> bool:
        """Return whether the breaker permits dispatch at this logical tick."""
        return tick >= self.open_until

    def success(self) -> None:
        """Clear consecutive failures after a verified node result."""
        self.failures = 0

    def failure(self, tick: int) -> None:
        """Record a failure and open the breaker at the configured threshold."""
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.open_until = tick + self.cooldown_ticks
            self.failures = 0


class NodeRouter:
    """Select a suitable node without bypassing AIDRAX state or Owner-Gates."""

    def __init__(self, state: RoutingState, events: EventSink) -> None:
        """Bind the policy to canonical state and a HERMES-compatible event sink."""
        self._state = state
        self._events = events
        self._breakers: dict[str, CircuitBreaker] = {}
        self._tick = 0

    def dispatch(self, job: Job, nodes: Sequence[Node]) -> Optional[str]:
        """Dispatch once, or retain the original job in a safe waiting state."""

        self._validate_job(job)
        self._tick += 1
        is_new = self._state.register(job.job_id)
        if not is_new and self._state.status(job.job_id) not in {"PENDING", "RETRY"}:
            return self._state.assignment(job.job_id)

        if job.protected_action and not job.owner_approved:
            self._state.set_status(job.job_id, "WAITING_OWNER_GATE")
            self._publish(job.job_id, "owner_gate_required")
            return None

        candidates = [
            node
            for node in nodes
            if node.health in ROUTABLE_STATES
            and job.required_capability in node.capabilities
            and self._breaker(node.node_id).allows(self._tick)
        ]
        if not candidates:
            self._state.set_status(job.job_id, "WAITING_FOR_CAPABLE_NODE")
            self._publish(job.job_id, "no_capable_node")
            return None

        chosen = min(
            candidates,
            key=lambda node: (node.health != HealthState.READY, node.load, node.node_id),
        )
        self._state.assign(job.job_id, chosen.node_id)
        self._state.set_status(job.job_id, "DISPATCHED")
        self._publish(job.job_id, "dispatched", node_id=chosen.node_id)
        return chosen.node_id

    def report_result(self, job_id: str, node_id: str, succeeded: bool) -> None:
        """Apply a matching result while preserving the original job identity."""

        if self._state.assignment(job_id) != node_id:
            raise ValueError("result does not match the authoritative assignment")
        if succeeded:
            self._breaker(node_id).success()
            self._state.set_status(job_id, "COMPLETED")
            self._publish(job_id, "completed", node_id=node_id)
            return

        self._breaker(node_id).failure(self._tick)
        self._state.set_status(job_id, "RETRY")
        self._publish(job_id, "retry_same_job_id", node_id=node_id)

    def _breaker(self, node_id: str) -> CircuitBreaker:
        """Return the stable node-local breaker, creating it on first use."""
        return self._breakers.setdefault(node_id, CircuitBreaker())

    def _publish(self, job_id: str, phase: str, **details: object) -> None:
        """Emit a namespaced lifecycle event without exposing internal state."""
        self._events.publish(
            f"routing.{phase}", {"job_id": job_id, "phase": phase, **details}
        )

    @staticmethod
    def _validate_job(job: Job) -> None:
        """Reject malformed job identities before they reach the state adapter."""
        if not job.job_id.strip():
            raise ValueError("job_id must be a non-empty string")
        if not job.required_capability.strip():
            raise ValueError("required_capability must be a non-empty string")
