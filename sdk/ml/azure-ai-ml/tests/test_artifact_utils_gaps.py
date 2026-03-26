import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from azure.ai.ml.constants._common import DefaultOpenEncoding
from azure.ai.ml._utils._artifact_utils import ArtifactCache

def test_artifact_cache_singleton_initializes_once(monkeypatch):
    call_counts = {"value": 0}

    def fake_check():
        call_counts["value"] += 1

    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(fake_check))
    ArtifactCache._instance = None
    first = ArtifactCache()
    second = ArtifactCache()
    assert first is second
    assert call_counts["value"] == 1

def test_check_artifact_extension_raises_on_failure(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda value: value)

    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=1, stderr="extension missing")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError) as excinfo:
        ArtifactCache.check_artifact_extension()
    assert "Auto-installation failed" in str(excinfo.value)

def test_format_organization_name_replaces_invalid_chars():
    formatted = ArtifactCache._format_organization_name("org<>name")
    assert formatted == "org__name"

def test_get_organization_project_by_git_dev_azure_url(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda value: value)

    def fake_run(*args, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout="https://dev.azure.com/testorg/testproj\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    organization, project = ArtifactCache.get_organization_project_by_git()
    assert organization == "https://dev.azure.com/testorg"
    assert project == "testproj"

def test_get_organization_project_by_git_visualstudio_url(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda value: value)

    def fake_run(*args, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout="https://myorg.visualstudio.com/collection/testproj/_git/repo\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    organization, project = ArtifactCache.get_organization_project_by_git()
    assert organization == "https://myorg.visualstudio.com"
    assert project == "testproj"

def test_get_organization_project_by_git_non_git_directory(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda value: value)

    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="fatal: not a git repo")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError) as excinfo:
        ArtifactCache.get_organization_project_by_git()
    assert "fatal: not a git repo" in str(excinfo.value)

def test_get_organization_project_by_git_unrecognized_url_raises(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda value: value)

    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout="https://example.com/repo", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError) as excinfo:
        ArtifactCache.get_organization_project_by_git()
    assert "Cannot get organization and project" in str(excinfo.value)

def test_download_artifacts_raises_after_retries(monkeypatch):
    ArtifactCache._instance = None
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    cache = ArtifactCache()

    def fake_redirect(_organization):
        raise RuntimeError("redirect failure")

    cache._redirect_artifacts_tool_path = fake_redirect

    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=1, stderr="stderr", stdout="stdout")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError) as excinfo:
        cache._download_artifacts(["cmd"], None, "package", "1.0", "feed", max_retries=1)
    message = str(excinfo.value)
    assert "Download package package:1.0 from the feed feed failed 1 times" in message
    assert "stdout" in message

def test_check_artifacts_missing_directory_returns_false(tmp_path, monkeypatch):
    ArtifactCache._instance = None
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    cache = ArtifactCache()
    missing = tmp_path / "missing"
    assert cache._check_artifacts(missing) is False

def test_check_artifacts_checksum_mismatch_returns_false(tmp_path, monkeypatch):
    ArtifactCache._instance = None
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    cache = ArtifactCache()
    artifact_dir = tmp_path / "artifact"
    artifact_dir.mkdir()
    file_path = artifact_dir / "file.txt"
    file_path.write_text("content", encoding=DefaultOpenEncoding.WRITE)
    checksum_path = cache._get_checksum_path(artifact_dir)
    checksum_path.write_text("wrongvalue", encoding=DefaultOpenEncoding.WRITE)
    assert cache._check_artifacts(artifact_dir) is False

def test_check_artifacts_checksum_match_returns_true(tmp_path, monkeypatch):
    ArtifactCache._instance = None
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    cache = ArtifactCache()
    artifact_dir = tmp_path / "artifact"
    artifact_dir.mkdir()
    file_path = artifact_dir / "file.txt"
    file_path.write_text("content", encoding=DefaultOpenEncoding.WRITE)
    expected_hash = ArtifactCache.hash_files_content([file_path])
    checksum_path = cache._get_checksum_path(artifact_dir)
    checksum_path.write_text(expected_hash, encoding=DefaultOpenEncoding.WRITE)
    assert cache._check_artifacts(artifact_dir) is True

