import json

from argus.report import ReportWriter
from argus.scanner import ProjectScanner


def test_report_writer_exports_projects(tmp_path):
    (tmp_path / "alpha").mkdir()
    output = tmp_path / "reports" / "projects.json"

    ReportWriter.write(ProjectScanner().scan(tmp_path), output)

    assert json.loads(output.read_text(encoding="utf-8")) == [
        {"name": "alpha", "path": str(tmp_path / "alpha")}
    ]
