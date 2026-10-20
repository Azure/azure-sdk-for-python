import os
import shutil
import re
from tempfile import mkdtemp

import pytest

from ci_tools.parsing import ParsedSetup
from ci_tools.versioning.version_set_dev import set_dev_version
from ci_tools.versioning.version_shared import get_classification, DEV_STATUS_REGEX
from ci_tools.versioning.version_shared import synchronized_version_update, set_version_py
from ci_tools.parsing.parse_functions import get_pyproject_dict
from packaging_tools.sdk_update_version import main as update_version
from pathlib import Path
from ci_tools.versioning import version_set, version_increment

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


@pytest.fixture
def synchronized_package(tmp_path):
    namespace = tmp_path / "azure" / "widget"
    namespace.mkdir(parents=True)
    (namespace / "_version.py").write_text('VERSION = "1.0.0"\n', encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "azure-test"\nversion = "1.0.0"\n'
        'requires-python = ">=3.10"\ndependencies = []\n'
        'classifiers = ["Development Status :: 5 - Production/Stable"]\n'
        "[tool.azure-sdk-build]\nsynchronize-version-metadata = true\n",
        encoding="utf-8",
    )
    (tmp_path / "api.metadata.yml").write_text("apiHash: keep\npackageVersion: 1.0.0\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(
        "## Release History\n### 1.0.0 (Unreleased)\n\nChanges.\n\n### 0.9.0 (2025-01-01)\n\nHistory.\n",
        encoding="utf-8",
    )
    (tmp_path / "setup.py").write_text(
        'classifiers = ["Development Status :: 5 - Production/Stable"]\n', encoding="utf-8"
    )
    return tmp_path


def assert_synchronized_version(root, version):
    assert get_pyproject_dict(str(root / "pyproject.toml"))["project"]["version"] == version
    assert f'VERSION = "{version}"' in (root / "azure" / "widget" / "_version.py").read_text()
    assert f"packageVersion: {version}" in (root / "api.metadata.yml").read_text()
    assert f"### {version} (" in (root / "CHANGELOG.md").read_text()
    assert "### 0.9.0 (2025-01-01)\n\nHistory." in (root / "CHANGELOG.md").read_text()
    assert "apiHash: keep" in (root / "api.metadata.yml").read_text()


@pytest.mark.parametrize("version", ["1.0.1", "1.1.0b1"])
def test_release_updater_synchronizes_static_metadata(synchronized_package, version):
    update_version(synchronized_package, version=version, release_date="2026-10-19")
    assert_synchronized_version(synchronized_package, version)
    assert f"### {version} (2026-10-19)" in (synchronized_package / "CHANGELOG.md").read_text()
    classifier = get_classification(version)
    assert classifier in (synchronized_package / "setup.py").read_text()
    assert classifier in (synchronized_package / "pyproject.toml").read_text()


def test_dev_updater_synchronizes_static_metadata(synchronized_package):
    parsed = ParsedSetup.from_path(str(synchronized_package))
    set_dev_version([parsed], "20261019001")
    assert_synchronized_version(synchronized_package, "1.0.0a20261019001")


@pytest.mark.parametrize("failure", ["updater", "changelog", "write"])
def test_synchronized_update_restores_all_original_bytes(synchronized_package, monkeypatch, failure):
    originals = {file: file.read_bytes() for file in synchronized_package.rglob("*") if file.is_file()}
    if failure == "write":
        write_bytes = Path.write_bytes

        def fail_metadata_write(file, data):
            if file.name == "api.metadata.yml" and b"1.0.1" in data:
                raise OSError("injected write failure")
            return write_bytes(file, data)

        monkeypatch.setattr(Path, "write_bytes", fail_metadata_write)
    expected_error = {
        "updater": (RuntimeError, "injected updater failure"),
        "changelog": (ValueError, "Latest changelog version"),
        "write": (OSError, "injected write failure"),
    }[failure]
    with pytest.raises(expected_error[0], match=expected_error[1]):
        with synchronized_version_update(synchronized_package):
            set_version_py(str(synchronized_package / "pyproject.toml"), "1.0.1")
            if failure == "updater":
                raise RuntimeError("injected updater failure")
            if failure == "write":
                changelog = synchronized_package / "CHANGELOG.md"
                changelog.write_text(changelog.read_text().replace("1.0.0", "1.0.1"), encoding="utf-8")
    assert {file: file.read_bytes() for file in originals} == originals


def test_synchronized_update_preserves_other_toml_versions(synchronized_package):
    project = synchronized_package / "pyproject.toml"
    with project.open("a", encoding="utf-8") as stream:
        stream.write('[tool.example]\nversion = "99.0.0"\n')
    update_version(synchronized_package, version="1.0.1", release_date="2026-10-19")
    assert get_pyproject_dict(str(project))["tool"]["example"]["version"] == "99.0.0"


@pytest.mark.parametrize("module", [version_set, version_increment])
@pytest.mark.parametrize("fails", [False, True])
def test_release_entrypoints_synchronize_or_roll_back(synchronized_package, monkeypatch, module, fails):
    parsed = ParsedSetup.from_path(str(synchronized_package))
    originals = {file: file.read_bytes() for file in synchronized_package.rglob("*") if file.is_file()}
    monkeypatch.setattr(module, "get_packages", lambda *_args, **_kwargs: [parsed])

    def update_changelog(_setup, version, *_args, **_kwargs):
        if fails:
            raise RuntimeError("changelog command failed")
        changelog = synchronized_package / "CHANGELOG.md"
        changelog.write_text(
            changelog.read_text().replace("### 1.0.0", f"### {version} (Unreleased)\n\n### 1.0.0"),
            encoding="utf-8",
        )

    monkeypatch.setattr(module, "update_change_log", update_changelog)
    args = ["version-command", "--package-name", "azure-test", "--service", "test", "--repo", str(synchronized_package)]
    if module is version_set:
        args.extend(["--new-version", "1.0.1"])
        command = module.version_set_main
    else:
        command = module.version_increment_main
    monkeypatch.setattr("sys.argv", args)
    if fails:
        with pytest.raises(RuntimeError, match="changelog command failed"):
            command()
        assert {file: file.read_bytes() for file in originals} == originals
    else:
        command()
        assert_synchronized_version(synchronized_package, "1.0.1")
        assert "### 1.0.0 (Unreleased)" in (synchronized_package / "CHANGELOG.md").read_text()


def test_dev_update_propagates_synchronization_failure(synchronized_package):
    parsed = ParsedSetup.from_path(str(synchronized_package))
    (synchronized_package / "api.metadata.yml").write_text("apiHash: keep\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Expected exactly one version"):
        set_dev_version([parsed], "20261019001")
    assert parsed.version == ParsedSetup.from_path(str(synchronized_package)).version
