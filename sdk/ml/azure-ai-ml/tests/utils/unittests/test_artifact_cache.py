# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import errno
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import PureWindowsPath
from threading import Event

import pytest

from azure.ai.ml._utils._artifact_utils import ArtifactCache
from azure.ai.ml.entities._component._additional_includes import AdditionalIncludes
from test_utilities.artifact_fixtures import (
    _MODULE,
    _PARAMETERS,
    artifact_cache,
    check_artifact_tool_environment,
    download,
)


pytestmark = [pytest.mark.unittest, pytest.mark.core_sdk_test]


def _cache_path(cache, parameters):
    return (
        cache.cache_directory
        / cache._format_organization_name(parameters["organization"])
        / parameters["project"]
        / parameters["feed"]
        / parameters["name"]
        / parameters["version"]
    )


def _directory_link(link, target, run=subprocess.run):
    if os.name == "nt":
        run(
            [os.environ["COMSPEC"], "/c", "mklink", "/J", str(link), str(target)],
            check=True,
            capture_output=True,
        )
    else:
        link.symlink_to(target, target_is_directory=True)


@pytest.mark.parametrize("method", ["get", "set"])
@pytest.mark.parametrize("field", ["project", "feed", "name", "version"])
@pytest.mark.parametrize(
    "value",
    [
        "",
        ".",
        "..",
        "../outside",
        r"..\outside",
        "/outside",
        r"\outside",
        r"C:\outside",
        "C:outside",
        r"\\server\share",
        r"\\?\C:\outside",
        "name:stream",
        "name.",
        "name ",
        "NUL",
        "CON.txt",
        "NUL.*",
        "CON.*",
        "name\x00",
        "name\n",
        "name\t",
        "name?",
        "name|",
        42,
    ],
)
def test_invalid_cache_components_rejected_before_access(artifact_cache, tmp_path, mocker, method, field, value):
    parameters = dict(_PARAMETERS, **{field: value})
    check = mocker.patch.object(artifact_cache, "_check_artifacts", side_effect=AssertionError("Unexpected cache read"))
    run = mocker.patch(f"{_MODULE}.subprocess.run", side_effect=AssertionError("Unexpected process"))
    staging = mocker.patch(f"{_MODULE}.tempfile.mkdtemp", return_value=str(tmp_path / "unused"))

    with pytest.raises(ValueError, match="Artifact"):
        getattr(artifact_cache, method)(**parameters)

    check.assert_not_called()
    run.assert_not_called()
    staging.assert_not_called()


@pytest.mark.parametrize("field", ["feed", "name", "version"])
def test_required_cache_components_cannot_be_none(artifact_cache, mocker, field):
    run = mocker.patch(f"{_MODULE}.subprocess.run")
    with pytest.raises(ValueError, match="Artifact"):
        artifact_cache.get(**dict(_PARAMETERS, **{field: None}), resolve=False)
    run.assert_not_called()


@pytest.mark.parametrize("organization", ["", 42])
def test_cache_rejects_invalid_organization_type(artifact_cache, organization):
    with pytest.raises(ValueError, match="organization"):
        artifact_cache.get(**dict(_PARAMETERS, organization=organization), resolve=False)


@pytest.mark.parametrize("method", ["get", "set"])
def test_cache_rejects_absolute_paths_without_touching_outside_files(artifact_cache, tmp_path, mocker, method):
    outside = tmp_path / "outside"
    outside.mkdir()
    canary = outside / "canary.txt"
    canary.write_text("unchanged", encoding="utf-8")
    run = mocker.patch(f"{_MODULE}.subprocess.run", side_effect=AssertionError("Unexpected process"))

    with pytest.raises(ValueError, match="Artifact"):
        getattr(artifact_cache, method)(**dict(_PARAMETERS, version=str(outside)))

    assert canary.read_text(encoding="utf-8") == "unchanged"
    assert list(outside.iterdir()) == [canary]
    run.assert_not_called()


