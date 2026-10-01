from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable


@dataclass(slots=True)
class ModuleInfo:
    name: str
    version: str
    author: str
    description: str = ""


class ModuleRegistry:
    """
    Zentrale Modul-Registry von AIDRAX OS.
    Verwaltet alle registrierten Core- und Systemmodule.
    """

    def __init__(self):
        self._modules: Dict[str, ModuleInfo] = {}

    def register(self, module: ModuleInfo) -> None:
        if module.name in self._modules:
            raise ValueError(
                f"Module '{module.name}' is already registered."
            )

        self._modules[module.name] = module

    def unregister(self, name: str) -> None:
        self._modules.pop(name, None)

    def exists(self, name: str) -> bool:
        return name in self._modules

    def get(self, name: str) -> ModuleInfo | None:
        return self._modules.get(name)

    def list(self) -> Iterable[ModuleInfo]:
        return sorted(
            self._modules.values(),
            key=lambda m: m.name.lower()
        )

    def count(self) -> int:
        return len(self._modules)

    def clear(self) -> None:
        self._modules.clear()

    def to_dict(self):

        return {
            module.name: {
                "version": module.version,
                "author": module.author,
                "description": module.description,
            }
            for module in self._modules.values()
        }
