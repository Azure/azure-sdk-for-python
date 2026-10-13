# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import os
from io import BytesIO
from types import SimpleNamespace
from zipfile import ZipFile

import pytest
from requests import Response
from test_utilities.artifact_fixtures import (
    _MODULE,
    _OVERRIDE,
    _PARAMETERS,
    artifact_cache,
    check_artifact_tool_environment,
    download,
    tool_request,
)

from azure.ai.ml._utils._artifact_utils import ArtifactCache
from azure.core.exceptions import HttpResponseError


pytestmark = [pytest.mark.unittest, pytest.mark.core_sdk_test]


@pytest.fixture
def cache_temp_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(f"{_MODULE}.tempfile.tempdir", str(tmp_path))


@pytest.mark.parametrize(
    "organization",
    [
        "https://example.test?.visualstudio.com",
        "https://example.test#.visualstudio.com",
        "https://dev.azure.com/example.test?ignored",
        "https://dev.azure.com/example.test#ignored",
        "https://example.test/https://dev.azure.com/test-org",
        "https://test-org.visualstudio.com.example.test",
        "https://test-org.visualstudio.com@evil.example.test",
        "https://user@dev.azure.com/test-org",
        "https://dev.azure.com/test-org/project",
        "https://dev.azure.com/test-org?x=1",
        "https://dev.azure.com/test-org?",
        "https://dev.azure.com/test-org#",
        "https://dev.azure.com/test%2Forg",
        "https://dev.azure.com/test\\org",
        "https://dev.azure.com/test-org\n",
        " https://dev.azure.com/test-org",
        "https://dev.azure.com:444/test-org",
        "https://dev.azure.com:invalid/test-org",
        "https://127.0.0.1/test-org",
        "https://[::1]/test-org",
        "http://dev.azure.com/test-org",
        "https://dev.azure.com/-test-org",
        "https://dev.azure.com/test-org-",
        "",
        42,
    ],
)
def test_invalid_organization_never_obtains_token(artifact_cache, tool_request, organization):
    credential, pipeline = tool_request
    pipeline.get.side_effect = [SimpleNamespace(status_code=403, text="test response")]
    with pytest.raises(ValueError, match="organization"):
        artifact_cache._redirect_artifacts_tool_path(organization)
    credential.assert_not_called()
    pipeline.get.assert_not_called()
    assert _OVERRIDE not in os.environ


@pytest.mark.parametrize(
    "organization",
    [
        "https://dev.azure.com/test-org",
        "https://dev.azure.com/test-org/",
        "https://DEV.AZURE.COM:443/TEST-ORG",
        "https://test-org.visualstudio.com",
        "https://TEST-ORG.VISUALSTUDIO.COM:443/",
        None,
    ],
)
def test_tool_request_is_canonical_and_token_is_not_forwarded(
    artifact_cache, tool_request, tmp_path, mocker, organization
):
    credential, pipeline = tool_request
    tool_path = tmp_path / "tool"
    tool_path.mkdir()
    mocker.patch(f"{_MODULE}.tempfile.mkdtemp", return_value=str(tool_path))
    artifact_cache._redirect_artifacts_tool_path(organization)

    credential.return_value.get_token.assert_called_once_with("https://management.azure.com/.default")
    os_name = "Windows" if os.name == "nt" else "Linux"
    assert pipeline.get.call_args_list[0].args == (
        "https://test-org.vsblob.visualstudio.com/_apis/clienttools/ArtifactTool/release?"
        f"osName={os_name}&arch=AMD64",
    )
    assert pipeline.get.call_args_list[0].kwargs == {
        "headers": {"Authorization": "Bearer fake-token"},
        "permit_redirects": False,
    }
    assert pipeline.get.call_args_list[1].args == ("https://downloads.example.test/artifacttool.zip",)
    assert pipeline.get.call_args_list[1].kwargs == {"permit_redirects": False}
    assert os.environ[_OVERRIDE] == str(tool_path.resolve())
    tool_name = "artifacttool.exe" if os.name == "nt" else "artifacttool"
    assert (tool_path / tool_name).is_file()
    artifact_cache._redirect_artifacts_tool_path(organization)
    assert pipeline.get.call_count == 2
    assert credential.call_count == 1


