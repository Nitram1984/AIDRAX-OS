import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidrax_brand_experience import ExperienceEngine


EVENTS = {"POWER_ON": "boot", "BOOT_COMPLETE": "login", "LOGIN_READY": "desktop", "UPDATE_SUCCEEDED": "update-success", "SHUTDOWN_REQUESTED": "shutdown"}


class ExperienceEngineTests(unittest.TestCase):
    def test_cue_is_inert_and_deterministic(self):
        cue = ExperienceEngine(EVENTS).cue_for("POWER_ON")
        self.assertEqual((cue.event, cue.scene, cue.status), ("POWER_ON", "boot", "PENDING_ADAPTER"))

    def test_incomplete_or_unknown_lifecycle_is_rejected(self):
        with self.assertRaises(ValueError): ExperienceEngine({"POWER_ON": "boot"})
        with self.assertRaises(ValueError): ExperienceEngine(EVENTS).cue_for("FORMAT")


if __name__ == "__main__":
    unittest.main()
