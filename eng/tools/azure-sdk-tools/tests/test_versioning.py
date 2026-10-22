import os
import shutil
import re
from tempfile import mkdtemp

import pytest

from ci_tools.parsing import ParsedSetup
from ci_tools.versioning.version_set_dev import set_dev_version
from ci_tools.versioning.version_shared import get_classification, DEV_STATUS_REGEX

integration_folder = os.path.join(os.path.dirname(__file__), "integration")
setup_folder = os.path.join(integration_folder, "scenarios", "setup_py_project_def")
pyproject_folder = os.path.join(integration_folder, "scenarios", "pyproject_project_def")
pyproject_beta_folder = os.path.join(integration_folder, "scenarios", "pyproject_project_def_beta")


def create_temp_directory_from_template(input_directory: str) -> str:
    """
    Create a temporary directory from a template directory.

    Args:
        input_directory (str): The path to the input directory to copy.

    Returns:
        str: The path to the newly created temporary directory.
    """
    temp_dir = mkdtemp()
    shutil.copytree(input_directory, temp_dir, dirs_exist_ok=True)
    return temp_dir


def test_replace_regex_version():
    pyproject_content = """
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "License :: OSI Approved :: MIT License"
    ]
"""

    content_after = re.sub(DEV_STATUS_REGEX, '\g<1>"{}"'.format("Development Status :: 4 - Beta"), pyproject_content)
    assert content_after != pyproject_content
    assert content_after.count("Development Status :: 4 - Beta") == 1


def test_classification_decision():
    inputVersionProduction = "1.0.0"
    inputVersionBeta = "1.0.0b1"
    inputVersionAlpha = "1.0.0a20250813001"

    decisionProduction = get_classification(inputVersionProduction)
    decisionBeta = get_classification(inputVersionBeta)
    decisionAlpha = get_classification(inputVersionAlpha)

    assert decisionProduction == "Development Status :: 5 - Production/Stable"
    assert decisionBeta == "Development Status :: 4 - Beta"
    assert decisionAlpha == "Development Status :: 4 - Beta"


@pytest.mark.parametrize("input_folder", [pyproject_folder, pyproject_beta_folder])
def test_set_dev_version_on_pyproject(input_folder):
    # Create a temp directory from the pyproject template
    temp_dir = create_temp_directory_from_template(input_folder)
    # Parse the setup for the project in the temp directory
    parsed = ParsedSetup.from_path(temp_dir)
    # Apply dev version with build id
    set_dev_version([parsed], "20250813001")
    # Re-parse after version update
    parsed_after = ParsedSetup.from_path(temp_dir)
    # Expect version to have 'a' suffix with zero-padded build id
    assert parsed_after.version == "0.0.1a20250813001"
    assert "Development Status :: 4 - Beta" in parsed_after.classifiers


def test_set_dev_version_on_setup():
    # Create a temp directory from the setup template
    temp_dir = create_temp_directory_from_template(setup_folder)
    # Parse the setup for the project in the temp directory
    parsed = ParsedSetup.from_path(temp_dir)
    # Apply dev version with build id
    set_dev_version([parsed], "20250813001")
    # Re-parse after version update
    parsed_after = ParsedSetup.from_path(temp_dir)
    # Expect version to have 'a' suffix with zero-padded build id
    assert parsed_after.version == "1.0.0a20250813001"
    assert "Development Status :: 4 - Beta" in parsed_after.classifiers
