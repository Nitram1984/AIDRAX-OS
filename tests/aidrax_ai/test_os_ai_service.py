import json
import tempfile
import unittest
from pathlib import Path

from aidrax_ai.provider.lifecycle import ProviderHealth
from aidrax_ai.provider.provider import Provider
from aidrax_ai.provider.runtime import ProviderRuntime
from aidrax_os.runtime import AIProviderService
from atlas.registry import Registry


class FakeProvider(Provider):
    def __init__(self):
        self.ready = False

    def name(self):
        return "Test AI"

    def capabilities(self):
        return ("ai.test",)

    def initialize(self):
        self.ready = True

    def shutdown(self):
        self.ready = False

    def health(self):
        return ProviderHealth.HEALTHY if self.ready else ProviderHealth.DEGRADED

    def execute(self, capability, payload):
        return payload


class AIProviderServiceTests(unittest.TestCase):
    def test_start_execute_status_stop(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "capability-manifests").mkdir()
            (root / "capabilities.json").write_text(
                json.dumps({"granted_permissions": [], "discovery_directories": []}),
                encoding="utf-8",
            )
            manifest = {
                "id": "ai-provider-runtime",
                "name": "AIDRAX AI Provider Runtime",
                "version": "1.0.0",
                "description": "test",
                "author": "AIDRAX Intelligence",
                "dependencies": [],
                "permissions": [],
                "health": "HEALTHY",
                "priority": 50,
                "supported_interfaces": ["ai.provider.runtime"],
            }
            manifest_path = root / "capability-manifests" / "aidrax-ai-provider-runtime.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            providers = ProviderRuntime()
            providers.register(FakeProvider(), "test-ai")
            service = AIProviderService(
                config_directory=root,
                registry=Registry(root / "registry.json"),
                provider_runtime=providers,
            )
            started = service.start()
            self.assertEqual(started[0].state.value, "READY")
            self.assertEqual(service.execute("ai.test", {"ok": True}), {"ok": True})
            self.assertTrue(service.status()["started"])
            service.stop()
            self.assertFalse(service.status()["started"])


if __name__ == "__main__":
    unittest.main()