def test_set_calls_download_artifacts_on_artifacttool_missing(monkeypatch, tmp_path):
    ArtifactCache._instance = None
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", tmp_path / "cache")
    monkeypatch.setattr(shutil, "which", lambda value: value)

    temp_dirs = []

    def fake_mkdtemp():
        path = tmp_path / f"temp_{len(temp_dirs)}"
        path.mkdir(exist_ok=True)
        temp_dirs.append(path)
        return str(path)

    monkeypatch.setattr(tempfile, "mkdtemp", fake_mkdtemp)

    download_calls = []

    def fake_download(self, download_cmd, organization, name, version, feed, max_retries=3):
        download_calls.append(
            (download_cmd[:], organization, name, version, feed),
        )

    monkeypatch.setattr(ArtifactCache, "_download_artifacts", fake_download)

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=1,
            stderr="No such file or directory: /path/artifacttool",
            stdout="",
        ),
    )

    cache = ArtifactCache()
    artifact_path = cache.set(
        feed="feed",
        name="package",
        version="1.0",
        scope="project",
        organization="https://dev.azure.com/org",
        project="proj",
    )
    assert download_calls
    assert artifact_path.exists()
    checksum_file = artifact_path.parent / f"1.0_{ArtifactCache.POSTFIX_CHECKSUM}"
    assert checksum_file.exists()

def test_set_raises_runtime_error_when_download_fails(monkeypatch, tmp_path):
    ArtifactCache._instance = None
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", tmp_path / "cache")
    monkeypatch.setattr(shutil, "which", lambda value: value)

    temp_dirs = []

    def fake_mkdtemp():
        path = tmp_path / f"temp_{len(temp_dirs)}"
        path.mkdir(exist_ok=True)
        temp_dirs.append(path)
        return str(path)

    monkeypatch.setattr(tempfile, "mkdtemp", fake_mkdtemp)

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stderr="generic failure", stdout=""),
    )

    cache = ArtifactCache()
    with pytest.raises(RuntimeError) as excinfo:
        cache.set(
            feed="feed",
            name="package",
            version="1.0",
            scope="project",
            organization="https://dev.azure.com/org",
            project="proj",
        )
    assert "generic failure" in str(excinfo.value)

def test_set_handles_artifacttool_not_found_and_writes_checksum(tmp_path, monkeypatch):
    ArtifactCache._instance = None
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", lambda: None)
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", tmp_path / "cache_dir")
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/az")
    download_cmd = {}

    def fake_download_artifacts(self, download_cmd_arg, organization_arg, name_arg, version_arg, feed_arg, max_retries=3):
        download_cmd["cmd"] = list(download_cmd_arg)
        assert download_cmd["cmd"][-1] == "--debug"

    monkeypatch.setattr(ArtifactCache, "_download_artifacts", fake_download_artifacts)
    temp_calls = [
        {"path": tmp_path / "download_temp", "with_file": True},
        {"path": tmp_path / "checksum_temp", "with_file": False},
    ]

    def fake_mkdtemp(*args, **kwargs):
        if not temp_calls:
            raise RuntimeError("mkdtemp called more times than expected")
        info = temp_calls.pop(0)
        info["path"].mkdir(parents=True, exist_ok=True)
        if info["with_file"]:
            (info["path"] / "payload.txt").write_text("value")
        return str(info["path"])

    monkeypatch.setattr(tempfile, "mkdtemp", fake_mkdtemp)

    class FakeResult:
        def __init__(self):
            self.returncode = 1
            self.stderr = "No such file or directory: artifacttool"
            self.stdout = ""

    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: FakeResult())
    cache = ArtifactCache()
    returned_path = cache.set(
        feed="feed",
        name="package",
        version="1.0",
        scope="project",
        organization="https://example.visualstudio.com",
        project="proj",
    )
    expected_path = (
        cache.DEFAULT_DISK_CACHE_DIRECTORY
        / ArtifactCache._format_organization_name("https://example.visualstudio.com")
        / "proj"
        / "feed"
        / "package"
        / "1.0"
    )
    assert returned_path == expected_path
    assert expected_path.exists()
    checksum_path = expected_path.parent / f"1.0_{ArtifactCache.POSTFIX_CHECKSUM}"
    file_list = [path for path in expected_path.rglob("*") if path.is_file()]
    assert checksum_path.read_text() == ArtifactCache.hash_files_content(file_list)
    assert download_cmd["cmd"][-1] == "--debug"

