from __future__ import annotations
import gzip, hashlib, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from aidrax_rootfs_runtime_closure.resolve import closure
def stanza(name, version, depends=""):
    return "\n".join([f"Package: {name}", "Architecture: amd64", f"Version: {version}", *( [f"Depends: {depends}"] if depends else []), f"Filename: pool/{name}.deb", "Size: 1", f"SHA256: {'a'*64}"])
class ClosureTests(unittest.TestCase):
 def test_resolves_transitive_dependencies(self):
  with tempfile.TemporaryDirectory() as directory:
   index=Path(directory)/"Packages.gz"
   with gzip.open(index,"wt") as stream: stream.write("\n\n".join([stanza("kernel","1","modules, initramfs"),stanza("modules","1"),stanza("initramfs","1","busybox | busybox-static"),stanza("busybox","1")]))
   contract={"root_packages":{"kernel":"1"},"alternative_preferences":{"busybox|busybox-static":"busybox"},"snapshot":{"packages_url":"https://example.invalid"}}
   result=closure(index,contract)
  self.assertEqual([x["name"] for x in result["artifacts"]],["busybox","initramfs","kernel","modules"])
