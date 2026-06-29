#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import subprocess
import tempfile
import sys

import pytest

CHECKER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _code_report_args(use_apistub: bool = False):
    return ["--code-report"] + (["--use-apistub"] if use_apistub else [])


def _assert_code_report_matches_expected(actual_report_path: str, expected_report_file: str):
    with open(actual_report_path, encoding="utf-8") as f:
        actual_report = json.load(f)
    assert isinstance(actual_report, dict) and len(actual_report) > 0, "Code report should not be empty"

    expected_path = os.path.join(DATA_DIR, expected_report_file)
    if os.environ.get("UPDATE_EXPECTED"):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(expected_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(actual_report, f, indent=2, sort_keys=True)
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
            json.dump(actual_report, f, indent=2, sort_keys=True)
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
                    venv.env_exe, "-m", "pip", "install",
                    "-r", os.path.join(CHECKER_DIR, "..", "..", "eng", "apiview_reqs.txt"),
                    "--index-url=https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/",
                ],
            )

        result = subprocess.run(
            [
                venv.env_exe,
                os.path.join(CHECKER_DIR, "detect_breaking_changes.py"),
                "-t",
                package_name,
                "-m",
                target_module,
                *_code_report_args(use_apistub),
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        assert result.returncode == 0, f"Code report generation for {package_version} failed:\n{result.stderr}"
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
        if os.environ.get("UPDATE_EXPECTED"):
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(expected_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(actual_changelog + "\n")
            return

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
    )


def test_generate_new_code_report_for_azure_mgmt_apimanagement_apistub():
    """Generate azure-mgmt-apimanagement 6.0.0b1 code report using --use-apistub."""
    _generate_and_compare_code_report(
        package_name="azure-mgmt-apimanagement",
        target_module="azure.mgmt.apimanagement",
        package_version="6.0.0b1",
        expected_report_file="expected_apimanagement_6b1_code_report_from_apistub.json",
        use_apistub=True,
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