def test_set_raises_runtime_error_when_download_fails_without_artifacttool_error(tmp_path, monkeypatch):
    ArtifactCache._instance = None
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", lambda: None)
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", tmp_path / "cache_dir")
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/az")

    def fake_mkdtemp(*args, **kwargs):
        path = tmp_path / "unused_temp"
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    monkeypatch.setattr(tempfile, "mkdtemp", fake_mkdtemp)

    class FakeResult:
        def __init__(self):
            self.returncode = 1
            self.stderr = "Some other error"
            self.stdout = ""

    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: FakeResult())
    cache = ArtifactCache()
    with pytest.raises(RuntimeError, match="Download package package:1.0 from the feed feed failed: Some other error"):
        cache.set(
            feed="feed",
            name="package",
            version="1.0",
            scope="project",
            organization="https://example.visualstudio.com",
            project="proj",
        )

def test_set_handles_os_rename_errors_and_still_returns_path(tmp_path, monkeypatch):
    ArtifactCache._instance = None
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", lambda: None)
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", tmp_path / "cache_dir")
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/az")
    temp_calls = [
        {"path": tmp_path / "download_temp", "with_file": True},
        {"path": tmp_path / "checksum_temp", "with_file": False},
    ]

    def fake_mkdtemp(*args, **kwargs):
        if not temp_calls:
            raise RuntimeError("mkdtemp called more times than expected")
        info = temp_calls.pop(0)
        info["path"].mkdir(parents=True, exist_ok=True)
        if info["with_file"]:
            (info["path"] / "payload.txt").write_text("value")
        return str(info["path"])

    monkeypatch.setattr(tempfile, "mkdtemp", fake_mkdtemp)

    class FakeResult:
        def __init__(self):
            self.returncode = 0
            self.stderr = ""
            self.stdout = ""

    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: FakeResult())
    original_rename = os.rename
    rename_calls = {"count": 0}

    def fake_rename(src, dst):
        rename_calls["count"] += 1
        if rename_calls["count"] == 1:
            raise FileExistsError("destination exists")
        original_rename(src, dst)

    monkeypatch.setattr(os, "rename", fake_rename)
    cache = ArtifactCache()
    returned_path = cache.set(
        feed="feed",
        name="package",
        version="1.0",
        scope="project",
        organization="https://example.visualstudio.com",
        project="proj",
    )
    expected_path = (
        cache.DEFAULT_DISK_CACHE_DIRECTORY
        / ArtifactCache._format_organization_name("https://example.visualstudio.com")
        / "proj"
        / "feed"
        / "package"
        / "1.0"
    )
    assert returned_path == expected_path
    assert rename_calls["count"] == 1
    assert not expected_path.exists()

def test_download_artifacts_retries_until_max_retries(monkeypatch):
    ArtifactCache._instance = None
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", lambda: None)
    cache = ArtifactCache()
    redirect_calls = {"count": 0}

    def fake_redirect(self, organization):
        redirect_calls["count"] += 1
        raise RuntimeError("redirect failure")

    monkeypatch.setattr(ArtifactCache, "_redirect_artifacts_tool_path", fake_redirect)
    run_calls = {"count": 0}

    class FakeResult:
        def __init__(self, seq):
            self.returncode = 1
            self.stderr = f"stderr {seq}"
            self.stdout = f"stdout {seq}"

    def fake_run(*args, **kwargs):
        run_calls["count"] += 1
        return FakeResult(run_calls["count"])

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="failed 1 times: stderr 1"):
        cache._download_artifacts(
            ["cmd"],
            "https://example.visualstudio.com",
            "package",
            "1.0",
            "feed",
            max_retries=1,
        )
    assert run_calls["count"] == 1
    assert redirect_calls["count"] == 1

def test_set_raises_runtime_error_when_download_command_fails_without_artifacttool_pattern(monkeypatch, tmp_path):
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", tmp_path / "cache")
    ArtifactCache._instance = None
    cache = ArtifactCache()
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stderr="unexpected failure", stdout=""),
    )
    with pytest.raises(RuntimeError) as excinfo:
        cache.set(feed="feed", name="name", version="1.0", scope="project", organization="https://org", project="proj")
    assert (
        "Download package name:1.0 from the feed feed failed: unexpected failure"
        == str(excinfo.value)
    )

