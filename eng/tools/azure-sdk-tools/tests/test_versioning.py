import os
import shutil
import re
import json
import sys
from tempfile import mkdtemp

import pytest
from packaging.requirements import Requirement

from ci_tools import functions
from ci_tools.parsing import ParsedSetup
from ci_tools.versioning.version_set_dev import set_dev_version
from ci_tools.versioning.version_shared import get_classification, set_version_py, DEV_STATUS_REGEX

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


@pytest.mark.parametrize(
    "python_version, cargo_version",
    [
        ("0.2.0", "0.2.0"),
        ("0.2.0b3", "0.2.0-beta.3"),
        ("0.2.0a20250813001", "0.2.0-alpha.20250813001"),
        ("0.2.0rc2", "0.2.0-rc.2"),
        ("0.2.0.dev4", "0.2.0-dev.4"),
    ],
)
def test_set_maturin_version_preserves_other_manifest_and_lock_entries(maturin_package, python_version, cargo_version):
    cargo = maturin_package / "Cargo.toml"
    lock = maturin_package / "Cargo.lock"
    original_cargo = cargo.read_text()
    original_lock = lock.read_text()

    set_version_py(str(maturin_package / "pyproject.toml"), python_version)

    assert cargo.read_text() == original_cargo.replace("'0.1.0'", f"'{cargo_version}'")
    assert lock.read_text() == original_lock.replace('"0.1.0"', f'"{cargo_version}"')
    assert ParsedSetup.from_path(str(maturin_package)).version == python_version


@pytest.mark.parametrize("version", ["not-a-version", "1.2", "1!1.2.3", "1.2.3.post1", "18446744073709551616.0.0"])
def test_set_maturin_version_rejects_unsupported_versions_without_writing(maturin_package, version):
    cargo = maturin_package / "Cargo.toml"
    lock = maturin_package / "Cargo.lock"
    before = cargo.read_bytes(), lock.read_bytes()

    with pytest.raises(ValueError):
        set_version_py(str(maturin_package / "pyproject.toml"), version)

    assert (cargo.read_bytes(), lock.read_bytes()) == before


def test_set_maturin_version_rejects_stale_lock_without_writing(maturin_package):
    cargo = maturin_package / "Cargo.toml"
    lock = maturin_package / "Cargo.lock"
    lock.write_text(lock.read_text().replace('"0.1.0"', '"0.0.9"'))
    before = cargo.read_bytes(), lock.read_bytes()

    with pytest.raises(ValueError, match="Cargo.lock"):
        set_version_py(str(maturin_package / "pyproject.toml"), "0.2.0")

    assert (cargo.read_bytes(), lock.read_bytes()) == before


def test_set_maturin_version_without_lock(maturin_package):
    lock = maturin_package / "Cargo.lock"
    lock.unlink()

    set_version_py(str(maturin_package / "pyproject.toml"), "0.2.0b1")

    assert ParsedSetup.from_path(str(maturin_package)).version == "0.2.0b1"
    assert not lock.exists()


def test_set_maturin_version_with_custom_manifest_path(maturin_package):
    manifest_dir = maturin_package / "native"
    manifest_dir.mkdir()
    (maturin_package / "Cargo.toml").rename(manifest_dir / "Cargo.toml")
    (maturin_package / "Cargo.lock").rename(manifest_dir / "Cargo.lock")
    pyproject = maturin_package / "pyproject.toml"
    with pyproject.open("a") as stream:
        stream.write('\n[tool.maturin]\nmanifest-path = "native/Cargo.toml"\n')

    set_version_py(str(pyproject), "0.2.0b1")

    assert ParsedSetup.from_path(str(maturin_package)).version == "0.2.0b1"
    assert 'version = "0.2.0-beta.1"' in (manifest_dir / "Cargo.lock").read_text()


def test_set_maturin_version_rejects_workspace_without_writing(maturin_package):
    cargo = maturin_package / "Cargo.toml"
    lock = maturin_package / "Cargo.lock"
    (maturin_package.parent / "Cargo.toml").write_text("[workspace]\n")
    before = cargo.read_bytes(), lock.read_bytes()

    with pytest.raises(ValueError, match="workspace"):
        set_version_py(str(maturin_package / "pyproject.toml"), "0.2.0")

    assert (cargo.read_bytes(), lock.read_bytes()) == before


@pytest.mark.parametrize(
    "tool, extra_args, expected",
    [
        ("set", ["--new-version", "0.2.0b1"], "0.2.0b1"),
        ("increment", [], "0.1.1"),
        ("dev", ["--build-id", "20250813.1"], "0.1.0a20250813001"),
    ],
)
def test_version_commands_update_maturin_cargo(maturin_package, monkeypatch, tool, extra_args, expected):
    from ci_tools.versioning import version_increment, version_set, version_set_dev

    monkeypatch.setattr(version_set, "update_change_log", lambda *args, **kwargs: None)
    monkeypatch.setattr(version_increment, "update_change_log", lambda *args, **kwargs: None)
    monkeypatch.setattr(version_set_dev, "process_requires", lambda *args: None)
    args = ["sdk-version", "azure-test-transfer", "--service", "storage", "--repo", str(maturin_package.parents[2])]
    if tool != "dev":
        args += ["--package-name", "azure-test-transfer"]
    monkeypatch.setattr(sys, "argv", args + extra_args)
    {
        "set": version_set.version_set_main,
        "increment": version_increment.version_increment_main,
        "dev": version_set_dev.version_set_dev_main,
    }[tool]()

    assert ParsedSetup.from_path(str(maturin_package)).version == expected


