import json, pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from aidrax_live_boot import BootContract
class ContractTests(unittest.TestCase):
 def test_live_desktop_is_safe_default(self):
  contract=BootContract(json.loads((ROOT/'config/boot-contract.json').read_text()))
  self.assertEqual(contract.entry('live-desktop').next_surface,'AIDRAX_DESKTOP')
  self.assertEqual(contract.entry('install').persistent_storage,'owner-gated')
 def test_contract_rejects_non_live_default(self):
  with self.assertRaises(ValueError): BootContract({'schema_version':1,'default_entry':'install','entries':{}})
