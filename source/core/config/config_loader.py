
import json
from pathlib import Path
def load_config(path):
    return json.loads(Path(path).read_text())