@pytest.mark.parametrize("method", ["get", "set"])
def test_cache_rejects_directory_links_outside_root(artifact_cache, tmp_path, mocker, method):
    outside = tmp_path / "cache-other"
    outside.mkdir()
    canary = outside / "canary.txt"
    canary.write_text("unchanged", encoding="utf-8")
    organization_path = artifact_cache.cache_directory / artifact_cache._format_organization_name(
        _PARAMETERS["organization"]
    )
    _directory_link(organization_path, outside)
    run = mocker.patch(f"{_MODULE}.subprocess.run", side_effect=AssertionError("Unexpected process"))

    with pytest.raises(ValueError, match="cache"):
        getattr(artifact_cache, method)(**_PARAMETERS)

    assert canary.read_text(encoding="utf-8") == "unchanged"
    assert list(outside.iterdir()) == [canary]
    run.assert_not_called()


def test_cache_rejects_checksum_link_outside_root(artifact_cache, tmp_path, mocker):
    path = _cache_path(artifact_cache, _PARAMETERS)
    path.mkdir(parents=True)
    checksum = artifact_cache._get_checksum_path(path)
    outside = tmp_path / "outside"
    outside.mkdir()
    _directory_link(checksum, outside)
    run = mocker.patch(f"{_MODULE}.subprocess.run")

    with pytest.raises(ValueError, match="cache"):
        artifact_cache.get(**_PARAMETERS)

    assert outside.is_dir()
    run.assert_not_called()


@pytest.mark.parametrize("scope", ["project", "organization"])
def test_cache_download_checksum_and_hit(artifact_cache, download, scope):
    parameters = dict(_PARAMETERS, scope=scope)
    path = artifact_cache.get(**parameters)
    assert path == _cache_path(artifact_cache, parameters).resolve()
    assert (path / "payload.txt").read_text(encoding="utf-8") == "package content"
    assert artifact_cache._check_artifacts(path)
    assert artifact_cache.get(**parameters) == path
    assert download.call_count == 1
    command = download.call_args.args[0]
    assert command[command.index("--scope") + 1] == scope


def test_cache_resolve_false_does_not_download(artifact_cache, download):
    assert artifact_cache.get(**_PARAMETERS, resolve=False) is None
    download.assert_not_called()


def test_cache_defaults_are_resolved_before_download(artifact_cache, download):
    parameters = {key: value for key, value in _PARAMETERS.items() if key not in ("organization", "project")}
    path = artifact_cache.set(**parameters)
    assert path == _cache_path(artifact_cache, _PARAMETERS).resolve()
    command = download.call_args.args[0]
    assert command[command.index("--org") + 1] == _PARAMETERS["organization"]
    assert command[command.index("--project") + 1] == _PARAMETERS["project"]


def test_invalid_cache_is_replaced(artifact_cache, download):
    path = artifact_cache.get(**_PARAMETERS)
    (path / "payload.txt").write_text("stale", encoding="utf-8")
    assert artifact_cache.get(**_PARAMETERS) == path
    assert artifact_cache._check_artifacts(path)
    assert (path / "payload.txt").read_text(encoding="utf-8") == "package content"
    assert download.call_count == 2


@pytest.mark.parametrize("version", ["*", "1.*", "1.2.*", "1.2.3-preview.1"])
def test_version_selectors_have_safe_distinct_cache_keys(artifact_cache, download, version):
    path = artifact_cache.get(**dict(_PARAMETERS, version=version))
    assert "*" not in path.name
    assert artifact_cache._check_artifacts(path)
    assert artifact_cache.get(**dict(_PARAMETERS, version=version)) == path
    command = download.call_args.args[0]
    assert command[command.index("--version") + 1] == version
    if "*" in version:
        literal_path = artifact_cache.get(**dict(_PARAMETERS, version=version.replace("*", "%2A")))
        assert literal_path != path


@pytest.mark.parametrize(
    "version, cache_name", [("*", "%2A"), ("1.*", "1.%2A"), ("1.2.*", "1.2.%2A"), ("%2A", "%252A")]
)
def test_reserved_filename_check_uses_encoded_cache_component(mocker, version, cache_name):
    windows_path = mocker.patch(f"{_MODULE}.PureWindowsPath", wraps=PureWindowsPath)

    assert ArtifactCache._cache_path_component(version, "version") == cache_name
    windows_path.assert_called_once_with(cache_name)


def test_cache_preserves_project_spaces_and_unicode(artifact_cache, download):
    parameters = dict(_PARAMETERS, project="Research \u03b1")
    path = artifact_cache.get(**parameters)
    assert path == _cache_path(artifact_cache, parameters).resolve()
    assert artifact_cache._check_artifacts(path)