def test_set_retries_download_artifacts_when_artifacttool_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", tmp_path / "cache")
    ArtifactCache._instance = None
    cache = ArtifactCache()
    org_project_calls = []

    def fake_get_org_project():
        org_project_calls.append(True)
        return "https://org.visualstudio.com", "project"

    monkeypatch.setattr(ArtifactCache, "get_organization_project_by_git", staticmethod(fake_get_org_project))
    download_calls = []

    def fake_download_artifacts(self, download_cmd, organization, name, version, feed):
        download_calls.append(list(download_cmd))

    monkeypatch.setattr(ArtifactCache, "_download_artifacts", fake_download_artifacts)
    tempdir_paths = [tmp_path / "tempdir", tmp_path / "checksum_temp"]
    mkdtemp_counter = 0

    def fake_mkdtemp():
        nonlocal mkdtemp_counter
        if mkdtemp_counter >= len(tempdir_paths):
            raise AssertionError("Unexpected mkdtemp call")
        path = tempdir_paths[mkdtemp_counter]
        path.mkdir(parents=True, exist_ok=True)
        if mkdtemp_counter == 0:
            (path / "dummy.txt").write_text("content")
        mkdtemp_counter += 1
        return str(path)

    monkeypatch.setattr(tempfile, "mkdtemp", fake_mkdtemp)

    class Result:
        def __init__(self, returncode, stderr="", stdout=""):
            self.returncode = returncode
            self.stderr = stderr
            self.stdout = stdout

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: Result(
            1, stderr="No such file or directory: /usr/bin/artifacttool", stdout=""
        ),
    )
    path = cache.set(feed="feed", name="name", version="1.0", scope="project")
    assert len(download_calls) == 1
    assert "--debug" in download_calls[0]
    assert len(org_project_calls) == 1
    expected_path = (
        Path(cache.DEFAULT_DISK_CACHE_DIRECTORY)
        / cache._format_organization_name("https://org.visualstudio.com")
        / "project"
        / "feed"
        / "name"
        / "1.0"
    ).absolute().resolve()
    assert path == expected_path
    checksum_path = expected_path.parent / f"1.0_{cache.POSTFIX_CHECKSUM}"
    assert checksum_path.exists()
    assert checksum_path.read_text().strip() == cache.hash_files_content(
        [str(expected_path / "dummy.txt")]
    )

def test_set_returns_path_even_if_rename_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", tmp_path / "cache")
    ArtifactCache._instance = None
    cache = ArtifactCache()
    version = "2.0"
    tempdir_paths = [tmp_path / "tempdir_fail", tmp_path / "checksum_fail"]
    mkdtemp_counter = 0

    def fake_mkdtemp():
        nonlocal mkdtemp_counter
        if mkdtemp_counter >= len(tempdir_paths):
            raise AssertionError("Unexpected mkdtemp call")
        path = tempdir_paths[mkdtemp_counter]
        path.mkdir(parents=True, exist_ok=True)
        if mkdtemp_counter == 0:
            (path / "dummy.txt").write_text("content")
        mkdtemp_counter += 1
        return str(path)

    monkeypatch.setattr(tempfile, "mkdtemp", fake_mkdtemp)
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stderr="", stdout=""),
    )
    expected_path = (
        Path(cache.DEFAULT_DISK_CACHE_DIRECTORY)
        / cache._format_organization_name("https://org.visualstudio.com")
        / "project"
        / "feed"
        / "name"
        / version
    )
    expected_resolved = expected_path.absolute()
    original_rename = os.rename
    rename_failed = False

    def fake_rename(src, dst):
        nonlocal rename_failed
        dst_str = os.fspath(dst)
        if dst_str.endswith(f"{version}_{cache.POSTFIX_CHECKSUM}"):
            return original_rename(src, dst)
        if not rename_failed and os.path.normpath(dst_str) == str(expected_resolved):
            rename_failed = True
            raise FileExistsError("target is in use")
        return original_rename(src, dst)

    monkeypatch.setattr(os, "rename", fake_rename)
    path = cache.set(
        feed="feed",
        name="name",
        version=version,
        scope="project",
        organization="https://org.visualstudio.com",
        project="project",
    )
    assert path == expected_resolved
    assert rename_failed
    assert not expected_resolved.exists()

