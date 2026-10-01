import hashlib,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from aidrax_signed_boot_chain.verify import verify
class Tests(unittest.TestCase):
 def test_hashes_verify(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d); data=b'a'; digest=hashlib.sha256(data).hexdigest()
   contract={'artifacts':{'shim-signed':{'sha256':digest},'grub-efi-amd64-signed':{'sha256':digest}}}; p=root/'contract.json';p.write_text(__import__('json').dumps(contract))
   (root/'shim-signed').write_bytes(data);(root/'grub-efi-amd64-signed').write_bytes(data)
   self.assertEqual('VERIFIED',verify(root,p)['status'])
 def test_missing_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d); p=root/'contract.json';p.write_text('{"artifacts":{"shim-signed":{"sha256":"00"}}}')
   self.assertEqual('BLOCKED',verify(root,p)['status'])
if __name__=='__main__':unittest.main()
