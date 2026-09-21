import tempfile
import unittest
from pathlib import Path

from aidrax_ai.provider.capability import AIProviderCapability
from aidrax_ai.provider.catalog import ProviderBinding, ProviderCatalog
from aidrax_ai.provider.errors import ProviderAuthorizationError, ProviderRegistrationError
from aidrax_ai.provider.factory import ProviderFactory
from aidrax_ai.provider.lifecycle import ProviderHealth
from aidrax_ai.provider.provider import Provider
from aidrax_ai.provider.runtime import ProviderRuntime
from aidrax_core.capabilities.contracts import CapabilityHealth


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


if __name__ == "__main__":
    unittest.main()
