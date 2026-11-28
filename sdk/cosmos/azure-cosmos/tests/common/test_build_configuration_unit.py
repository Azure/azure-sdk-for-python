# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests that read the package's build configuration files and check key settings.

Nothing is compiled. A wrong value here, such as the wrong Python version, a
missing processor type, or the wrong library version, would produce a package
that installs but is wrong, and such mistakes are often found only after release.
"""

from pathlib import Path
from functools import partial
import runpy
import shutil
import subprocess
import sys
from unittest.mock import patch

import pytest
from setuptools.errors import SetupError

try:
    import tomllib
except ImportError:
    import tomli as tomllib


PACKAGE_ROOT = Path(__file__).resolve().parents[2]

with pytest.MonkeyPatch.context() as _build_imports:
    # The build scripts are in the package folder, not in the installed SDK.
    _build_imports.syspath_prepend(str(PACKAGE_ROOT))
    import azure_cosmos_package_builder as build_backend
    import azure_cosmos_build_metadata as build_metadata


@pytest.fixture(name="setuptools_source")
def _setuptools_source(tmp_path):
    """Copy only the files setup.py needs into a temporary folder, so the tests
    cannot change the checkout."""
    for relative in (
        "setup.py",
        "azure_cosmos_build_metadata.py",
        "pyproject.toml",
        "api.metadata.yml",
        "README.md",
        "CHANGELOG.md",
        Path("azure") / "__init__.py",
        Path("azure") / "cosmos" / "__init__.py",
        Path("azure") / "cosmos" / "_version.py",
        Path("azure") / "cosmos" / "_rust.pyi",
    ):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PACKAGE_ROOT / relative, destination)
    return tmp_path


@pytest.mark.parametrize(
    "commands",
    [
        ["bdist_wheel"],
        ["sdist"],
        ["build"],
        ["build_py"],
        ["bdist_egg"],
        ["editable_wheel"],
        ["egg_info", "bdist_wheel"],
    ],
)
def test_setup_py_refuses_build_commands_rust(setuptools_source, commands):
    """setup.py only describes the package. Commands that build it (such as
    bdist_wheel or sdist) fail with a message that points to ``python -m build``,
    and leave no build output behind."""
    result = subprocess.run(
        [sys.executable, "setup.py", *commands],
        cwd=setuptools_source,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode != 0, result.stdout
    assert "setup.py is metadata-only" in result.stderr
    assert "python -m build" in result.stderr
    assert not (setuptools_source / "dist").exists()
    assert not (setuptools_source / "build").exists()
    assert not list(setuptools_source.glob("*.egg-info"))


@pytest.mark.parametrize(
    "commands", [["--name"], ["--version"], ["egg_info"], ["dist_info"]]
)
def test_setup_py_still_answers_metadata_commands_rust(
    setuptools_source, commands
):
    """Commands that only read package information (``--name``, ``--version``,
    ``egg_info``, ``dist_info``) still work and build nothing."""
    result = subprocess.run(
        [sys.executable, "setup.py", *commands],
        cwd=setuptools_source,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    if commands == ["--name"]:
        assert "azure-cosmos" in result.stdout
    elif commands == ["--version"]:
        assert build_metadata.validate_version_metadata(PACKAGE_ROOT) in result.stdout
    elif commands == ["egg_info"]:
        assert list(setuptools_source.glob("*.egg-info/PKG-INFO"))
    else:
        assert list(setuptools_source.glob("*.dist-info/METADATA"))
    assert not (setuptools_source / "dist").exists()
    assert not (setuptools_source / "build").exists()


@pytest.mark.parametrize("command", ["install", "develop"])
def test_setup_py_refuses_install_commands_rust(monkeypatch, command):
    """``install`` and ``develop`` raise SetupError before any command runs."""
    monkeypatch.chdir(PACKAGE_ROOT)
    with patch("setuptools.setup") as setup:
        runpy.run_path(str(PACKAGE_ROOT / "setup.py"))
    distribution = setup.call_args.kwargs["distclass"]()
    distribution.commands = [command]
    with patch("setuptools.Distribution.run_commands") as run_commands:
        with pytest.raises(SetupError, match="setup.py is metadata-only"):
            distribution.run_commands()
    run_commands.assert_not_called()


def _read_toml(path):
    """Read one configuration file and return its contents."""
    with path.open("rb") as stream:
        return tomllib.load(stream)


def test_pyproject_and_setup_py_metadata_match_rust(monkeypatch):
    """pyproject.toml and setup.py give the same name, version, Python requirement,
    dependencies and other fields, and the version matches ``_version.py``. If they
    differed, the package's details would depend on which tool built it.
    """
    project = _read_toml(PACKAGE_ROOT / "pyproject.toml")["project"]
    version = runpy.run_path(str(PACKAGE_ROOT / "azure" / "cosmos" / "_version.py"))["VERSION"]
    monkeypatch.chdir(PACKAGE_ROOT)
    with patch("setuptools.setup") as setup:
        runpy.run_path(str(PACKAGE_ROOT / "setup.py"))
    setup_py_args = setup.call_args.kwargs

    assert project["name"] == setup_py_args["name"] == "azure-cosmos"
    assert project["version"] == setup_py_args["version"] == version
    assert project["requires-python"] == setup_py_args["python_requires"] == ">=3.10"
    assert project["dependencies"] == setup_py_args["install_requires"]
    assert project["optional-dependencies"] == setup_py_args["extras_require"]
    assert project["classifiers"] == setup_py_args["classifiers"]
    assert project["description"] == setup_py_args["description"]
    assert project["license"] == {"text": setup_py_args["license"]}
    assert project["authors"] == [{"name": setup_py_args["author"], "email": setup_py_args["author_email"]}]
    assert project["maintainers"] == [
        {"name": setup_py_args["maintainer"], "email": setup_py_args["maintainer_email"]}
    ]
    assert project["keywords"] == [word.strip() for word in setup_py_args["keywords"].split(",")]
    assert project["urls"] == {"Homepage": setup_py_args["url"], **setup_py_args["project_urls"]}
    assert "Changelog" in project["urls"]
    readme = (PACKAGE_ROOT / project["readme"]).read_text(encoding="utf-8")
    assert setup_py_args["long_description"] == readme
    assert build_metadata.validate_version_metadata(PACKAGE_ROOT) == version


def test_wheel_targets_and_build_settings_rust():
    """pyproject.toml lists the expected wheels: one wheel per platform for Python
    3.10 and later, for Windows (x64, ARM64), Linux (x64, ARM64; none for
    musl-based Linux such as Alpine) and macOS (ARM64). It also pins maturin
    1.15.0 as the build tool and builds with the exact library versions in
    Cargo.lock. No wheel is built.
    """
    config = _read_toml(PACKAGE_ROOT / "pyproject.toml")
    wheels = config["tool"]["cibuildwheel"]
    assert wheels["build"] == ["cp310-*"]
    assert wheels["skip"] == ["*-musllinux*"]
    assert wheels["windows"]["archs"] == ["AMD64", "ARM64"]
    assert wheels["linux"]["archs"] == ["x86_64", "aarch64"]
    assert wheels["macos"]["archs"] == ["arm64"]
    assert wheels["linux"]["manylinux-x86_64-image"] == "manylinux_2_28"
    assert wheels["linux"]["manylinux-aarch64-image"] == "manylinux_2_28"
    assert config["build-system"]["requires"] == ["maturin==1.15.0"]
    assert config["build-system"]["build-backend"] == build_backend.__name__ == "azure_cosmos_package_builder"
    assert config["build-system"]["backend-path"] == ["."]
    assert config["tool"]["maturin"]["locked"] is True
    assert config["tool"]["maturin"]["module-name"] == "azure.cosmos._rust"
    assert config["tool"]["maturin"]["features"] == ["pyo3/extension-module"]


def test_driver_library_is_pinned_with_expected_features_rust():
    """The compiled module is built from the azure_data_cosmos_driver library at
    one fixed GitHub commit. Cargo.lock records the same commit, and no local copy
    is used. Customer builds turn on only the expected features. The test-only
    features (fault injection and an in-memory test service) are used only in
    development builds or with the test-probes feature.
    """
    workspace = _read_toml(PACKAGE_ROOT / "Cargo.toml")
    binding = _read_toml(PACKAGE_ROOT / "azure_cosmos_rust" / "Cargo.toml")
    driver = workspace["workspace"]["dependencies"]["azure_data_cosmos_driver"]
    assert driver == {
        "git": "https://github.com/Azure/azure-sdk-for-rust",
        "rev": "36c6f191ffe45ef44e5ef4efa26c59f0d71c3300",
    }
    for group in ("dependencies", "dev-dependencies"):
        dependency = binding[group]["azure_data_cosmos_driver"]
        assert dependency["workspace"] is True
        assert "path" not in dependency
    assert set(binding["dependencies"]["azure_data_cosmos_driver"]["features"]) == {
        "__internal_native_query_plan", "unstable_patch"
    }
    assert binding["dev-dependencies"]["azure_data_cosmos_driver"]["features"] == [
        "__internal_in_memory_emulator", "fault_injection"
    ]
    assert binding["features"]["test-probes"] == ["azure_data_cosmos_driver/fault_injection"]
    assert binding["features"]["default"] == ["extension-module"]
    assert binding["features"]["extension-module"] == ["pyo3/extension-module"]
    assert set(binding["dependencies"]["pyo3"]["features"]) == {
        "abi3-py310", "generate-import-lib"
    }
    lock = _read_toml(PACKAGE_ROOT / "Cargo.lock")
    locked_drivers = [package for package in lock["package"] if package["name"] == "azure_data_cosmos_driver"]
    assert len(locked_drivers) == 1
    assert locked_drivers[0]["source"] == (
        "git+https://github.com/Azure/azure-sdk-for-rust?rev=36c6f191ffe45ef44e5ef4efa26c59f0d71c3300"
        "#36c6f191ffe45ef44e5ef4efa26c59f0d71c3300"
    )


def test_minimum_compiler_version_matches_toolchain_rust():
    """The minimum compiler version in Cargo.toml (``rust-version``) matches the
    version in rust-toolchain.toml, without its ``ms-prod-`` prefix.
    """
    workspace = _read_toml(PACKAGE_ROOT / "Cargo.toml")["workspace"]["package"]
    channel = _read_toml(PACKAGE_ROOT / "rust-toolchain.toml")["toolchain"]["channel"]
    assert channel.removeprefix("ms-prod-") == workspace["rust-version"]


def test_windows_arm64_build_settings_rust():
    """Windows ARM64 wheels are built on an x64 machine, so the build must name the
    target processor (``CARGO_BUILD_TARGET``) and the folder with the ARM64 Python
    library (``PYO3_CROSS_LIB_DIR``). The whole override list is compared, so an
    extra override is also caught.
    """
    config = _read_toml(PACKAGE_ROOT / "pyproject.toml")
    overrides = config["tool"]["cibuildwheel"]["overrides"]
    assert overrides == [{
        "select": "*-win_arm64",
        "environment": {
            "CARGO_BUILD_TARGET": "aarch64-pc-windows-msvc",
            "PYO3_CROSS_LIB_DIR": "$PYTHON_ARM64_LIB_DIR",
        },
    }]


def test_source_archive_lists_build_files_rust():
    """The source archive settings include the build scripts, version files, tests
    and samples, and the two scripts named there exist. No archive is built.
    """
    config = _read_toml(PACKAGE_ROOT / "pyproject.toml")
    source_inputs = {
        entry["path"] for entry in config["tool"]["maturin"]["include"]
        if entry["format"] == "sdist"
    }
    assert {
        "azure_cosmos_package_builder.py",
        "azure_cosmos_build_metadata.py",
        "api.metadata.yml",
        "CHANGELOG.md",
        "rust-toolchain.toml",
        "scripts/*.sh",
        "samples/*.py",
        "tests/**/*",
    } <= source_inputs
    for name in ("install-msrustup.sh", "configure-cargo-feed.sh"):
        assert (PACKAGE_ROOT / "scripts" / name).is_file()


def test_wheel_leaves_out_shared_azure_namespace_file_rust():
    """The azure folder is shared by all azure-* packages, so the wheel must not
    include ``azure/__init__.py``."""
    excludes = _read_toml(PACKAGE_ROOT / "pyproject.toml")["tool"]["maturin"]["exclude"]
    namespace_rules = [
        entry for entry in excludes
        if (entry if isinstance(entry, str) else entry["path"]) == "azure/__init__.py"
    ]
    assert namespace_rules == [{"path": "azure/__init__.py", "format": "wheel"}]


@pytest.mark.parametrize(
    "stale_file",
    [
        "pyproject.toml",
        "api.metadata.yml",
        "CHANGELOG.md",
        Path("azure") / "cosmos" / "_version.py",
    ],
)
@pytest.mark.parametrize(
    "build_hook",
    [
        "build_wheel",
        "build_sdist",
        "build_editable",
        "prepare_metadata_for_build_wheel",
        "prepare_metadata_for_build_editable",
        "setup",
    ],
)
def test_every_build_entry_point_rejects_version_mismatch_rust(monkeypatch, tmp_path, stale_file, build_hook):
    """If the version in pyproject.toml, api.metadata.yml, CHANGELOG.md or
    ``_version.py`` differs from the others, every way of building the package
    (each build hook, and setup.py) raises "Package version mismatch" before
    building anything."""
    version = build_metadata.validate_version_metadata(PACKAGE_ROOT)
    for relative in ("pyproject.toml", "api.metadata.yml", "CHANGELOG.md", Path("azure") / "cosmos" / "_version.py"):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PACKAGE_ROOT / relative, destination)
    stale_path = tmp_path / stale_file
    stale_path.write_text(stale_path.read_text(encoding="utf-8").replace(version, "0.0.0"), encoding="utf-8")
    validate = partial(build_metadata.validate_version_metadata, tmp_path)
    if build_hook == "setup":
        monkeypatch.setattr(build_metadata, "validate_version_metadata", validate)
        monkeypatch.chdir(PACKAGE_ROOT)
        with patch("setuptools.setup") as builder:
            with pytest.raises(RuntimeError, match="Package version mismatch"):
                runpy.run_path(str(PACKAGE_ROOT / "setup.py"))
    else:
        monkeypatch.setattr(build_backend, "validate_version_metadata", validate)
        with patch.object(build_backend.maturin, build_hook) as builder:
            with pytest.raises(RuntimeError, match="Package version mismatch"):
                getattr(build_backend, build_hook)(str(tmp_path))
    builder.assert_not_called()
