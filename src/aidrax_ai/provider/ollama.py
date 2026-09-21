from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from .lifecycle import ProviderHealth
from .provider import Provider


class OllamaProvider(Provider):
    """Local advisory-only Ollama provider; never performs host actions."""

    def __init__(self, base_url: str = "http://127.0.0.1:11434"):
        self.base_url = base_url.rstrip("/")
        self.models = {
            "ai.chat": "llama3.2:latest",
            "ai.code": "qwen2.5-coder:7b",
        }
        self._ready = False

    def name(self) -> str:
        return "Ollama Local Advisory"

    def capabilities(self) -> tuple[str, ...]:
        return tuple(sorted(self.models))

    def initialize(self) -> None:
        self._tags()
        self._ready = True

    def health(self) -> ProviderHealth:
        if not self._ready:
            return ProviderHealth.DEGRADED
        try:
            self._tags()
            return ProviderHealth.HEALTHY
        except (OSError, URLError, ValueError):
            return ProviderHealth.UNHEALTHY

    def execute(self, capability: str, payload: dict):
        model = self.models[capability]
        prompt = payload.get("prompt", payload.get("text"))
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Ollama payload requires non-empty 'prompt' or 'text'")
        body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=120) as response:
            data = json.load(response)
        return {"text": data.get("response", ""), "model": model, "mode": "advisory"}

    def shutdown(self) -> None:
        self._ready = False

    def metadata(self) -> dict[str, object]:
        return {
            "backend": "ollama",
            "base_url": self.base_url,
            "models": dict(self.models),
            "mode": "advisory-only",
            "network_scope": "localhost",
        }

    def _tags(self) -> dict:
        with urlopen(f"{self.base_url}/api/tags", timeout=5) as response:
            data = json.load(response)
        if not isinstance(data, dict) or not isinstance(data.get("models"), list):
            raise ValueError("Ollama /api/tags returned an invalid response")
        installed = {item.get("name") for item in data["models"] if isinstance(item, dict)}
        missing = sorted(set(self.models.values()) - installed)
        if missing:
            raise ValueError("required Ollama models missing: " + ", ".join(missing))
        return data
