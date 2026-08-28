import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidrax_os import boot_plan


class PlatformContractTests(unittest.TestCase):
    def test_boot_plan_has_canonical_authorities_in_order(self):
        plan = boot_plan()
        self.assertLess(plan.index("ATLAS"), plan.index("HERMES"))
        self.assertLess(plan.index("HERMES"), plan.index("ARGUS"))
        self.assertLess(plan.index("ARGUS"), plan.index("CapabilityRuntime"))

    def test_json_boot_contract_agrees_with_python_boundary(self):
        contract = json.loads((ROOT / "platform" / "boot-order.json").read_text())
        declared = tuple(item["component"] for item in contract["boot_sequence"])
        self.assertEqual(declared, boot_plan())


if __name__ == "__main__":
    unittest.main()
