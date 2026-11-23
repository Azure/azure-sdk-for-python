import pytest
import tempfile
import os

from typing import List
from tempfile import TemporaryDirectory


@pytest.fixture()
def tmp_directory_create():
    with TemporaryDirectory() as tmp_dir:

        def create_temp_directory(fake_creation_paths: List[str]) -> TemporaryDirectory:
            for file in fake_creation_paths:
                target_path = os.path.join(tmp_dir, file)
                dirname = os.path.join(tmp_dir, os.path.dirname(file))

                if not os.path.exists(dirname):
                    os.mkdir(dirname)

                with open(target_path, "w"):
                    pass
            return tmp_dir

        yield create_temp_directory


@pytest.fixture
def maturin_package(tmp_path):
    package = tmp_path / "sdk" / "storage" / "azure-test-transfer"
    module = package / "azure" / "example" / "transfer"
    module.mkdir(parents=True)
    (package / "pyproject.toml").write_text(
        '[build-system]\nbuild-backend = "maturin"\n'
        '[project]\nname = "azure-test-transfer"\ndynamic = ["version"]\n'
        'requires-python = ">=3.10"\ndependencies = []\n'
        'classifiers = ["Development Status :: 4 - Beta"]\n',
        encoding="utf-8",
    )
    (package / "Cargo.toml").write_text(
        "[package]\nname = \"transfer-test\"\nversion = '0.1.0' # package version\n"
        '[dependencies]\nhelper = { version = "7.0.0" }\n',
        encoding="utf-8",
    )
    (package / "Cargo.lock").write_text(
        "version = 4\n"
        '[[package]]\nname = "helper"\nversion = "7.0.0"\n'
        'source = "registry+https://github.com/rust-lang/crates.io-index"\n'
        '[[package]]\nname = "transfer-test"\nversion = "0.1.0"\ndependencies = ["helper"]\n',
        encoding="utf-8",
    )
    (module / "__init__.py").write_text(
        'from importlib.metadata import version\n__version__ = version("azure-test-transfer")\n',
        encoding="utf-8",
    )
    return package
