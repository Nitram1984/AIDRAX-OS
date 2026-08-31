import hashlib,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"));from aidrax_rootfs_assembly.assemble import assemble
class Tests(unittest.TestCase):
 def test_existing_target_blocks(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);base=root/"base";base.write_bytes(b"bad");target=root/"target";target.mkdir()
   with self.assertRaisesRegex(ValueError,"target exists"):assemble(base,root,{"artifacts":[]},root,target,hashlib.sha256(b"bad").hexdigest())
