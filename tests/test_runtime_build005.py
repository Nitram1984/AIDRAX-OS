import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "source" / "core" / "kernel"))

from runtime import AidraxRuntime

runtime = AidraxRuntime()
report = runtime.boot()
assert report["status"] == "GREEN", report
assert report["build"] == "005", report
assert "health_monitor" in report, report
print("BUILD005_RUNTIME_TEST_GREEN")
