from argus.scanner import ProjectScanner


def test_project_scanner_returns_reportable_projects(tmp_path):
    (tmp_path / "alpha").mkdir()
    projects = ProjectScanner().scan(tmp_path)

    assert [project.to_dict() for project in projects] == [
        {"name": "alpha", "path": str(tmp_path / "alpha")}
    ]
