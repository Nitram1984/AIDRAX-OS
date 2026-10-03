"""Bridge AO-026 exact-scope approvals into provider authorization."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any, Protocol


class OwnerGateReceipt(Protocol):
    request_id: str
    status: str
    scope_hash: str


class OwnerGateAdapter(Protocol):
    def submit(self, action: str, target: dict[str, str], rationale: str) -> OwnerGateReceipt: ...
    def approve(self, request_id: str, scope_hash: str, approved: bool) -> OwnerGateReceipt: ...


class OwnerGateAuthorizationBridge:
    """Convert AO-026 receipts into one-shot provider authorization tokens."""

    def __init__(self, agent: OwnerGateAdapter) -> None:
        self._agent = agent
        self._requests: dict[str, tuple[str, str, str]] = {}
        self._approved: set[tuple[str, str, str]] = set()

    def prepare(self, provider_id: str, capability: str, payload: dict[str, Any]) -> OwnerGateReceipt:
        scope = self._scope(provider_id, capability, payload)
        receipt = self._agent.submit(
            "ai.provider.execute",
            {"provider": provider_id, "capability": capability, "payload_sha256": scope[2]},
            "AIDRAX provider execution approval",
        )
        self._requests[receipt.request_id] = scope
        return receipt

    def approve(self, request_id: str, scope_hash: str, approved: bool) -> OwnerGateReceipt:
        receipt = self._agent.approve(request_id, scope_hash, approved)
        scope = self._requests.get(request_id)
        if scope is not None and receipt.status in {"APPROVED_FOR_DISPATCH", "GREEN"}:
            self._approved.add(scope)
        return receipt

    def __call__(self, provider_id: str, capability: str, payload: dict[str, Any]) -> bool:
        scope = self._scope(provider_id, capability, payload)
        if scope not in self._approved:
            return False
        self._approved.remove(scope)
        return True

    @staticmethod
    def _scope(provider_id: str, capability: str, payload: dict[str, Any]) -> tuple[str, str, str]:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
        digest = sha256(encoded.encode("utf-8")).hexdigest()
        return provider_id, capability, digest


__all__ = ["OwnerGateAuthorizationBridge"]
