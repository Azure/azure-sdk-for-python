# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import pytest

from azure.ai.ml._utils._artifact_utils import ArtifactCache


_MODULE = "azure.ai.ml._utils._artifact_utils"
_OVERRIDE = "AZURE_DEVOPS_EXT_ARTIFACTTOOL_OVERRIDE_PATH"
_PARAMETERS = {
    "organization": "https://dev.azure.com/test-org",
    "project": "test project",
    "feed": "test-feed",
    "name": "test-package",
    "version": "1.2.3",
    "scope": "project",
}


@pytest.fixture(autouse=True)
def check_artifact_tool_environment():
    original = os.environ.get(_OVERRIDE)
    yield
    actual = os.environ.get(_OVERRIDE)
    assert actual == original, "Artifact tool override environment was not restored"


@pytest.fixture
def artifact_cache(tmp_path, monkeypatch, mocker):
    monkeypatch.setattr(ArtifactCache, "_instance", None)
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", tmp_path / "cache")
    mocker.patch.object(ArtifactCache, "check_artifact_extension")
    # Identity's import-time platform detection can run uname on Linux.
    mocker.patch("azure.identity.DefaultAzureCredential", side_effect=AssertionError("Unexpected credential access"))
    mocker.patch(f"{_MODULE}.shutil.which", return_value="az")
    mocker.patch(f"{_MODULE}.subprocess.run", side_effect=AssertionError("Unexpected process"))
    mocker.patch.object(
        ArtifactCache, "get_organization_project_by_git", return_value=(_PARAMETERS["organization"], "test project")
    )
    monkeypatch.delenv(_OVERRIDE, raising=False)
    yield ArtifactCache()
    os.environ.pop(_OVERRIDE, None)


@pytest.fixture
def download(artifact_cache, mocker):
    def write_package(command, **_kwargs):
        destination = Path(command[command.index("--path") + 1])
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "payload.txt").write_text("package content", encoding="utf-8")
        return SimpleNamespace(returncode=0, stderr="", stdout="")

    return mocker.patch(f"{_MODULE}.subprocess.run", side_effect=write_package)


@pytest.fixture
def tool_request(artifact_cache, mocker):
    credential = mocker.patch("azure.identity.DefaultAzureCredential")
    credential.return_value.get_token.return_value.token = "fake-token"
    pipeline = mocker.patch(f"{_MODULE}.HttpPipeline").return_value
    archive = BytesIO()
    with ZipFile(archive, "w") as zip_file:
        zip_file.writestr("artifacttool.exe" if os.name == "nt" else "artifacttool", "test tool; never executed")
    metadata = SimpleNamespace(
        status_code=200,
        json=lambda: {"uri": "https://downloads.example.test/artifacttool.zip"},
    )
    binary = SimpleNamespace(status_code=200, content=archive.getvalue())
    pipeline.get.side_effect = [metadata, binary]
    return credential, pipeline