def test_download_artifacts_warns_then_succeeds(monkeypatch):
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    ArtifactCache._instance = None
    cache = ArtifactCache()
    redirect_calls = []

    def fake_redirect(self, organization):
        redirect_calls.append(organization)
        raise ValueError("redirect failure")

    monkeypatch.setattr(ArtifactCache, "_redirect_artifacts_tool_path", fake_redirect)
    results = [
        SimpleNamespace(returncode=1, stderr="error1", stdout="stdout1"),
        SimpleNamespace(returncode=0, stderr="", stdout=""),
    ]
    run_calls = []

    def fake_run(*args, **kwargs):
        run_calls.append(args[0])
        return results.pop(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    cache._download_artifacts(["cmd"], "org", "name", "1.0", "feed", max_retries=2)
    assert len(redirect_calls) == 2
    assert len(run_calls) == 2

def test_download_artifacts_raises_after_multiple_retries(monkeypatch):
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    ArtifactCache._instance = None
    cache = ArtifactCache()
    monkeypatch.setattr(ArtifactCache, "_redirect_artifacts_tool_path", lambda self, organization: None)
    responses = [
        SimpleNamespace(returncode=1, stderr="err1", stdout="out1"),
        SimpleNamespace(returncode=1, stderr="err2", stdout="out2"),
    ]

    def fake_run(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError) as excinfo:
        cache._download_artifacts(["cmd"], "org", "name", "1.0", "feed", max_retries=2)
    assert "Download artifact debug info" in str(excinfo.value)
    assert "out2" in str(excinfo.value)

def test_download_artifacts_retries_and_handles_redirect_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    ArtifactCache._instance = None
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", tmp_path / "cache")
    cache = ArtifactCache()

    redirect_calls = []

    def fake_redirect(self, organization):
        redirect_calls.append(organization)
        if len(redirect_calls) == 1:
            raise RuntimeError("redirect fail")
    monkeypatch.setattr(ArtifactCache, "_redirect_artifacts_tool_path", fake_redirect)

    run_calls = []

    def fake_run(cmd, **kwargs):
        run_calls.append(cmd)
        if len(run_calls) == 1:
            return SimpleNamespace(returncode=1, stderr="retry", stdout="")
        return SimpleNamespace(returncode=0, stderr="", stdout="")
    monkeypatch.setattr(subprocess, "run", fake_run)

    cache._download_artifacts(["az", "artifacts"], "https://org.visualstudio.com", "package", "1.0", "feed", max_retries=2)

    assert len(redirect_calls) == 2
    assert len(run_calls) == 2

def test_download_artifacts_raises_after_exhausting_retries(monkeypatch, tmp_path):
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    ArtifactCache._instance = None
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", tmp_path / "cache")
    cache = ArtifactCache()

    redirect_count = {"value": 0}

    def fake_redirect(self, organization):
        redirect_count["value"] += 1
    monkeypatch.setattr(ArtifactCache, "_redirect_artifacts_tool_path", fake_redirect)

    def fake_run(cmd, **kwargs):
        return SimpleNamespace(returncode=1, stderr="fatal", stdout="info")
    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError) as excinfo:
        cache._download_artifacts(["az", "artifacts"], "https://dev.azure.com/org", "package", "1.0", "feed", max_retries=1)
    assert "Download package" in str(excinfo.value)
    assert redirect_count["value"] == 1

def test_set_handles_missing_org_project_and_writes_checksum(tmp_path, monkeypatch):
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    ArtifactCache._instance = None
    cache_dir = tmp_path / "cache"
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", cache_dir)
    monkeypatch.setattr(shutil, "which", lambda tool: "/usr/bin/git" if tool == "git" else "/usr/bin/az")
    monkeypatch.setattr(ArtifactCache, "get_organization_project_by_git", staticmethod(lambda: ("https://my<org>.visualstudio.com", "proj")))
    mkdtemp_calls = {"value": 0}

    def fake_mkdtemp():
        path = tmp_path / f"temp{mkdtemp_calls['value']}"
        path.mkdir(parents=True, exist_ok=True)
        if mkdtemp_calls["value"] == 0:
            (path / "payload.txt").write_text("data")
        mkdtemp_calls["value"] += 1
        return str(path)
    monkeypatch.setattr(tempfile, "mkdtemp", fake_mkdtemp)
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=0, stderr="", stdout=""))

    cache = ArtifactCache()
    artifact_path = cache.set(feed="feed", name="package", version="1.2.3", scope="project")

    payload_file = artifact_path / "payload.txt"
    assert payload_file.read_text() == "data"
    expected_checksum = ArtifactCache.hash_files_content([str(payload_file)])
    checksum_file = artifact_path.parent / f"1.2.3_{ArtifactCache.POSTFIX_CHECKSUM}"
    assert checksum_file.read_text() == expected_checksum
    sanitized_organization = ArtifactCache._format_organization_name("https://my<org>.visualstudio.com")
    expected_path = (cache_dir / sanitized_organization / "proj" / "feed" / "package" / "1.2.3").resolve()
    assert artifact_path == expected_path

