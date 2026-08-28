from pathlib import Path
from argus.scanner import scan

def test_empty(tmp_path):
 assert scan(tmp_path)==[]
