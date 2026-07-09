#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import sys
import time
import zipfile
from unittest import mock

import pytest

CHECKER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SCRIPTS_DIR = os.path.dirname(CHECKER_DIR)
REPO_ROOT = os.path.dirname(SCRIPTS_DIR)
MAX_APIMANAGEMENT_APISTUB_CODE_REPORT_SECONDS = 120

for _path in (SCRIPTS_DIR, CHECKER_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)


def _code_report_args(use_apistub: bool = False):
    return ["--code-report"] + (["--use-apistub"] if use_apistub else [])


def _download_and_extract_sdist(executable: str, package_name: str, version: str, dest_dir: str) -> str:
    """Download the sdist for ``package_name==version`` and extract it.

    Returns the path to the extracted source tree (the directory that contains
    ``setup.py``/``pyproject.toml``). ``--use-apistub`` builds the code report
    from local source, so a real source tree is required.
    """
    download_dir = tempfile.mkdtemp(dir=dest_dir)
    subprocess.check_call(
        [
            executable,
            "-m",
            "pip",
            "download",
            f"{package_name}=={version}",
            "--no-deps",
            "--no-binary=:all:",
            "-d",
            download_dir,
        ],
    )
    sdists = [f for f in os.listdir(download_dir) if f.endswith((".tar.gz", ".zip"))]
    if not sdists:
        raise FileNotFoundError(f"No sdist found for {package_name}=={version}")
    sdist_path = os.path.join(download_dir, sdists[0])
    extract_dir = tempfile.mkdtemp(dir=dest_dir)
    if sdist_path.endswith(".zip"):
        with zipfile.ZipFile(sdist_path) as archive:
            archive.extractall(extract_dir)
    else:
        with tarfile.open(sdist_path) as archive:
            archive.extractall(extract_dir)
    entries = [os.path.join(extract_dir, e) for e in os.listdir(extract_dir)]
    source_dirs = [e for e in entries if os.path.isdir(e)]
    return source_dirs[0] if len(source_dirs) == 1 else extract_dir


def _prepare_fake_repo(tmpdir: str, package_name: str, source_dir: str) -> str:
    """Arrange ``source_dir`` inside a minimal fake repo rooted at ``tmpdir``.

    ``azpysdk apistub`` resolves the repo root by walking up from its working
    directory looking for a ``.git`` marker and reads helper scripts from
    ``<repo>/eng`` and ``<repo>/scripts``. Recreating just those inside the temp
    dir lets apistub run against the extracted source while keeping all of its
    scratch output (``.venv``, ``.staging``, ``.artifacts`` ...) under ``tmpdir``
    instead of the real repo. apistub is invoked with ``target='.'`` (cwd is the
    package), so the source can live directly under ``tmpdir`` -- no
    ``sdk/<service>/`` nesting is required. Returns the package directory
    (``<tmpdir>/<package_name>``).
    """
    os.makedirs(os.path.join(tmpdir, ".git"), exist_ok=True)

    # Symlink the real ``eng`` and ``scripts`` directories so apistub can find
    # its helper scripts (e.g. Export-APIViewMarkdown.ps1 under ``eng`` and
    # common_tasks under ``scripts/devops_tasks``) under the fake repo root.
    for name in ("eng", "scripts"):
        link = os.path.join(tmpdir, name)
        if not os.path.exists(link):
            os.symlink(os.path.join(REPO_ROOT, name), link)

    pkg_dir = os.path.join(tmpdir, package_name)
    shutil.move(source_dir, pkg_dir)
    return pkg_dir