def test_set_retries_after_artifacttool_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    ArtifactCache._instance = None
    cache_dir = tmp_path / "cache2"
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", cache_dir)
    monkeypatch.setattr(shutil, "which", lambda tool: "/usr/bin/az")
    mkdtemp_calls = {"value": 0}

    def fake_mkdtemp():
        path = tmp_path / f"temp_retry{mkdtemp_calls['value']}"
        path.mkdir(parents=True, exist_ok=True)
        if mkdtemp_calls["value"] == 0:
            (path / "retry.txt").write_text("retry payload")
        mkdtemp_calls["value"] += 1
        return str(path)
    monkeypatch.setattr(tempfile, "mkdtemp", fake_mkdtemp)

    download_calls = []

    def fake_download_artifacts(self, download_cmd, organization, name, version, feed, max_retries=3):
        download_calls.append(list(download_cmd))
    monkeypatch.setattr(ArtifactCache, "_download_artifacts", fake_download_artifacts)

    def fake_run(cmd, **kwargs):
        return SimpleNamespace(returncode=1, stderr="No such file or directory: /usr/bin/artifacttool", stdout="stdout")
    monkeypatch.setattr(subprocess, "run", fake_run)

    cache = ArtifactCache()
    artifact_path = cache.set(
        feed="feed",
        name="pkg",
        version="2.0",
        scope="organization",
        organization="https://org.visualstudio.com",
        project="proj",
    )

    assert len(download_calls) == 1
    assert "--debug" in download_calls[0]
    payload_file = artifact_path / "retry.txt"
    assert payload_file.read_text() == "retry payload"
    checksum_file = artifact_path.parent / f"2.0_{ArtifactCache.POSTFIX_CHECKSUM}"
    expected_checksum = ArtifactCache.hash_files_content([str(payload_file)])
    assert checksum_file.read_text() == expected_checksum

def test_set_ignores_rename_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(ArtifactCache, "check_artifact_extension", staticmethod(lambda: None))
    ArtifactCache._instance = None
    cache_dir = tmp_path / "cache3"
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", cache_dir)
    monkeypatch.setattr(shutil, "which", lambda tool: "/usr/bin/az")
    mkdtemp_calls = {"value": 0}

    def fake_mkdtemp():
        path = tmp_path / f"temp_error{mkdtemp_calls['value']}"
        path.mkdir(parents=True, exist_ok=True)
        if mkdtemp_calls["value"] == 0:
            (path / "error.txt").write_text("data")
        mkdtemp_calls["value"] += 1
        return str(path)
    monkeypatch.setattr(tempfile, "mkdtemp", fake_mkdtemp)

    rename_calls = {"value": 0}

    def fake_rename(src, dst):
        rename_calls["value"] += 1
        if rename_calls["value"] == 1:
            raise FileExistsError("dest already exists")
        return None
    monkeypatch.setattr(os, "rename", fake_rename)
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=0, stderr="", stdout=""))

    cache = ArtifactCache()
    artifact_path = cache.set(
        feed="feed",
        name="pkg",
        version="3.0",
        scope="project",
        organization="https://org.visualstudio.com",
        project="proj",
    )

    sanitized_organization = ArtifactCache._format_organization_name("https://org.visualstudio.com")
    expected_path = (cache_dir / sanitized_organization / "proj" / "feed" / "pkg" / "3.0").resolve()
    assert artifact_path == expected_path
    assert rename_calls["value"] == 1

