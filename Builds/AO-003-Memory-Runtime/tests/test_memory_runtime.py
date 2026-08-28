import pathlib, sys, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from aidrax_memory import MemoryRuntime, MemoryRuntimeError
class Registry:
    def __init__(self): self.records=[]
    def add(self, component): self.records.append(component)
class Events:
    def __init__(self): self.items=[]
    def publish(self, event, payload): self.items.append((event,payload))
class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.registry=Registry(); self.events=Events()
        self.runtime=MemoryRuntime(pathlib.Path(self.temp.name)/"memory.jsonl",self.registry,self.events); self.runtime.start()
    def tearDown(self): self.temp.cleanup()
    def test_remember_recall_and_restore(self):
        entry=self.runtime.remember("mission.control","Review AO-003",("roadmap",))
        self.assertEqual(self.runtime.recall("mission.control","ao-003"),(entry,))
        restored=MemoryRuntime(pathlib.Path(self.temp.name)/"memory.jsonl",Registry(),Events()); restored.start()
        self.assertEqual(restored.recall("mission.control"),(entry,))
    def test_tombstone_hides_entry_after_restore(self):
        entry=self.runtime.remember("mission.control","temporary")
        self.runtime.forget(entry.entry_id)
        self.assertEqual(self.runtime.recall("mission.control"),())
        self.assertEqual(self.events.items[-1][0],"memory.entry_forgotten")
    def test_invalid_namespace_is_rejected(self):
        with self.assertRaises(MemoryRuntimeError): self.runtime.remember("Mission Control","x")
if __name__ == "__main__": unittest.main()
