import json
from pathlib import Path

class Config:

    def __init__(self):
        self.data = {}

    def load(self, filename):
        path = Path(filename)

        with path.open("r", encoding="utf-8") as f:
            self.data = json.load(f)

        return self.data

    def get(self, key, default=None):
        return self.data.get(key, default)
