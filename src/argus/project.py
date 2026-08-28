from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

@dataclass(slots=True)
class Project:

    name: str
    path: Path

    project_type: str = "unknown"

    git_repository: bool = False

    languages: list[str] = field(default_factory=list)

    build_files: list[str] = field(default_factory=list)

    config_files: list[str] = field(default_factory=list)

    size_bytes: int = 0

    last_modified: datetime | None = None

    def to_dict(self):

        return {

            "name": self.name,

            "path": str(self.path),

            "project_type": self.project_type,

            "git_repository": self.git_repository,

            "languages": self.languages,

            "build_files": self.build_files,

            "config_files": self.config_files,

            "size_bytes": self.size_bytes,

            "last_modified": (
                self.last_modified.isoformat()
                if self.last_modified
                else None
            ),
        }
