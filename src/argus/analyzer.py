from pathlib import Path
from datetime import datetime


class ProjectAnalyzer:

    LANGUAGE_EXTENSIONS = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".kt": "Kotlin",
        ".go": "Go",
        ".rs": "Rust",
        ".cpp": "C++",
        ".c": "C",
        ".h": "C",
        ".hpp": "C++",
        ".cs": "C#",
        ".html": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".toml": "TOML",
        ".sh": "Shell",
        ".md": "Markdown",
    }

    CONFIG_FILES = {
        ".gitignore",
        ".env",
        ".editorconfig",
        ".prettierrc",
        ".eslintrc",
    }

    def analyze(self, project):

        languages = set()
        build_files = []
        config_files = []

        total_size = 0
        newest = 0

        for file in project.path.rglob("*"):

            if not file.is_file():
                continue

            try:
                stat = file.stat()
            except OSError:
                continue

            total_size += stat.st_size

            if stat.st_mtime > newest:
                newest = stat.st_mtime

            ext = file.suffix.lower()

            if ext in self.LANGUAGE_EXTENSIONS:
                languages.add(self.LANGUAGE_EXTENSIONS[ext])

            if file.name in {
                "pyproject.toml",
                "package.json",
                "Cargo.toml",
                "go.mod",
                "pom.xml",
                "build.gradle",
                "Dockerfile",
                "docker-compose.yml",
                "compose.yml",
            }:
                build_files.append(file.name)

            if file.name in self.CONFIG_FILES:
                config_files.append(file.name)

        project.languages = sorted(languages)
        project.build_files = sorted(set(build_files))
        project.config_files = sorted(set(config_files))
        project.size_bytes = total_size

        if newest:
            project.last_modified = datetime.fromtimestamp(newest)

        return project
