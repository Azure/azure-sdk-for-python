from pathlib import Path
import re

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.mark.parametrize(
    "template",
    [
        ("eng", "pipelines", "tsp-spec-sync.yml"),
        ("scripts", "issue_helper", "issue_helper.yml"),
        ("eng", "pipelines", "templates", "stages", "archetype-python-release.yml"),
        ("eng", "pipelines", "templates", "stages", "archetype-sdk-tool-python.yml"),
        ("eng", "pipelines", "templates", "stages", "release-artifact.yml"),
    ],
)
def test_standalone_pipeline_python_tasks_have_explicit_versions(template):
    configuration = yaml.safe_load(REPO_ROOT.joinpath(*template).read_text())
    versions = []

    def collect(node):
        if isinstance(node, dict):
            if node.get("task") == "UsePythonVersion@0":
                versions.append(node["inputs"]["versionSpec"])
            for value in node.values():
                collect(value)
        elif isinstance(node, list):
            for value in node:
                collect(value)

    collect(configuration)
    assert versions
    for version in versions:
        match = re.match(r"^(\d+)\.(\d+)", str(version))
        if match:
            assert tuple(map(int, match.groups())) >= (3, 11)
