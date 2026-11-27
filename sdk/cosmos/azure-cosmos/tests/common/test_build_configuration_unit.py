# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline checks that the files describing how this package is built still say what the
release process needs them to say.

No test compiles Rust. These tests read the build configuration files and check
the values that, if changed by accident, would produce a package that looks fine and is
wrong: built for the wrong Python, missing an architecture, or built against a driver
from somebody's laptop instead of a fixed revision.

Those mistakes are expensive because they are usually found after publishing. Reading the
files takes no time and catches them in every run.
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
    # Build helpers belong to the checkout, not to the installed SDK wheel.
    _build_imports.syspath_prepend(str(PACKAGE_ROOT))
    import azure_cosmos_package_builder as build_backend
    import azure_cosmos_build_metadata as build_metadata


@pytest.fixture(name="setuptools_source")
def _setuptools_source(tmp_path):
    """Copy only packaging inputs so rejected commands cannot affect the checkout."""
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
def test_setuptools_artifact_commands_fail_closed_rust(setuptools_source, commands):
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
def test_setuptools_metadata_commands_remain_available_rust(
    setuptools_source, commands
):
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
def test_setuptools_install_commands_never_execute_rust(monkeypatch, command):
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


def test_python_metadata_stays_aligned_rust(monkeypatch):
    """The two places that describe this package agree with each other and with the version file.

    The package is described both in the modern configuration file and in the older build
    script, which is still there for tooling that expects it. Every field written in both
    has to match, including the version, which comes from a third place again.

    The older script is run with the function that would actually build replaced, so what
    it was about to be told can be read back. Two descriptions that drift apart produce a
    package whose declared dependencies or supported Python versions depend on which tool
    did the building.
    """
    project = _read_toml(PACKAGE_ROOT / "pyproject.toml")["project"]
    version = runpy.run_path(str(PACKAGE_ROOT / "azure" / "cosmos" / "_version.py"))["VERSION"]
    monkeypatch.chdir(PACKAGE_ROOT)
    with patch("setuptools.setup") as setup:
        runpy.run_path(str(PACKAGE_ROOT / "setup.py"))
    legacy = setup.call_args.kwargs

    assert project["name"] == legacy["name"] == "azure-cosmos"
    assert project["version"] == legacy["version"] == version
    assert project["requires-python"] == legacy["python_requires"] == ">=3.10"
    assert project["dependencies"] == legacy["install_requires"]
    assert project["optional-dependencies"] == legacy["extras_require"]
    assert project["classifiers"] == legacy["classifiers"]
    assert project["description"] == legacy["description"]
    assert project["license"] == {"text": legacy["license"]}
    assert project["authors"] == [{"name": legacy["author"], "email": legacy["author_email"]}]
    assert project["maintainers"] == [
        {"name": legacy["maintainer"], "email": legacy["maintainer_email"]}
    ]
    assert project["keywords"] == [word.strip() for word in legacy["keywords"].split(",")]
    assert project["urls"] == {"Homepage": legacy["url"], **legacy["project_urls"]}
    assert "Changelog" in project["urls"]
    readme = (PACKAGE_ROOT / project["readme"]).read_text(encoding="utf-8")
    assert legacy["long_description"] == readme
    assert build_metadata.validate_version_metadata(PACKAGE_ROOT) == version


def test_prototype_wheel_targets_rust():
    """Check declared wheel targets, builder version, and locked-build settings.

    These assertions do not build wheels, prove binary reproducibility, or
    establish that the resulting packages run on every listed platform.
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


def test_driver_source_and_features_are_preserved_rust():
    """The driver comes from one pinned GitHub commit, so CI needs no Rust checkout.

    Both dependency groups inherit the same source. The lock must record that
    same commit, with no second copy of the driver from a local folder.
    The optional features are listed explicitly because they change what the driver can
    do. Query planning and PATCH support are on for normal use; fault injection
    requires test-probes or native Rust tests. The built-in test service is a
    development dependency, so it is absent from customer builds.
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


def test_declared_minimum_rust_matches_the_toolchain_rust():
    """``rust-version`` names the only compiler CI builds with, so the promise stays true.

    Changing the ``rust-toolchain.toml`` channel without updating ``rust-version``
    fails here.
    """
    workspace = _read_toml(PACKAGE_ROOT / "Cargo.toml")["workspace"]["package"]
    channel = _read_toml(PACKAGE_ROOT / "rust-toolchain.toml")["toolchain"]["channel"]
    assert channel.removeprefix("ms-prod-") == workspace["rust-version"]


def test_windows_cross_build_has_target_and_import_library_inputs_rust():
    """Building for Windows on ARM needs two settings, and both are still there.

    This build happens on an Intel machine producing a package for a different processor,
    so the compiler has to be told what it is aiming at and where to find the matching
    Python library. Without them the build either fails outright or quietly produces
    something for the wrong processor.

    The whole list is compared rather than just these entries, so an added override that
    happens to match first cannot go unnoticed.
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


def test_source_archive_declares_its_build_and_ci_inputs_rust():
    """Check declared source-archive inputs and the named scripts on disk.

    No archive is built or installed, so this does not verify actual archive
    contents or a successful source installation.
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
    """Other azure-* packages share the azure folder, so the wheel must not own it."""
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
def test_build_routes_reject_version_drift_rust(monkeypatch, tmp_path, stale_file, build_hook):
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
