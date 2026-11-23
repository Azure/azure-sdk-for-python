import asyncio
import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
TOOLS_ROOT = os.path.join(REPO_ROOT, "eng", "tools", "azure-sdk-tools")
if TOOLS_ROOT not in sys.path:
    sys.path.insert(0, TOOLS_ROOT)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from eng.scripts import dispatch_checks
from eng.scripts.dispatch_checks import CheckResult, get_check_dest_dir, run_all_checks


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


@pytest.mark.parametrize("apistub_enabled", [False, True, None])
def test_dispatch_requires_apistub(tmp_path, monkeypatch, apistub_enabled):
    package_dir = str(tmp_path)
    config = "[tool.azure-sdk-build]\npylint = false\n"
    if apistub_enabled is not None:
        config += f"apistub = {str(apistub_enabled).lower()}\n"
    (tmp_path / "pyproject.toml").write_text(config)
    for check in ("APISTUB", "PYLINT", "CI_ENABLED"):
        monkeypatch.delenv(f"{tmp_path.name.upper().replace('-', '_')}_{check}", raising=False)
    result = CheckResult(package_dir, "apistub", 0, 0.0, "", "")

    with patch("eng.scripts.dispatch_checks.in_ci", return_value=False), patch(
        "eng.scripts.dispatch_checks.run_check", new_callable=AsyncMock, return_value=result
    ) as run_check:
        invocation = run_all_checks([package_dir], ["pylint", "apistub"], 1, str(tmp_path), None, "")
        if apistub_enabled is False:
            with pytest.raises(ValueError, match="apistub is required"):
                asyncio.run(invocation)
            run_check.assert_not_called()
        else:
            assert asyncio.run(invocation) == 0
            run_check.assert_awaited_once()
            assert run_check.call_args.args[2] == "apistub"
            assert "--disablecov" not in run_check.call_args.args[3]


@pytest.mark.parametrize("disablecov", [False, True])
def test_dispatch_forwards_coverage_option_without_shifting_positional_args(tmp_path, disablecov):
    package_dir = str(tmp_path)
    destination = str(tmp_path / "reports")
    (tmp_path / "pyproject.toml").write_text("[tool.azure-sdk-build]\n")
    result = CheckResult(package_dir, "devtest", 0, 0.0, "", "")

    with patch("eng.scripts.dispatch_checks.in_ci", return_value=False), patch(
        "eng.scripts.dispatch_checks.run_check", new_callable=AsyncMock, return_value=result
    ) as run_check:
        assert (
            asyncio.run(
                run_all_checks(
                    [package_dir], ["devtest"], 1, str(tmp_path), None, "", destination, "core", disablecov=disablecov
                )
            )
            == 0
        )

    run_check.assert_awaited_once()
    assert run_check.call_args.args[3] == [sys.executable, "-m", "azpysdk.main"] + (
        ["--disablecov"] if disablecov else []
    )
    assert run_check.call_args.args[8:10] == (destination, "core")


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


def test_finalize_isolate_dirs_removes_optional_isolates_without_coverage(tmp_path):
    isolate_dir = tmp_path / ".venv_optional"
    isolate_dir.mkdir()
    dispatch_checks.ISOLATE_DIRS_TO_CLEAN.append(os.fspath(isolate_dir))

    with patch("eng.scripts.dispatch_checks.in_ci", return_value=1):
        dispatch_checks._finalize_isolate_dirs(["optional"], coverage_enabled=True)

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
