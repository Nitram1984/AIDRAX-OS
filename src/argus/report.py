from pathlib import Path
import json


class ReportWriter:

    @staticmethod
    def write(projects, output: Path):

        output.parent.mkdir(parents=True, exist_ok=True)

        with output.open("w", encoding="utf-8") as f:
            json.dump(
                [project.to_dict() for project in projects],
                f,
                indent=2,
                ensure_ascii=False,
            )
