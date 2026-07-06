import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "source" / "core" / "logging"))

from enterprise_logger import EnterpriseLogger
from log_integrity import verify_log_file

logger = EnterpriseLogger(ROOT / "logs")
logger.log("INFO", "Build 007 runtime logging online", "runtime")
logger.log("SECURITY", "Security logging channel online", "security")
logger.log("AUDIT", "Audit logging channel online", "governance")
logger.log("PRIVACY", "Privacy logging channel online", "privacy")

required = [
    ROOT / "logs" / "runtime.log",
    ROOT / "logs" / "security.log",
    ROOT / "logs" / "audit.log",
    ROOT / "logs" / "privacy.log",
]

for p in required:
    assert p.exists(), f"missing log file: {p}"
    result = verify_log_file(p)
    assert result["status"] == "GREEN", result

print("BUILD007_LOGGING_TEST_GREEN")
