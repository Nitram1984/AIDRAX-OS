import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aidrax_ai.provider.capability import AIProviderCapability
from aidrax_ai.provider.catalog import ProviderBinding, ProviderCatalog
from aidrax_ai.provider.errors import ProviderAuthorizationError, ProviderRegistrationError
from aidrax_ai.provider.factory import ProviderFactory
from aidrax_ai.provider.lifecycle import ProviderHealth
from aidrax_ai.provider.provider import Provider
from aidrax_ai.provider.runtime import ProviderRuntime
from aidrax_ai.provider.secrets import EnvironmentSecretResolver
from aidrax_core.capabilities.contracts import CapabilityHealth
from aidrax_os.runtime import AIProviderService, OwnerGateAuthorizationBridge
from atlas.registry import Registry


class _Receipt:
    def __init__(self, request_id, status, scope_hash):
        self.request_id = request_id
        self.status = status
        self.scope_hash = scope_hash


class _OwnerGate:
    def __init__(self):
        self._scope_hash = "scope"

    def submit(self, action, target, rationale):
        self.last_target = target
        return _Receipt("request-1", "PENDING_OWNER", self._scope_hash)

    def approve(self, request_id, scope_hash, approved):
        status = "APPROVED_FOR_DISPATCH" if approved and scope_hash == self._scope_hash else "RED/STOP"
        return _Receipt(request_id, status, self._scope_hash)


class FakeProvider(Provider):
    def __init__(self, name="Local AI", gated=False):
        self._name = name
        self._gated = gated
        self.started = False

    def name(self):
        return self._name

    def capabilities(self):
        return ("ai.chat",)

    def initialize(self):
        self.started = True

    def health(self):
        return ProviderHealth.HEALTHY if self.started else ProviderHealth.DEGRADED

    def execute(self, capability, payload):
        return {"provider": self._name, "echo": payload["text"]}

    def shutdown(self):
        self.started = False

    def owner_gate_required(self, capability):
        return self._gated


class ProviderRuntimeTests(unittest.TestCase):
    def test_register_initialize_and_execute(self):
        runtime = ProviderRuntime()
        self.assertEqual(runtime.register(FakeProvider(), "local-ai"), "local-ai")
        runtime.initialize_all()
        self.assertEqual(runtime.execute("ai.chat", {"text": "hello"})["echo"], "hello")
        self.assertEqual(runtime.status("local-ai")["state"], "READY")

    def test_capability_collision_is_rejected(self):
        runtime = ProviderRuntime()
        runtime.register(FakeProvider("one"), "one")
        with self.assertRaises(ProviderRegistrationError):
            runtime.register(FakeProvider("two"), "two")

    def test_owner_gate_is_enforced(self):
        runtime = ProviderRuntime()
        runtime.register(FakeProvider(gated=True), "gated")
        runtime.initialize_all()
        with self.assertRaises(ProviderAuthorizationError):
            runtime.execute("ai.chat", {"text": "blocked"})
        allowed = ProviderRuntime(authorization=lambda provider_id, capability, payload: True)
        allowed.register(FakeProvider(gated=True), "gated")
        allowed.initialize_all()
        self.assertEqual(allowed.execute("ai.chat", {"text": "go"})["echo"], "go")

    def test_restart_safe_catalog_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            catalog = ProviderCatalog(Path(directory) / "providers.json")
            catalog.save((ProviderBinding("local-ai", "local"),))
            runtime = ProviderRuntime()
            runtime.restore(catalog, ProviderFactory({"local": FakeProvider}))
            self.assertEqual(runtime.status("local-ai")["state"], "READY")
            self.assertIn("ai.chat", runtime.capabilities())

    def test_canonical_capability_adapter(self):
        runtime = ProviderRuntime()
        runtime.register(FakeProvider(), "local-ai")
        adapter = AIProviderCapability(runtime)
        adapter.initialize()
        adapter.activate()
        self.assertEqual(adapter.health(), CapabilityHealth.HEALTHY)
        adapter.deactivate()
        self.assertEqual(adapter.health(), CapabilityHealth.DEGRADED)

    def test_os_service_composes_provider_runtime_through_capability_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = ProviderRuntime()
            runtime.register(FakeProvider(), "local-ai")
            service = AIProviderService(
                config_directory="config",
                registry=Registry(Path(directory) / "registry.json"),
                provider_runtime=runtime,
            )
            statuses = service.start()
            self.assertEqual(statuses[0].state.value, "READY")
            self.assertTrue(service.status()["started"])
            self.assertEqual(service.execute("ai.chat", {"text": "hello"})["echo"], "hello")
            service.stop()

    def test_environment_secret_resolver_is_runtime_only(self):
        resolver = EnvironmentSecretResolver()
        key = resolver.key("xai-watchlist", "api-key")
        self.assertEqual(key, "AIDRAX_PROVIDER_XAI_WATCHLIST_API_KEY")
        with patch.dict(os.environ, {key: "test-secret"}, clear=False):
            self.assertEqual(resolver.resolve("xai-watchlist", "api-key"), "test-secret")
        self.assertIsNone(resolver.resolve("xai-watchlist", "api-key"))

    def test_owner_gate_bridge_consumes_exact_scope_once(self):
        agent = _OwnerGate()
        bridge = OwnerGateAuthorizationBridge(agent)
        payload = {"text": "approved prompt"}
        receipt = bridge.prepare("cloud-ai", "ai.chat", payload)
        self.assertEqual(receipt.status, "PENDING_OWNER")
        self.assertNotIn("approved prompt", str(agent.last_target))
        bridge.approve(receipt.request_id, receipt.scope_hash, True)
        self.assertTrue(bridge("cloud-ai", "ai.chat", payload))
        self.assertFalse(bridge("cloud-ai", "ai.chat", payload))
        self.assertFalse(bridge("cloud-ai", "ai.chat", {"text": "different"}))


if __name__ == "__main__":
    unittest.main()