@pytest.mark.parametrize(
    "uri",
    [
        "http://downloads.example.test/tool.zip",
        "//downloads.example.test/tool.zip",
        "file:///tmp/tool.zip",
        "https://user@downloads.example.test/tool.zip",
        "https://downloads.example.test:444/tool.zip",
        "https://downloads.example.test:invalid/tool.zip",
        "https://[invalid/tool.zip",
        "https://downloads.example.test/tool.zip#fragment",
        "https://downloads.example.test\\@example.test/tool.zip",
        "https://downloads.example.test/tool.zip\n",
        "https:///tool.zip",
        "",
        None,
        42,
    ],
)
def test_invalid_tool_download_url_is_rejected(artifact_cache, tool_request, uri):
    _, pipeline = tool_request
    pipeline.get.side_effect = [SimpleNamespace(status_code=200, json=lambda: {"uri": uri})]
    with pytest.raises(ValueError, match="download"):
        artifact_cache._redirect_artifacts_tool_path(_PARAMETERS["organization"])
    assert pipeline.get.call_count == 1
    assert _OVERRIDE not in os.environ


@pytest.mark.parametrize("metadata", [{}, [], None, "invalid"])
def test_invalid_tool_metadata_is_rejected(artifact_cache, tool_request, metadata):
    _, pipeline = tool_request
    pipeline.get.side_effect = [SimpleNamespace(status_code=200, json=lambda: metadata)]
    with pytest.raises(ValueError, match="download"):
        artifact_cache._redirect_artifacts_tool_path(_PARAMETERS["organization"])
    assert pipeline.get.call_count == 1
    assert _OVERRIDE not in os.environ


@pytest.mark.parametrize("request_index", [0, 1])
@pytest.mark.parametrize("status_code", [302, 307, 403, 500])
def test_failed_or_redirected_tool_requests_do_not_install(artifact_cache, tool_request, request_index, status_code):
    _, pipeline = tool_request
    responses = [
        SimpleNamespace(status_code=200, json=lambda: {"uri": "https://downloads.example.test/tool.zip"}),
        SimpleNamespace(status_code=200, content=b"unused"),
    ]
    responses[request_index] = SimpleNamespace(status_code=status_code, reason="test response")
    pipeline.get.side_effect = responses
    with pytest.raises(HttpResponseError):
        artifact_cache._redirect_artifacts_tool_path(_PARAMETERS["organization"])
    assert pipeline.get.call_count == request_index + 1
    assert _OVERRIDE not in os.environ


@pytest.mark.parametrize("request_index", [0, 1])
def test_real_http_pipeline_does_not_follow_redirects(artifact_cache, mocker, request_index):
    credential = mocker.patch("azure.identity.DefaultAzureCredential")
    credential.return_value.get_token.return_value.token = "fake-token"
    metadata = Response()
    metadata.status_code = 200
    metadata._content = json.dumps({"uri": "https://downloads.example.test/tool.zip"}).encode("utf-8")
    metadata.raw = BytesIO(metadata._content)
    redirect = Response()
    redirect.status_code = 302
    redirect.reason = "Found"
    redirect.headers["Location"] = "https://untrusted.example.test/"
    redirect._content = b""
    redirect.raw = BytesIO()
    request = mocker.patch(
        "requests.sessions.Session.request", side_effect=[metadata, redirect] if request_index else [redirect]
    )

    with pytest.raises(HttpResponseError):
        artifact_cache._redirect_artifacts_tool_path(_PARAMETERS["organization"])

    assert request.call_count == request_index + 1
    assert request.call_args_list[0].kwargs["headers"]["Authorization"] == "Bearer fake-token"
    if request_index:
        assert "Authorization" not in request.call_args_list[1].kwargs["headers"]
    for call in request.call_args_list:
        assert call.args[1] != redirect.headers["Location"]
        assert call.kwargs["allow_redirects"] is False
    assert _OVERRIDE not in os.environ


def test_rejected_archive_does_not_install_tool(artifact_cache, tool_request, tmp_path, mocker):
    _, pipeline = tool_request
    archive = BytesIO()
    with ZipFile(archive, "w") as zip_file:
        zip_file.writestr("../outside", "test content")
    pipeline.get.side_effect = [
        SimpleNamespace(status_code=200, json=lambda: {"uri": "https://downloads.example.test/tool.zip"}),
        SimpleNamespace(status_code=200, content=archive.getvalue()),
    ]
    staging = tmp_path / "tool"
    staging.mkdir()
    mocker.patch(f"{_MODULE}.tempfile.mkdtemp", return_value=str(staging))

    with pytest.raises(RuntimeError, match="path traversal"):
        artifact_cache._redirect_artifacts_tool_path(_PARAMETERS["organization"])

    assert not staging.exists()
    assert not (tmp_path / "outside").exists()
    assert _OVERRIDE not in os.environ
    assert artifact_cache._artifacts_tool_path is None