def test_cache_does_not_hide_storage_errors(artifact_cache, download, mocker):
    mocker.patch(f"{_MODULE}.os.rename", side_effect=PermissionError("test write denied"))
    with pytest.raises(PermissionError, match="test write denied"):
        artifact_cache.set(**_PARAMETERS)
    assert not list(artifact_cache.cache_directory.glob("tmp*"))


def test_download_reports_missing_azure_cli(artifact_cache, download, mocker):
    mocker.patch(f"{_MODULE}.shutil.which", return_value=None)
    with pytest.raises(RuntimeError, match="Azure CLI is required"):
        artifact_cache.set(**_PARAMETERS)
    download.assert_not_called()
    assert not list(artifact_cache.cache_directory.iterdir())


def test_constructor_reports_missing_azure_cli(tmp_path, monkeypatch, mocker):
    cache_directory = tmp_path / "cache"
    monkeypatch.setattr(ArtifactCache, "_instance", None)
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", cache_directory)
    mocker.patch(f"{_MODULE}.shutil.which", return_value=None)
    run = mocker.patch(f"{_MODULE}.subprocess.run", side_effect=AssertionError("Unexpected process"))

    for _ in range(2):
        with pytest.raises(RuntimeError, match="Azure CLI is required"):
            ArtifactCache()
        assert ArtifactCache._instance is None

    run.assert_not_called()
    assert not cache_directory.exists()


def test_constructor_retries_extension_check_after_failure(tmp_path, monkeypatch, mocker):
    monkeypatch.setattr(ArtifactCache, "_instance", None)
    monkeypatch.setattr(ArtifactCache, "DEFAULT_DISK_CACHE_DIRECTORY", tmp_path / "cache")
    mocker.patch(f"{_MODULE}.shutil.which", return_value="az")
    run = mocker.patch(f"{_MODULE}.subprocess.run", side_effect=[mocker.Mock(returncode=1), mocker.Mock(returncode=0)])

    with pytest.raises(RuntimeError, match="Auto-installation failed"):
        ArtifactCache()
    assert ArtifactCache._instance is None

    cache = ArtifactCache()
    assert ArtifactCache._instance is cache
    assert cache.cache_directory.is_dir()
    assert run.call_count == 2
    run.assert_called_with(["az", "artifacts", "--help", "--yes"], capture_output=True, check=False)


def test_direct_set_preserves_an_existing_valid_cache(artifact_cache, download):
    path = artifact_cache.set(**_PARAMETERS)
    assert artifact_cache.set(**_PARAMETERS) == path
    assert artifact_cache._check_artifacts(path)
    assert not list(artifact_cache.cache_directory.glob("tmp*"))


@pytest.mark.parametrize("method", ["get", "set"])
def test_concurrent_cache_writer_waits_for_checksum(artifact_cache, download, mocker, method):
    contender_cache = object.__new__(ArtifactCache)
    contender_cache.__init__(cache_directory=artifact_cache.cache_directory)
    checksum_pending = Event()
    collision_checked = Event()
    publish_checksum = Event()
    replace = os.replace
    check_artifacts = contender_cache._check_artifacts

    def paused_replace(source, destination):
        checksum_pending.set()
        assert publish_checksum.wait(timeout=5)
        replace(source, destination)

    def checked_collision(path):
        valid = check_artifacts(path)
        if not valid:
            collision_checked.set()
        return valid

    mocker.patch(f"{_MODULE}.os.replace", side_effect=paused_replace)
    mocker.patch.object(contender_cache, "_check_artifacts", side_effect=checked_collision)
    with ThreadPoolExecutor(max_workers=2) as executor:
        winner = executor.submit(artifact_cache.set, **_PARAMETERS)
        try:
            assert checksum_pending.wait(timeout=5)
            contender = executor.submit(getattr(contender_cache, method), **_PARAMETERS)
            assert collision_checked.wait(timeout=5)
        finally:
            publish_checksum.set()
        path = winner.result(timeout=5)
        assert contender.result(timeout=5) == path

    assert artifact_cache._check_artifacts(path)
    assert download.call_count == (1 if method == "get" else 2)
    assert not list(artifact_cache.cache_directory.glob("tmp*"))


