# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline checks for the Rust wheel prototype's packaging configuration."""

from pathlib import Path
import runpy
from unittest.mock import patch

try:
    import tomllib
except ImportError:
    import tomli as tomllib


PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def _read_toml(path):
    with path.open("rb") as stream:
        return tomllib.load(stream)


def test_python_metadata_stays_aligned(monkeypatch):
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
    config = _read_toml(PACKAGE_ROOT / "pyproject.toml")
    source_inputs = {
        entry["path"] for entry in config["tool"]["maturin"]["include"]
        if entry["format"] == "sdist"
    }
    assert {"azure_cosmos_build_backend.py", "rust-toolchain.toml", "scripts/*.sh"} <= source_inputs
    for name in ("install-msrustup.sh", "configure-cargo-feed.sh"):
        assert (PACKAGE_ROOT / "scripts" / name).is_file()
