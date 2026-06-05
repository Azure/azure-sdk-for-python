#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import subprocess
import tempfile

CHECKER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _generate_and_compare_changelog(
    package_name: str,
    target_module: str,
    source_version: str,
    target_version: str,
    expected_changelog_file: str,
):
    """Install two versions of a package in the same venv, generate code reports, and compare the changelog."""
    from packaging_tools.venvtools import create_venv_with_package

    packages = [f"{package_name}=={source_version}"]
    with create_venv_with_package(packages) as venv, tempfile.TemporaryDirectory() as tmpdir:
        subprocess.check_call(
            [venv.env_exe, "-m", "pip", "install", "-r", os.path.join(CHECKER_DIR, "dev_requirements.txt")],
            cwd=CHECKER_DIR,
        )

        # Generate code report for source version
        result = subprocess.run(
            [
                venv.env_exe,
                os.path.join(CHECKER_DIR, "detect_breaking_changes.py"),
                "-t", package_name,
                "-m", target_module,
                "--code-report",
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        assert result.returncode == 0, f"Code report generation for {source_version} failed:\n{result.stderr}"

        source_report_path = os.path.join(tmpdir, "source_report.json")
        os.rename(os.path.join(tmpdir, "code_report.json"), source_report_path)

        with open(source_report_path) as f:
            source_report = json.load(f)
        assert isinstance(source_report, dict) and len(source_report) > 0, \
            f"Code report for {source_version} should not be empty"

        # Upgrade to target version in the same venv
        subprocess.check_call(
            [venv.env_exe, "-m", "pip", "install", f"{package_name}=={target_version}"],
        )

        # Generate code report for target version
        result = subprocess.run(
            [
                venv.env_exe,
                os.path.join(CHECKER_DIR, "detect_breaking_changes.py"),
                "-t", package_name,
                "-m", target_module,
                "--code-report",
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        assert result.returncode == 0, f"Code report generation for {target_version} failed:\n{result.stderr}"

        target_report_path = os.path.join(tmpdir, "target_report.json")
        os.rename(os.path.join(tmpdir, "code_report.json"), target_report_path)

        with open(target_report_path) as f:
            target_report = json.load(f)
        assert isinstance(target_report, dict) and len(target_report) > 0, \
            f"Code report for {target_version} should not be empty"

        # Compare the two reports to generate changelog
        result = subprocess.run(
            [
                venv.env_exe,
                os.path.join(CHECKER_DIR, "detect_breaking_changes.py"),
                "-t", package_name,
                "--changelog",
                "--source-report", source_report_path,
                "--target-report", target_report_path,
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        assert result.returncode == 0, f"Changelog comparison failed:\n{result.stderr}"

        changelog_output = result.stdout
        assert "===== changelog start =====" in changelog_output, \
            f"Changelog output missing start marker:\n{changelog_output}"
        assert "===== changelog end =====" in changelog_output, \
            f"Changelog output missing end marker:\n{changelog_output}"

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

        assert actual_changelog == expected_changelog, (
            f"Changelog mismatch.\n--- Expected ---\n{expected_changelog}\n--- Actual ---\n{actual_changelog}"
        )


def test_code_report_for_azure_mgmt_peering():
    """Compare azure-mgmt-peering 2.0.0b1 vs 2.0.0b2 changelog."""
    _generate_and_compare_changelog(
        package_name="azure-mgmt-peering",
        target_module="azure.mgmt.peering",
        source_version="2.0.0b1",
        target_version="2.0.0b2",
        expected_changelog_file="expected_peering_b1_b2_changelog.txt",
    )


def test_code_report_for_azure_mgmt_apimanagement():
    """Compare azure-mgmt-apimanagement 5.0.0 vs 6.0.0b1 changelog."""
    _generate_and_compare_changelog(
        package_name="azure-mgmt-apimanagement",
        target_module="azure.mgmt.apimanagement",
        source_version="5.0.0",
        target_version="6.0.0b1",
        expected_changelog_file="expected_apimanagement_5_6b1_changelog.txt",
    )
