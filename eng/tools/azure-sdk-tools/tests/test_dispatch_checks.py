import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
TOOLS_ROOT = os.path.join(REPO_ROOT, "eng", "tools", "azure-sdk-tools")
if TOOLS_ROOT not in sys.path:
    sys.path.insert(0, TOOLS_ROOT)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from eng.scripts import dispatch_checks
from eng.scripts.dispatch_checks import get_check_dest_dir


def test_apistub_dest_dir_uses_package_subdirectory():
    package_dir = os.path.join(REPO_ROOT, "sdk", "core", "azure-core")
    artifact_dir = os.path.join(REPO_ROOT, "artifacts")

    with patch(
        "eng.scripts.dispatch_checks.ParsedSetup.from_path",
        return_value=SimpleNamespace(name="azure-core"),
    ):
        result = get_check_dest_dir(package_dir, "apistub", artifact_dir)

    assert result == os.path.join(artifact_dir, "azure-core")


def test_non_apistub_dest_dir_is_unchanged():
    package_dir = os.path.join(REPO_ROOT, "sdk", "core", "azure-core")
    artifact_dir = os.path.join(REPO_ROOT, "artifacts")

    with patch("eng.scripts.dispatch_checks.ParsedSetup.from_path") as parsed_setup:
        result = get_check_dest_dir(package_dir, "pylint", artifact_dir)

    assert result == artifact_dir
    parsed_setup.assert_not_called()


def test_empty_dest_dir_is_unchanged():
    package_dir = os.path.join(REPO_ROOT, "sdk", "core", "azure-core")

    with patch("eng.scripts.dispatch_checks.ParsedSetup.from_path") as parsed_setup:
        result = get_check_dest_dir(package_dir, "apistub", None)

    assert result is None
    parsed_setup.assert_not_called()


def test_finalize_isolate_dirs_preserves_coverage_sources(tmp_path):
    isolate_dir = tmp_path / ".venv_whl"
    isolate_dir.mkdir()
    dispatch_checks.ISOLATE_DIRS_TO_CLEAN.append(os.fspath(isolate_dir))

    with patch("eng.scripts.dispatch_checks.in_ci", return_value=1):
        dispatch_checks._finalize_isolate_dirs(["whl"], coverage_enabled=True)

    assert isolate_dir.exists()
    assert not dispatch_checks.ISOLATE_DIRS_TO_CLEAN


def test_finalize_isolate_dirs_removes_sources_for_non_coverage_checks(tmp_path):
    isolate_dir = tmp_path / ".venv_pylint"
    isolate_dir.mkdir()
    dispatch_checks.ISOLATE_DIRS_TO_CLEAN.append(os.fspath(isolate_dir))

    with patch("eng.scripts.dispatch_checks.in_ci", return_value=1):
        dispatch_checks._finalize_isolate_dirs(["pylint", "samples"], coverage_enabled=True)

    assert not isolate_dir.exists()
    assert not dispatch_checks.ISOLATE_DIRS_TO_CLEAN


def test_finalize_isolate_dirs_removes_github_actions_venvs(tmp_path):
    isolate_dir = tmp_path / ".venv_whl"
    isolate_dir.mkdir()
    dispatch_checks.ISOLATE_DIRS_TO_CLEAN.append(os.fspath(isolate_dir))

    with patch("eng.scripts.dispatch_checks.in_ci", return_value=2):
        dispatch_checks._finalize_isolate_dirs(["whl"], coverage_enabled=True)

    assert not isolate_dir.exists()
    assert not dispatch_checks.ISOLATE_DIRS_TO_CLEAN


def test_finalize_isolate_dirs_removes_non_coverage_sources(tmp_path):
    isolate_dir = tmp_path / ".venv_whl"
    isolate_dir.mkdir()
    dispatch_checks.ISOLATE_DIRS_TO_CLEAN.append(os.fspath(isolate_dir))

    dispatch_checks._finalize_isolate_dirs(["whl"], coverage_enabled=False)

    assert not isolate_dir.exists()
    assert not dispatch_checks.ISOLATE_DIRS_TO_CLEAN
