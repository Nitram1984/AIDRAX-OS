import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from aidrax_platform_integration import CapabilityBootstrap
class Runtime:
    def __init__(self): self.starts=self.stops=0
    def discover_and_activate(self): self.starts+=1;return ["ready"]
    def shutdown(self): self.stops+=1;return ["inactive"]
class Tests(unittest.TestCase):
    def test_start_is_idempotent_and_stop_delegates(self):
        runtime=Runtime();boot=CapabilityBootstrap(runtime)
        self.assertEqual(boot.start(),("ready",));self.assertEqual(boot.start(),("ready",));self.assertEqual(runtime.starts,1)
        self.assertEqual(boot.stop(),("inactive",));self.assertEqual(runtime.stops,1);self.assertEqual(boot.status(),())
if __name__=="__main__":unittest.main()