def test_increment_maturin_dev_version(maturin_package, monkeypatch):
    from ci_tools.versioning import version_increment

    set_version_py(str(maturin_package / "pyproject.toml"), "0.2.0.dev4")
    monkeypatch.setattr(version_increment, "update_change_log", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sdk_increment_version",
            "azure-test-transfer",
            "--package-name",
            "azure-test-transfer",
            "--service",
            "storage",
            "--repo",
            str(maturin_package.parents[2]),
        ],
    )
    version_increment.version_increment_main()

    assert ParsedSetup.from_path(str(maturin_package)).version == "0.2.0b1"


def test_dev_version_reports_cargo_update_failure(maturin_package, monkeypatch):
    lock = maturin_package / "Cargo.lock"
    lock.write_text(lock.read_text().replace('"0.1.0"', '"0.0.9"'))
    monkeypatch.setattr("ci_tools.versioning.version_set_dev.process_requires", lambda *args: None)

    with pytest.raises(ValueError, match="Cargo.lock"):
        set_dev_version([ParsedSetup.from_path(str(maturin_package))], "20250813001")


def test_dev_build_updates_maturin_version(maturin_package, monkeypatch):
    from ci_tools import build

    monkeypatch.setattr(build, "process_requires", lambda *args: None)
    built = []
    monkeypatch.setattr(build, "create_package", lambda *args: built.append(args))

    build.build_packages([str(maturin_package)], is_dev_build=True, build_id="20250813001")

    assert ParsedSetup.from_path(str(maturin_package)).version == "0.1.0a20250813001"
    assert len(built) == 1


def test_find_invalid_versions_accepts_maturin_metadata_version(maturin_package, monkeypatch, capsys):
    from ci_tools.versioning.find_invalid_versions import find_invalid_versions_main

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sdk_find_invalid_versions",
            "azure-test-transfer",
            "--service",
            "storage",
            "--repo",
            str(maturin_package.parents[2]),
        ],
    )
    find_invalid_versions_main()
    assert "No invalid packages found" in capsys.readouterr().out


def test_find_invalid_versions_still_checks_python_init(maturin_package, monkeypatch, capsys):
    from ci_tools.versioning.find_invalid_versions import find_invalid_versions_main

    pyproject = maturin_package / "pyproject.toml"
    pyproject.write_text(pyproject.read_text().replace('"maturin"', '"setuptools.build_meta"'))
    module = maturin_package / "azure" / "example" / "transfer"
    (module / "_version.py").write_text('VERSION = "0.1.0"\n')
    (module / "__init__.py").write_text("value = 1\n")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sdk_find_invalid_versions",
            "azure-test-transfer",
            "--service",
            "storage",
            "--repo",
            str(maturin_package.parents[2]),
        ],
    )
    with pytest.raises(SystemExit) as exc:
        find_invalid_versions_main()
    assert exc.value.code == 1
    assert "Could not find __version__ = VERSION" in capsys.readouterr().out


@pytest.mark.parametrize("filename", ["setup.py", "pyproject.toml"])
@pytest.mark.parametrize(
    "requirement",
    [
        "azure-ai-agentserver-core>=2.3.0b2,<3.0.0",
        "azure-ai-agentserver-core<3.0.0,>=2.3.0b2",
        "azure-ai-agentserver-core >= 2.3.0b2, < 3.0.0",
    ],
)
@pytest.mark.parametrize("is_dev_build, available_on_pypi", [(False, False), (True, True), (False, True)])
def test_process_requires_updates_original_requirement_text(
    tmp_path, monkeypatch, filename, requirement, is_dev_build, available_on_pypi
):
    dependencies = json.dumps([requirement, "requests>=2.0.0"])
    if filename == "pyproject.toml":
        contents = f'[project]\nname = "test-package"\nversion = "1.0.0"\ndependencies = {dependencies}\n'
    else:
        contents = (
            "from setuptools import setup\n"
            f'setup(name="test-package", version="1.0.0", install_requires={dependencies})\n'
        )
    path = tmp_path / filename
    path.write_text(contents, encoding="utf-8")
    monkeypatch.setattr(functions, "is_required_version_on_pypi", lambda *args: available_on_pypi)
    monkeypatch.setattr(functions, "get_version_from_repo", lambda *args: "2.3.0b3")
    monkeypatch.setattr(functions, "get_base_version", lambda *args: "2.3.0")

    functions.process_requires(str(path), is_dev_build=is_dev_build)

    replacement = "azure-ai-agentserver-core<3.0.0,>=2.3.0a1,<2.3.0b0"
    should_update = is_dev_build or not available_on_pypi
    expected = contents.replace(requirement, replacement) if should_update else contents
    assert path.read_text(encoding="utf-8") == expected
    requirements = [Requirement(value) for value in ParsedSetup.from_path(str(path)).requires]
    core = next(value for value in requirements if value.name == "azure-ai-agentserver-core")
    assert core.specifier.contains("2.3.0a20261029003", prereleases=True) is should_update
    assert core.specifier.contains("2.3.0b2", prereleases=True) is not should_update