def test_get_retries_incomplete_cache_before_replacing(artifact_cache, download, mocker):
    path = _cache_path(artifact_cache, _PARAMETERS)
    path.mkdir(parents=True)
    (path / "incomplete.txt").write_text("incomplete", encoding="utf-8")
    sleep = mocker.patch(f"{_MODULE}.time.sleep")

    assert artifact_cache.get(**_PARAMETERS) == path.resolve()

    assert sleep.call_count == artifact_cache._CACHE_PUBLISH_RETRIES
    assert all(call.args == (artifact_cache._CACHE_PUBLISH_RETRY_DELAY,) for call in sleep.call_args_list)
    assert artifact_cache._check_artifacts(path)
    assert not (path / "incomplete.txt").exists()
    assert download.call_count == 1
    assert not list(artifact_cache.cache_directory.glob("tmp*"))


def test_get_rechecks_publication_after_final_retry(artifact_cache, download, mocker):
    path = _cache_path(artifact_cache, _PARAMETERS)
    path.mkdir(parents=True)
    payload = path / "payload.txt"
    payload.write_text("package content", encoding="utf-8")
    sleeps = 0

    def publish_after_last_sleep(_delay):
        nonlocal sleeps
        sleeps += 1
        if sleeps == artifact_cache._CACHE_PUBLISH_RETRIES:
            artifact_cache._get_checksum_path(path).write_text(
                artifact_cache.hash_files_content([payload]), encoding="utf-8"
            )

    mocker.patch(f"{_MODULE}.time.sleep", side_effect=publish_after_last_sleep)

    assert artifact_cache.get(**_PARAMETERS) == path.resolve()
    assert sleeps == artifact_cache._CACHE_PUBLISH_RETRIES
    assert artifact_cache._check_artifacts(path)
    download.assert_not_called()


def test_get_waits_for_transient_checksum_sharing_violation(artifact_cache, download, mocker):
    path = artifact_cache.set(**_PARAMETERS)
    check = mocker.patch.object(
        artifact_cache,
        "_check_artifacts",
        side_effect=[False, PermissionError(errno.EACCES, "checksum being published"), True],
    )
    sleep = mocker.patch(f"{_MODULE}.time.sleep")

    assert artifact_cache.get(**_PARAMETERS) == path
    assert check.call_count == 3
    sleep.assert_called_once_with(artifact_cache._CACHE_PUBLISH_RETRY_DELAY)
    assert download.call_count == 1


def test_get_does_not_hide_persistent_checksum_permission_errors(artifact_cache, download, mocker):
    path = artifact_cache.set(**_PARAMETERS)
    check = mocker.patch.object(
        artifact_cache,
        "_check_artifacts",
        side_effect=[False]
        + [PermissionError(errno.EACCES, "checksum read denied")] * artifact_cache._CACHE_PUBLISH_RETRIES,
    )
    sleep = mocker.patch(f"{_MODULE}.time.sleep")

    with pytest.raises(PermissionError, match="checksum read denied"):
        artifact_cache.get(**_PARAMETERS)

    assert check.call_count == artifact_cache._CACHE_PUBLISH_RETRIES + 1
    assert sleep.call_count == artifact_cache._CACHE_PUBLISH_RETRIES - 1
    assert (path / "payload.txt").read_text(encoding="utf-8") == "package content"
    assert download.call_count == 1


def test_get_revalidates_destination_while_waiting(artifact_cache, download, tmp_path, mocker):
    path = _cache_path(artifact_cache, _PARAMETERS)
    path.mkdir(parents=True)
    organization_path = artifact_cache.cache_directory / artifact_cache._format_organization_name(
        _PARAMETERS["organization"]
    )
    outside = tmp_path / "outside"
    outside.mkdir()
    canary = outside / "canary.txt"
    canary.write_text("unchanged", encoding="utf-8")

    def replace_parent(_delay):
        organization_path.rename(tmp_path / "original")
        _directory_link(organization_path, outside)

    mocker.patch(f"{_MODULE}.time.sleep", side_effect=replace_parent)

    with pytest.raises(ValueError, match="cache"):
        artifact_cache.get(**_PARAMETERS)

    assert list(outside.iterdir()) == [canary]
    assert canary.read_text(encoding="utf-8") == "unchanged"
    download.assert_not_called()