@pytest.mark.parametrize("layout", ["empty", "unrelated", "nested", "directory"])
@pytest.mark.parametrize("existing_override", [None, "pre-existing-tool"])
def test_archive_without_executable_does_not_install_tool(
    artifact_cache, tool_request, tmp_path, mocker, monkeypatch, layout, existing_override
):
    _, pipeline = tool_request
    tool_name = "artifacttool.exe" if os.name == "nt" else "artifacttool"
    members = {
        "empty": [],
        "unrelated": ["readme.txt"],
        "nested": [f"bin/{tool_name}"],
        "directory": [f"{tool_name}/"],
    }[layout]
    archive = BytesIO()
    with ZipFile(archive, "w") as zip_file:
        for member in members:
            zip_file.writestr(member, "test tool; never executed")
    pipeline.get.side_effect = [
        SimpleNamespace(status_code=200, json=lambda: {"uri": "https://downloads.example.test/tool.zip"}),
        SimpleNamespace(status_code=200, content=archive.getvalue()),
    ]
    staging = tmp_path / "tool"
    staging.mkdir()
    mocker.patch(f"{_MODULE}.tempfile.mkdtemp", return_value=str(staging))
    if existing_override is not None:
        monkeypatch.setenv(_OVERRIDE, existing_override)

    with pytest.raises(RuntimeError, match="archive does not contain"):
        artifact_cache._redirect_artifacts_tool_path(_PARAMETERS["organization"])

    assert pipeline.get.call_count == 2
    assert not staging.exists()
    assert os.environ.get(_OVERRIDE) == existing_override
    assert artifact_cache._artifacts_tool_path is None


def test_fallback_does_not_swallow_validation_errors(artifact_cache, tool_request, mocker):
    credential, _ = tool_request
    run = mocker.patch(f"{_MODULE}.subprocess.run", side_effect=AssertionError("Unexpected retry"))
    with pytest.raises(ValueError, match="organization"):
        artifact_cache._download_artifacts(
            ["az", "artifacts"], "https://example.test?.visualstudio.com", "package", "1.0.0", "feed"
        )
    run.assert_not_called()
    credential.assert_not_called()


@pytest.mark.usefixtures("cache_temp_directory")
def test_missing_tool_fallback_rejects_invalid_organization(artifact_cache, tool_request, mocker):
    credential, pipeline = tool_request
    run = mocker.patch(
        f"{_MODULE}.subprocess.run",
        return_value=SimpleNamespace(returncode=1, stderr="No such file or directory: artifacttool", stdout=""),
    )
    with pytest.raises(ValueError, match="organization"):
        artifact_cache.set(**dict(_PARAMETERS, organization="https://example.test?.visualstudio.com"))
    assert run.call_count == 1
    credential.assert_not_called()
    pipeline.get.assert_not_called()
    assert _OVERRIDE not in os.environ


@pytest.mark.usefixtures("cache_temp_directory")
def test_download_enters_fallback_only_for_missing_artifacttool(artifact_cache, download, mocker):
    write_package = download.side_effect
    fallback = mocker.patch.object(artifact_cache, "_redirect_artifacts_tool_path")
    download.side_effect = [
        SimpleNamespace(returncode=1, stderr="No such file or directory: artifacttool", stdout=""),
        SimpleNamespace(returncode=0, stderr="", stdout=""),
    ]

    def write_after_fallback(*_args):
        command = download.call_args.args[0]
        write_package(command)

    fallback.side_effect = write_after_fallback
    assert artifact_cache.set(**_PARAMETERS).is_dir()
    fallback.assert_called_once_with(_PARAMETERS["organization"])
    assert download.call_count == 2


@pytest.mark.usefixtures("cache_temp_directory")
def test_unrelated_download_failure_does_not_obtain_token(artifact_cache, tool_request, mocker):
    credential, pipeline = tool_request
    mocker.patch(
        f"{_MODULE}.subprocess.run",
        return_value=SimpleNamespace(returncode=1, stderr="package does not exist", stdout=""),
    )
    with pytest.raises(RuntimeError, match="package does not exist"):
        artifact_cache.set(**_PARAMETERS)
    credential.assert_not_called()
    pipeline.get.assert_not_called()


@pytest.mark.parametrize("member", ["../outside", "/outside"])
def test_safe_extractall_rejects_traversal(tmp_path, member):
    archive = BytesIO()
    with ZipFile(archive, "w") as zip_file:
        zip_file.writestr(member, "test content")
    archive.seek(0)
    with ZipFile(archive) as zip_file, pytest.raises(RuntimeError, match="path traversal"):
        ArtifactCache._safe_extractall(zip_file, tmp_path / "extracted")
    assert not (tmp_path / "outside").exists()
