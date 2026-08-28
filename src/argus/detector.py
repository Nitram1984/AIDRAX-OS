from pathlib import Path

PROJECT_SIGNATURES = {
    "python": ["pyproject.toml", "requirements.txt", "setup.py"],
    "node": ["package.json"],
    "rust": ["Cargo.toml"],
    "go": ["go.mod"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "docker": ["Dockerfile", "docker-compose.yml", "compose.yml"],
    "flatpak": ["flatpak-builder.json"],
    "snap": ["snapcraft.yaml"],
}


class ProjectDetector:

    def detect(self, directory: Path) -> str:

        if not directory.is_dir():
            return "unknown"

        for project_type, signatures in PROJECT_SIGNATURES.items():
            for signature in signatures:
                if (directory / signature).exists():
                    return project_type

        return "unknown"

    def is_git_repository(self, directory: Path) -> bool:

        return (directory / ".git").exists()
