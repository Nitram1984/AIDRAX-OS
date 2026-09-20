"""Fail-closed owner-gate state machine with no platform authority by default."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Callable, Mapping
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class ActionRequest:
    request_id: str
    action: str
    target: Mapping[str, str]
    rationale: str
    scope_hash: str


@dataclass(frozen=True, slots=True)
class GateReceipt:
    request_id: str
    status: str
    scope_hash: str
    detail: str


class OwnerGateAgent:
    """Prepare, approve and report requests; execution is opt-in and injected."""

    def __init__(self, *, executor: Callable[[ActionRequest], str] | None = None, auto_apply: bool = False) -> None:
        if not isinstance(auto_apply, bool):
            raise TypeError("auto_apply must be a boolean")
        self._executor = executor
        self._auto_apply = auto_apply
        self._requests: dict[str, ActionRequest] = {}

    @property
    def status(self) -> str:
        return "PREPARED" if self._executor is None else "INACTIVE"

    def submit(self, action: str, target: Mapping[str, str], rationale: str) -> GateReceipt:
        self._validate_text(action, "action")
        self._validate_text(rationale, "rationale")
        normalized = self._target(target)
        scope_hash = self._scope_hash(action, normalized, rationale)
        request = ActionRequest(str(uuid4()), action, normalized, rationale, scope_hash)
        self._requests[request.request_id] = request
        return GateReceipt(request.request_id, "PENDING_OWNER", scope_hash, "Awaiting exact-scope Owner-Gate approval")

    def approve(self, request_id: str, scope_hash: str, approved: bool) -> GateReceipt:
        request = self._requests.get(request_id)
        if request is None:
            raise KeyError("unknown request")
        if not approved:
            return GateReceipt(request_id, "RED/STOP", request.scope_hash, "Owner-Gate denied")
        if scope_hash != request.scope_hash:
            return GateReceipt(request_id, "RED/STOP", request.scope_hash, "Owner-Gate scope mismatch")
        if not self._auto_apply or self._executor is None:
            return GateReceipt(request_id, "APPROVED_FOR_DISPATCH", request.scope_hash, "Prepared only; no executor activation")
        detail = self._executor(request)
        return GateReceipt(request_id, "GREEN", request.scope_hash, detail)

    @staticmethod
    def _validate_text(value: str, name: str) -> None:
        if not isinstance(value, str) or not value.strip() or len(value) > 512:
            raise ValueError(f"{name} must be non-empty and at most 512 characters")

    @classmethod
    def _target(cls, target: Mapping[str, str]) -> Mapping[str, str]:
        if not isinstance(target, Mapping) or not target:
            raise ValueError("target must be a non-empty mapping")
        normalized = {str(key): str(value) for key, value in target.items()}
        if any(not key.strip() or not value.strip() for key, value in normalized.items()):
            raise ValueError("target keys and values must be non-empty")
        return dict(sorted(normalized.items()))

    @staticmethod
    def _scope_hash(action: str, target: Mapping[str, str], rationale: str) -> str:
        material = "\n".join((action, rationale, *(f"{key}={value}" for key, value in target.items())))
        return sha256(material.encode("utf-8")).hexdigest()