def test_set_populates_cache_and_checksum(tmp_path, monkeypatch):
    monkeypatch.setattr(ArtifactCache, '_instance', None)
    monkeypatch.setattr(ArtifactCache, 'check_artifact_extension', staticmethod(lambda: None))
    monkeypatch.setattr(ArtifactCache, 'DEFAULT_DISK_CACHE_DIRECTORY', tmp_path / 'cache')
    monkeypatch.setattr(shutil, 'which', lambda _: '/bin/az')

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args, returncode=0, stdout='', stderr='')

    monkeypatch.setattr(subprocess, 'run', fake_run)

    download_dir = tmp_path / 'download-1'
    checksum_dir = tmp_path / 'checksum-1'
    mkdtemp_state = {'calls': 0}

    def fake_mkdtemp(*args, **kwargs):
        mkdtemp_state['calls'] += 1
        if mkdtemp_state['calls'] == 1:
            download_dir.mkdir(parents=True, exist_ok=True)
            (download_dir / 'payload.bin').write_bytes(b'payload')
            return str(download_dir)
        checksum_dir.mkdir(parents=True, exist_ok=True)
        return str(checksum_dir)

    monkeypatch.setattr(tempfile, 'mkdtemp', fake_mkdtemp)

    cache = ArtifactCache()
    result = cache.set(
        feed='feed',
        name='name',
        version='v1',
        scope='project',
        organization='https://contoso.visualstudio.com',
        project='proj',
    )

    expected_path = (
        ArtifactCache.DEFAULT_DISK_CACHE_DIRECTORY
        / ArtifactCache._format_organization_name('https://contoso.visualstudio.com')
        / 'proj'
        / 'feed'
        / 'name'
        / 'v1'
    )
    expected_absolute_path = expected_path.absolute().resolve()
    assert result == expected_absolute_path
    assert (expected_path / 'payload.bin').read_bytes() == b'payload'
    checksum_path = expected_path.parent / f'v1_{ArtifactCache.POSTFIX_CHECKSUM}'
    assert checksum_path.read_text() == ArtifactCache.hash_files_content([str(expected_path / 'payload.bin')])

def test_set_swallows_rename_error(tmp_path, monkeypatch):
    monkeypatch.setattr(ArtifactCache, '_instance', None)
    monkeypatch.setattr(ArtifactCache, 'check_artifact_extension', staticmethod(lambda: None))
    monkeypatch.setattr(ArtifactCache, 'DEFAULT_DISK_CACHE_DIRECTORY', tmp_path / 'cache')
    monkeypatch.setattr(shutil, 'which', lambda _: '/bin/az')

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args, returncode=0, stdout='', stderr='')

    monkeypatch.setattr(subprocess, 'run', fake_run)

    download_dir = tmp_path / 'download-2'
    checksum_dir = tmp_path / 'checksum-2'
    mkdtemp_state = {'calls': 0}

    def fake_mkdtemp(*args, **kwargs):
        mkdtemp_state['calls'] += 1
        if mkdtemp_state['calls'] == 1:
            download_dir.mkdir(parents=True, exist_ok=True)
            (download_dir / 'payload.bin').write_bytes(b'payload')
            return str(download_dir)
        checksum_dir.mkdir(parents=True, exist_ok=True)
        return str(checksum_dir)

    monkeypatch.setattr(tempfile, 'mkdtemp', fake_mkdtemp)

    real_rename = os.rename
    rename_state = {'count': 0}

    def fake_rename(src, dst):
        rename_state['count'] += 1
        if rename_state['count'] == 1:
            raise OSError('cannot rename')
        return real_rename(src, dst)

    monkeypatch.setattr(os, 'rename', fake_rename)

    cache = ArtifactCache()
    result = cache.set(
        feed='feed',
        name='name',
        version='v1',
        scope='project',
        organization='https://contoso.visualstudio.com',
        project='proj',
    )

    expected_path = (
        ArtifactCache.DEFAULT_DISK_CACHE_DIRECTORY
        / ArtifactCache._format_organization_name('https://contoso.visualstudio.com')
        / 'proj'
        / 'feed'
        / 'name'
        / 'v1'
    )
    expected_absolute_path = expected_path.absolute().resolve()
    assert result == expected_absolute_path
    assert rename_state['count'] == 1
    assert not expected_path.exists()
    checksum_path = expected_path.parent / f'v1_{ArtifactCache.POSTFIX_CHECKSUM}'
    assert not checksum_path.exists()
