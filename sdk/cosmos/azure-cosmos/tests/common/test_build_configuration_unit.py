# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline checks that the files describing how this package is built still say what the
release process needs them to say.

Nothing here builds anything. These tests read the build configuration files and check
the values that, if changed by accident, would produce a package that looks fine and is
wrong: built for the wrong Python, missing an architecture, or built against a driver
from somebody's laptop instead of a fixed revision.

Those mistakes are expensive because they are usually found after publishing. Reading the
files takes no time and catches them in every run.
"""

from pathlib import Path
import runpy
from unittest.mock import patch

try:
    import tomllib
except ImportError:
    import tomli as tomllib


PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def _read_toml(path):
    """Read one configuration file and return its contents."""
    with path.open("rb") as stream:
        return tomllib.load(stream)


def test_python_metadata_stays_aligned(monkeypatch):
    """The two places that describe this package agree with each other and with the version file.

    The package is described both in the modern configuration file and in the older build
    script, which is still there for tooling that expects it. Six things have to match,
    including the version, which comes from a third place again.

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


def test_prototype_wheel_targets():
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
    assert config["build-system"]["build-backend"] == "azure_cosmos_build_backend"
    assert config["tool"]["maturin"]["locked"] is True
    assert config["tool"]["maturin"]["module-name"] == "azure.cosmos._rust"


def test_driver_source_and_features_are_preserved():
    """The driver is taken from a fixed published revision, never from a local folder.

    The check for no local path is the important one. Pointing at a folder on disk is the
    normal thing to do while working on both projects at once, and it is easy to commit by
    accident. When that happens the build either fails on a machine that lacks the folder
    or, worse, succeeds using whatever uncommitted state that folder happened to contain.

    The revision must be a full forty-character identifier, not a branch name, so it
    cannot move underneath the build. The recorded dependency list is checked to point at
    the same revision, since those two disagreeing means the build uses one and the
    recorded state describes the other.

    The optional features are listed explicitly because they change what the driver can
    do. Two are on for normal use; a separate one is on only for the driver's own tests,
    which is what keeps a built-in test service out of what customers receive.
    """
    workspace = _read_toml(PACKAGE_ROOT / "Cargo.toml")
    binding = _read_toml(PACKAGE_ROOT / "azure_cosmos_rust" / "Cargo.toml")
    driver = workspace["workspace"]["dependencies"]["azure_data_cosmos_driver"]
    assert driver["git"] == "https://github.com/Azure/azure-sdk-for-rust"
    assert len(driver["rev"]) == 40
    assert "path" not in driver
    for group in ("dependencies", "dev-dependencies"):
        dependency = binding[group]["azure_data_cosmos_driver"]
        assert dependency["workspace"] is True
        assert "path" not in dependency
    assert set(binding["dependencies"]["azure_data_cosmos_driver"]["features"]) == {
        "__internal_native_query_plan", "fault_injection"
    }
    assert binding["dev-dependencies"]["azure_data_cosmos_driver"]["features"] == [
        "__internal_in_memory_emulator"
    ]
    assert set(binding["dependencies"]["pyo3"]["features"]) == {
        "extension-module", "abi3-py310", "generate-import-lib"
    }
    lock = _read_toml(PACKAGE_ROOT / "Cargo.lock")
    locked_driver = next(package for package in lock["package"] if package["name"] == "azure_data_cosmos_driver")
    assert locked_driver["source"] == f"git+{driver['git']}?rev={driver['rev']}#{driver['rev']}"


def test_windows_cross_build_has_target_and_import_library_inputs():
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


def test_source_archive_declares_its_build_bootstrap_inputs():
    """Check declared source-archive inputs and the named scripts on disk.

    No archive is built or installed, so this does not verify actual archive
    contents or a successful source installation.
    """
    config = _read_toml(PACKAGE_ROOT / "pyproject.toml")
    source_inputs = {
        entry["path"] for entry in config["tool"]["maturin"]["include"]
        if entry["format"] == "sdist"
    }
    assert {"azure_cosmos_build_backend.py", "rust-toolchain.toml", "scripts/*.sh"} <= source_inputs
    for name in ("install-msrustup.sh", "configure-cargo-feed.sh"):
        assert (PACKAGE_ROOT / "scripts" / name).is_file()
