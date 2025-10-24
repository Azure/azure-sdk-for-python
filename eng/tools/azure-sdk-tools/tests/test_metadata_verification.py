#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import subprocess
import pytest
import shutil
import glob
import sys

from ci_tools.parsing import ParsedSetup

# Import the functions we want to test from the verify modules
tox_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "tox"))
if tox_path not in sys.path:
    sys.path.append(tox_path)

# Also add the azure-sdk-tools path so pypi_tools can be imported
tools_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if tools_path not in sys.path:
    sys.path.append(tools_path)

from verify_whl import verify_whl_root_directory
from verify_sdist import verify_sdist

# Test scenario paths
scenarios_folder = os.path.join(os.path.dirname(__file__), "integration", "scenarios")
pyproject_metadata_scenario = os.path.join(scenarios_folder, "pyproject_metadata")
pyproject_invalid_metadata_scenario = os.path.join(scenarios_folder, "pyproject_invalid_metadata")
pyproject_beta_metadata_scenario = os.path.join(scenarios_folder, "pyproject_beta_metadata")
pyproject_beta_invalid_metadata_scenario = os.path.join(scenarios_folder, "pyproject_beta_invalid_metadata")


def build_package_in_scenario(scenario_path: str, package_type: str = "wheel") -> str:
    """Build a wheel or sdist package in the scenario directory and return the path to it."""
    # Clean up any existing build artifacts first
    for artifact_dir in ["build", "dist", "*.egg-info"]:
        artifact_path = os.path.join(scenario_path, artifact_dir)
        if artifact_dir.endswith("*"):
            # Handle glob patterns for egg-info directories
            for egg_info in glob.glob(os.path.join(scenario_path, artifact_dir)):
                if os.path.exists(egg_info):
                    shutil.rmtree(egg_info)
        elif os.path.exists(artifact_path):
            shutil.rmtree(artifact_path)

    # Build the package directly in the scenario directory
    if package_type == "wheel":
        cmd = [sys.executable, "-m", "build", "--wheel"]
    else:  # sdist
        cmd = [sys.executable, "-m", "build", "--sdist"]

    result = subprocess.run(cmd, cwd=scenario_path, check=True, capture_output=True)

    # Find the built package in the dist directory
    dist_dir = os.path.join(scenario_path, "dist")
    if package_type == "wheel":
        packages = glob.glob(os.path.join(dist_dir, "*.whl"))
    else:
        packages = glob.glob(os.path.join(dist_dir, "*.tar.gz"))

    if not packages:
        raise RuntimeError(f"No {package_type} package found after build in {dist_dir}")

    return packages[0]  # Return the first (and should be only) package


@pytest.mark.parametrize(
    "package_type,scenario_name,scenario_path",
    [
        ("wheel", "stable", "pyproject_metadata_scenario"),
        ("sdist", "stable", "pyproject_metadata_scenario"),
        ("wheel", "beta", "pyproject_beta_metadata_scenario"),
        ("sdist", "beta", "pyproject_beta_metadata_scenario"),
    ],
)
def test_verify_valid_metadata_passes(package_type, scenario_name, scenario_path):
    """Test that verify_whl/verify_sdist returns True for scenarios with complete metadata."""
    # Get the actual scenario path from globals
    actual_scenario_path = globals()[scenario_path]

    # Clean up any existing dist directory
    dist_dir = os.path.join(actual_scenario_path, "dist")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)

    try:
        # Build package in the scenario directory
        package_path = build_package_in_scenario(actual_scenario_path, package_type)

        # Parse the package to get expected information
        parsed_pkg = ParsedSetup.from_path(actual_scenario_path)

        # Run the appropriate verification function
        if package_type == "wheel":
            expected_module = parsed_pkg.namespace.split(".")[0] if parsed_pkg.namespace else "azure"
            result = verify_whl_root_directory(os.path.dirname(package_path), expected_module, parsed_pkg)
        else:
            result = verify_sdist(actual_scenario_path, os.path.dirname(package_path), parsed_pkg)

        # The valid metadata should pass verification (return True)
        assert result is True, f"verify_{package_type} should return True for valid {scenario_name} metadata scenario"

    finally:
        # Cleanup dist directory
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)


@pytest.mark.parametrize(
    "package_type,scenario_name,scenario_path,missing_keys",
    [
        ("wheel", "stable", "pyproject_invalid_metadata_scenario", ["homepage", "repository"]),
        ("sdist", "stable", "pyproject_invalid_metadata_scenario", ["homepage", "repository"]),
        ("wheel", "beta", "pyproject_beta_invalid_metadata_scenario", ["author_email", "summary"]),
        ("sdist", "beta", "pyproject_beta_invalid_metadata_scenario", ["author_email", "summary"]),
    ],
)
def test_verify_invalid_metadata_fails(package_type, scenario_name, scenario_path, missing_keys, caplog):
    """Test that verify_whl/verify_sdist fails for scenarios with invalid metadata and reports missing author_name and homepage."""
    # Get the actual scenario path from globals
    actual_scenario_path = globals()[scenario_path]

    # Clean up any existing dist directory
    dist_dir = os.path.join(actual_scenario_path, "dist")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)

    try:
        # Build package in the scenario directory
        package_path = build_package_in_scenario(actual_scenario_path, package_type)

        # Parse the package to get expected information
        parsed_pkg = ParsedSetup.from_path(actual_scenario_path)

        # Run the appropriate verification function with logging capture
        with caplog.at_level("ERROR"):
            if package_type == "wheel":
                expected_module = parsed_pkg.namespace.split(".")[0] if parsed_pkg.namespace else "azure"
                result = verify_whl_root_directory(os.path.dirname(package_path), expected_module, parsed_pkg)
            else:
                result = verify_sdist(actual_scenario_path, os.path.dirname(package_path), parsed_pkg)

        # The invalid metadata should fail verification (return False)
        assert (
            result is False
        ), f"verify_{package_type} should return False for invalid {scenario_name} metadata scenario with missing keys"

        # Check that the error log contains information about missing keys
        error_logs = [record.message for record in caplog.records if record.levelname == "ERROR"]

        # Raise error if homepage AND repository not found in current version
        if "homepage" in missing_keys:
            assert f"Current metadata must contain at least one of: {missing_keys}" in error_logs
        # Otherwise, check for missing keys from prior version
        else:
            missing_keys_pattern1 = f"Missing keys: {{'{missing_keys[0]}', '{missing_keys[1]}'}}"
            missing_keys_pattern2 = f"Missing keys: {{'{missing_keys[1]}', '{missing_keys[0]}'}}"
            has_missing_keys_error = any(
                missing_keys_pattern1 in msg or missing_keys_pattern2 in msg for msg in error_logs
            )

            assert (
                has_missing_keys_error
            ), f"Expected error log about Missing keys: '{missing_keys[0]}' and '{missing_keys[1]}' for {scenario_name} scenario, but got: {error_logs}"

    finally:
        # Cleanup dist directory
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
