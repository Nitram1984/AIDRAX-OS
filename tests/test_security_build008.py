import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "source" / "core" / "security"))
from security_runtime import SecurityRuntime

result = SecurityRuntime().smoke_test()
print("=== Build 008 Security Test ===")
print(result)
assert result["status"] == "GREEN"
assert result["owner_gate"]["owner"]["allowed"] is True
assert result["owner_gate"]["agent"]["allowed"] is False
print("BUILD008_SECURITY_TEST_GREEN")
