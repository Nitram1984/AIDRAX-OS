
import re, hashlib

SECRET_PATTERNS = [
    re.compile(r'(?i)(password|passwd|token|secret|api[_-]?key)\s*[:=]\s*([^\s]+)'),
    re.compile(r'(?i)bearer\s+[A-Za-z0-9._\-]+'),
]
INJECTION_PATTERNS = [
    re.compile(r'(?i)ignore (all|previous) instructions'),
    re.compile(r'(?i)system prompt'),
    re.compile(r'(?i)developer message'),
    re.compile(r'(?i)bypass .*safety'),
]

def redact_secrets(text):
    out=text
    for p in SECRET_PATTERNS:
        out=p.sub(lambda m: (m.group(1)+": [REDACTED]") if m.lastindex and m.lastindex>=1 else "[REDACTED]",out)
    return out

def detect_injection(text):
    hits=[p.pattern for p in INJECTION_PATTERNS if p.search(text)]
    return hits

def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8",errors="ignore")).hexdigest()