def test_incomplete_cache_publication_has_bounded_retries(artifact_cache, download, mocker):
    path = _cache_path(artifact_cache, _PARAMETERS)
    path.mkdir(parents=True)
    canary = path / "existing.txt"
    canary.write_text("unchanged", encoding="utf-8")
    sleep = mocker.patch(f"{_MODULE}.time.sleep")
    check = mocker.spy(artifact_cache, "_check_artifacts")

    with pytest.raises(OSError) as error:
        artifact_cache.set(**_PARAMETERS)

    assert error.value.errno in (errno.EEXIST, errno.ENOTEMPTY)
    assert check.call_count == artifact_cache._CACHE_PUBLISH_RETRIES
    assert sleep.call_count == artifact_cache._CACHE_PUBLISH_RETRIES
    assert all(call.args == (artifact_cache._CACHE_PUBLISH_RETRY_DELAY,) for call in sleep.call_args_list)
    assert canary.read_text(encoding="utf-8") == "unchanged"
    assert not list(artifact_cache.cache_directory.glob("tmp*"))


def test_cache_waits_for_transient_checksum_sharing_violation(artifact_cache, download, mocker):
    path = artifact_cache.set(**_PARAMETERS)
    check = mocker.patch.object(
        artifact_cache,
        "_check_artifacts",
        side_effect=[PermissionError(errno.EACCES, "checksum being published"), True],
    )
    sleep = mocker.patch(f"{_MODULE}.time.sleep")

    assert artifact_cache.set(**_PARAMETERS) == path
    assert check.call_count == 2
    sleep.assert_called_once_with(artifact_cache._CACHE_PUBLISH_RETRY_DELAY)


def test_cache_does_not_hide_persistent_checksum_permission_errors(artifact_cache, download, mocker):
    artifact_cache.set(**_PARAMETERS)
    check = mocker.patch.object(
        artifact_cache, "_check_artifacts", side_effect=PermissionError(errno.EACCES, "checksum read denied")
    )
    sleep = mocker.patch(f"{_MODULE}.time.sleep")

    with pytest.raises(PermissionError, match="checksum read denied"):
        artifact_cache.set(**_PARAMETERS)

    assert check.call_count == artifact_cache._CACHE_PUBLISH_RETRIES
    assert sleep.call_count == artifact_cache._CACHE_PUBLISH_RETRIES - 1


@pytest.mark.parametrize("error_code", [errno.EACCES, errno.EIO])
def test_valid_cache_does_not_hide_unrelated_storage_errors(artifact_cache, download, mocker, error_code):
    path = artifact_cache.set(**_PARAMETERS)
    mocker.patch(f"{_MODULE}.os.rename", side_effect=OSError(error_code, "test storage failure"))
    sleep = mocker.patch(f"{_MODULE}.time.sleep")

    with pytest.raises(OSError, match="test storage failure"):
        artifact_cache.set(**_PARAMETERS)

    sleep.assert_not_called()
    assert artifact_cache._check_artifacts(path)


def test_cache_uses_configured_root(artifact_cache, tmp_path, download):
    artifact_cache.__init__(cache_directory=tmp_path / "configured")
    path = artifact_cache.get(**_PARAMETERS)
    assert path == _cache_path(artifact_cache, _PARAMETERS).resolve()
    assert artifact_cache._check_artifacts(path)
    assert not list(artifact_cache.DEFAULT_DISK_CACHE_DIRECTORY.iterdir())


def test_cache_revalidates_destination_after_download(artifact_cache, download, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    write_package = download.side_effect

    def replace_parent(command, **kwargs):
        result = write_package(command, **kwargs)
        organization_path = artifact_cache.cache_directory / artifact_cache._format_organization_name(
            _PARAMETERS["organization"]
        )
        _directory_link(organization_path, outside)
        return result

    download.side_effect = replace_parent
    with pytest.raises(ValueError, match="cache"):
        artifact_cache.set(**_PARAMETERS)
    assert not list(outside.iterdir())


def test_additional_includes_uses_cache_validation(artifact_cache, tmp_path, mocker):
    run = mocker.patch(f"{_MODULE}.subprocess.run", side_effect=AssertionError("Unexpected process"))
    config = dict(_PARAMETERS, type="artifact", project=str(tmp_path / "outside"))
    with pytest.raises(ValueError, match="Artifact"):
        AdditionalIncludes._get_artifacts_by_config(config)
    run.assert_not_called()