def _assert_code_report_matches_expected(actual_report_path: str, expected_report_file: str):
    with open(actual_report_path, encoding="utf-8") as f:
        actual_report = json.load(f)
    assert isinstance(actual_report, dict) and len(actual_report) > 0, "Code report should not be empty"

    expected_path = os.path.join(DATA_DIR, expected_report_file)
    if os.environ.get("UPDATE_EXPECTED"):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(expected_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(actual_report, f, indent=2)
            f.write("\n")
        return

    if not os.path.isfile(expected_path):
        raise AssertionError(
            f"Expected code report file not found: {expected_path}. "
            "Set UPDATE_EXPECTED=1 to generate or update expected outputs."
        )
    with open(expected_path, encoding="utf-8") as f:
        expected_report = json.load(f)

    if actual_report != expected_report:
        dump_path = os.path.join(tempfile.gettempdir(), expected_report_file)
        with open(dump_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(actual_report, f, indent=2)
            f.write("\n")
        raise AssertionError(
            f"Code report mismatch. Actual code report written to: {dump_path}\n"
            f"To update expected data, copy it to: {expected_path}\n"
        )


def _generate_and_compare_code_report(
    package_name: str,
    target_module: str,
    package_version: str,
    expected_report_file: str,
    use_apistub: bool = False,
    max_code_report_seconds: int | None = None,
):
    """Install one package version, generate a code report, and compare it to expected data.

    When ``use_apistub`` is set, the code reports are produced from the
    apistub-generated ``api.md`` (via the ``--use-apistub`` flag) instead of by
    importing the installed package.
    """
    from packaging_tools.venvtools import create_venv_with_package

    packages = [f"{package_name}=={package_version}"]
    with create_venv_with_package(packages) as venv, tempfile.TemporaryDirectory() as tmpdir:
        subprocess.check_call(
            [venv.env_exe, "-m", "pip", "install", "-r", os.path.join(CHECKER_DIR, "dev_requirements.txt")],
            cwd=CHECKER_DIR,
        )
        if use_apistub:
            subprocess.check_call(
                [
                    venv.env_exe,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    os.path.join(CHECKER_DIR, "..", "..", "eng", "apiview_reqs.txt"),
                    "--index-url=https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/",
                ],
            )

        # The apistub-based code report is built from a local package source tree,
        # so extract the sdist for this version and lay it out inside a fake repo
        # under the temp dir. The import-based report only needs the installed
        # package, so the package name works as the target directly.
        if use_apistub:
            source_dir = _download_and_extract_sdist(venv.env_exe, package_name, package_version, tmpdir)
            target_package = _prepare_fake_repo(tmpdir, package_name, source_dir)
        else:
            target_package = package_name

        start = time.perf_counter()
        result = subprocess.run(
            [
                venv.env_exe,
                os.path.join(CHECKER_DIR, "detect_breaking_changes.py"),
                "-t",
                target_package,
                "-m",
                target_module,
                *_code_report_args(use_apistub),
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        elapsed = time.perf_counter() - start
        assert result.returncode == 0, f"Code report generation for {package_version} failed:\n{result.stderr}"
        if max_code_report_seconds is not None:
            assert elapsed < max_code_report_seconds, (
                f"Code report generation for {package_version} took {elapsed:.2f}s, "
                f"expected less than {max_code_report_seconds}s"
            )
        _assert_code_report_matches_expected(os.path.join(tmpdir, "code_report.json"), expected_report_file)


def _compare_code_reports_to_changelog(
    package_name: str,
    source_report_file: str,
    target_report_file: str,
    expected_changelog_file: str,
    order_insensitive: bool = False,
):
    """Compare checked-in code reports and validate the generated changelog."""
    source_report_path = os.path.join(DATA_DIR, source_report_file)
    target_report_path = os.path.join(DATA_DIR, target_report_file)
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [
                sys.executable,
                os.path.join(CHECKER_DIR, "detect_breaking_changes.py"),
                "-t",
                package_name,
                "--changelog",
                "--source-report",
                source_report_path,
                "--target-report",
                target_report_path,
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        assert result.returncode == 0, f"Changelog comparison failed:\n{result.stderr}"

        changelog_output = result.stdout
        assert (
            "===== changelog start =====" in changelog_output
        ), f"Changelog output missing start marker:\n{changelog_output}"
        assert (
            "===== changelog end =====" in changelog_output
        ), f"Changelog output missing end marker:\n{changelog_output}"

        # Extract changelog content between markers and compare with expected
        start = changelog_output.index("===== changelog start =====") + len("===== changelog start =====\n")
        end = changelog_output.index("\n===== changelog end =====")
        actual_changelog = changelog_output[start:end].strip()

        expected_path = os.path.join(DATA_DIR, expected_changelog_file)

        # If UPDATE_EXPECTED is set, (re)generate the expected changelog file.
        if os.environ.get("UPDATE_EXPECTED") and not order_insensitive:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(expected_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(actual_changelog + "\n")

        # Without UPDATE_EXPECTED, the expected file must already exist; otherwise, fail explicitly.
        if not os.path.isfile(expected_path):
            raise AssertionError(
                f"Expected changelog file not found: {expected_path}. "
                "Set UPDATE_EXPECTED=1 to generate or update expected outputs."
            )
        with open(expected_path, encoding="utf-8") as f:
            expected_changelog = f.read().strip()

        if order_insensitive:
            matches = sorted(l.strip() for l in actual_changelog.splitlines() if l.strip()) == sorted(
                l.strip() for l in expected_changelog.splitlines() if l.strip()
            )
        else:
            matches = actual_changelog == expected_changelog

        if not matches:
            # Dump the actual changelog to a temp folder so the expected data can be
            # updated by copying this file, without rerunning these expensive tests.
            dump_path = os.path.join(tempfile.gettempdir(), expected_changelog_file)
            with open(dump_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(actual_changelog + "\n")
            raise AssertionError(
                f"Changelog mismatch. Actual changelog written to: {dump_path}\n"
                f"To update expected data, copy it to: {expected_path}\n"
            )


def test_generate_old_code_report_for_azure_mgmt_peering():
    """Generate azure-mgmt-peering 2.0.0b1 code report."""
    _generate_and_compare_code_report(
        package_name="azure-mgmt-peering",
        target_module="azure.mgmt.peering",
        package_version="2.0.0b1",
        expected_report_file="expected_peering_b1_code_report.json",
    )


def test_generate_new_code_report_for_azure_mgmt_peering():
    """Generate azure-mgmt-peering 2.0.0b2 code report."""
    _generate_and_compare_code_report(
        package_name="azure-mgmt-peering",
        target_module="azure.mgmt.peering",
        package_version="2.0.0b2",
        expected_report_file="expected_peering_b2_code_report.json",
    )


def test_compare_code_reports_for_azure_mgmt_peering():
    """Compare azure-mgmt-peering 2.0.0b1 vs 2.0.0b2 changelog."""
    _compare_code_reports_to_changelog(
        package_name="azure-mgmt-peering",
        source_report_file="expected_peering_b1_code_report.json",
        target_report_file="expected_peering_b2_code_report.json",
        expected_changelog_file="expected_peering_b1_b2_changelog.txt",
    )


@pytest.mark.slow(reason="azure-mgmt-apimanagement code report generation may take up to 10 minutes")
def test_generate_old_code_report_for_azure_mgmt_apimanagement():
    """Generate azure-mgmt-apimanagement 5.0.0 code report. May take up to 10 minutes."""
    _generate_and_compare_code_report(
        package_name="azure-mgmt-apimanagement",
        target_module="azure.mgmt.apimanagement",
        package_version="5.0.0",
        expected_report_file="expected_apimanagement_5_code_report.json",
    )


@pytest.mark.slow(reason="azure-mgmt-apimanagement code report generation may take up to 10 minutes")
def test_generate_new_code_report_for_azure_mgmt_apimanagement():
    """Generate azure-mgmt-apimanagement 6.0.0b1 code report. May take up to 10 minutes."""
    _generate_and_compare_code_report(
        package_name="azure-mgmt-apimanagement",
        target_module="azure.mgmt.apimanagement",
        package_version="6.0.0b1",
        expected_report_file="expected_apimanagement_6b1_code_report.json",
    )


def test_compare_code_reports_for_azure_mgmt_apimanagement():
    """Compare azure-mgmt-apimanagement 5.0.0 vs 6.0.0b1 changelog."""
    _compare_code_reports_to_changelog(
        package_name="azure-mgmt-apimanagement",
        source_report_file="expected_apimanagement_5_code_report.json",
        target_report_file="expected_apimanagement_6b1_code_report.json",
        expected_changelog_file="expected_apimanagement_5_6b1_changelog.txt",
    )


def test_generate_old_code_report_for_azure_mgmt_peering_apistub():
    """Generate azure-mgmt-peering 2.0.0b1 code report using --use-apistub."""
    _generate_and_compare_code_report(
        package_name="azure-mgmt-peering",
        target_module="azure.mgmt.peering",
        package_version="2.0.0b1",
        expected_report_file="expected_peering_b1_code_report_from_apistub.json",
        use_apistub=True,
    )


def test_generate_new_code_report_for_azure_mgmt_peering_apistub():
    """Generate azure-mgmt-peering 2.0.0b2 code report using --use-apistub."""
    _generate_and_compare_code_report(
        package_name="azure-mgmt-peering",
        target_module="azure.mgmt.peering",
        package_version="2.0.0b2",
        expected_report_file="expected_peering_b2_code_report_from_apistub.json",
        use_apistub=True,
    )


def test_compare_code_reports_for_azure_mgmt_peering_apistub():
    """Compare azure-mgmt-peering 2.0.0b1 vs 2.0.0b2 changelog using --use-apistub."""
    _compare_code_reports_to_changelog(
        package_name="azure-mgmt-peering",
        source_report_file="expected_peering_b1_code_report_from_apistub.json",
        target_report_file="expected_peering_b2_code_report_from_apistub.json",
        expected_changelog_file="expected_peering_b1_b2_changelog.txt",
        order_insensitive=True,
    )


def test_generate_old_code_report_for_azure_mgmt_apimanagement_apistub():
    """Generate azure-mgmt-apimanagement 5.0.0 code report using --use-apistub."""
    _generate_and_compare_code_report(
        package_name="azure-mgmt-apimanagement",
        target_module="azure.mgmt.apimanagement",
        package_version="5.0.0",
        expected_report_file="expected_apimanagement_5_code_report_from_apistub.json",
        use_apistub=True,
        max_code_report_seconds=MAX_APIMANAGEMENT_APISTUB_CODE_REPORT_SECONDS,
    )


def test_generate_new_code_report_for_azure_mgmt_apimanagement_apistub():
    """Generate azure-mgmt-apimanagement 6.0.0b1 code report using --use-apistub."""
    _generate_and_compare_code_report(
        package_name="azure-mgmt-apimanagement",
        target_module="azure.mgmt.apimanagement",
        package_version="6.0.0b1",
        expected_report_file="expected_apimanagement_6b1_code_report_from_apistub.json",
        use_apistub=True,
        max_code_report_seconds=MAX_APIMANAGEMENT_APISTUB_CODE_REPORT_SECONDS,
    )


def test_compare_code_reports_for_azure_mgmt_apimanagement_apistub():
    """Compare azure-mgmt-apimanagement 5.0.0 vs 6.0.0b1 changelog using --use-apistub."""
    _compare_code_reports_to_changelog(
        package_name="azure-mgmt-apimanagement",
        source_report_file="expected_apimanagement_5_code_report_from_apistub.json",
        target_report_file="expected_apimanagement_6b1_code_report_from_apistub.json",
        expected_changelog_file="expected_apimanagement_5_6b1_changelog.txt",
        order_insensitive=True,
    )


def test_use_apistub_changelog_resolves_stable_from_pypi_and_current_from_local():
    """``--use-apistub`` without ``-s`` must diff local source against the previous PyPI release.

    Regression test for the empty-changelog bug where both ``current`` and
    ``stable`` were generated from the same (installed) version:
      * ``current`` must be generated from the local source (``from_pypi=False``).
      * ``stable`` must be generated from the previous released PyPI version
        (resolved via ``PyPIClient.get_relevant_versions``), not the installed one.
    """
    from breaking_changes_checker import detect_breaking_changes

    pypi_client = mock.MagicMock()
    # get_relevant_versions(...)[1] is the previous relevant/stable version.
    pypi_client.get_relevant_versions.return_value = ["31.0.0b1", "30.2.0"]

    checker = mock.MagicMock()
    checker.report_changes.return_value = ""
    checker.breaking_changes = []

    with mock.patch("pypi_tools.pypi.PyPIClient", return_value=pypi_client), mock.patch.object(
        detect_breaking_changes, "build_report_from_apistub", return_value={}
    ) as build_report, mock.patch.object(
        detect_breaking_changes, "compare_report_dicts", return_value=checker
    ) as compare:
        detect_breaking_changes.main(
            package_name="azure-mgmt-network",
            target_module="azure.mgmt.network",
            version=None,
            in_venv=False,
            pkg_dir="/tmp/azure-mgmt-network",
            changelog=True,
            code_report=False,
            latest_pypi_version=False,
            source_report=None,
            target_report=None,
            use_apistub=True,
        )

    assert build_report.call_count == 2, "Expected separate apistub reports for current and stable"

    calls_by_label = {call.kwargs["label"]: call for call in build_report.call_args_list}
    assert set(calls_by_label) == {"current", "stable"}

    # "current" comes from the local source.
    current_call = calls_by_label["current"]
    assert current_call.kwargs["from_pypi"] is False
    assert current_call.kwargs.get("version") is None

    # "stable" comes from the previous PyPI release, not the installed version.
    stable_call = calls_by_label["stable"]
    assert stable_call.kwargs["from_pypi"] is True
    assert stable_call.kwargs["version"] == "30.2.0"

    # The diff compares (stable, current) so the two reports must differ in version source.
    pypi_client.get_relevant_versions.assert_called_once_with("azure-mgmt-network")
    compare.assert_called_once()
    stable_arg, current_arg = compare.call_args.args[0], compare.call_args.args[1]
    assert stable_arg is not None and current_arg is not None
