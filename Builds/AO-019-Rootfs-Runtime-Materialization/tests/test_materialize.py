import hashlib,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"));from aidrax_rootfs_runtime_materialization.materialize import verify
class Tests(unittest.TestCase):
 def test_matching_package_verifies(self):
  with tempfile.TemporaryDirectory() as directory:
   value=b"aidrax";path=Path(directory)/"x.deb";path.write_bytes(value);lock={"artifacts":[{"filename":"pool/x.deb","size":len(value),"sha256":hashlib.sha256(value).hexdigest()}]};self.assertTrue(verify(Path(directory),lock))
