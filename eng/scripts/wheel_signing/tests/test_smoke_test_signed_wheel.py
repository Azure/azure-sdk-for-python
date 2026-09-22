# Unit coverage for smoke_test_signed_wheel.py's pure helper logic: wheel-name parsing and
# compiled-module discovery from distribution metadata. The actual pip install + import path is
# exercised for real by the Smoke_Windows/Smoke_macOS pipeline jobs on their native OS, not here.

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import smoke_test_signed_wheel  # noqa: E402


class _FakePackagePath(str):
    """Mimics importlib.metadata's PackagePath: str(file) is the full relative path (this
    class *is* a str), while file.name is only the basename, matching pathlib.PurePath.name."""

    @property
    def name(self) -> str:
        return Path(str(self)).name


def _fake_file(relative_path: str) -> _FakePackagePath:
    return _FakePackagePath(relative_path)


def test_distribution_name_from_wheel():
    assert (
        smoke_test_signed_wheel.distribution_name_from_wheel("azure_template_two-1.0.0-cp310-abi3-win_amd64.whl")
        == "azure_template_two"
    )


def test_find_compiled_modules_windows_pyd(tmp_path):
    fake_dist = SimpleNamespace(
        files=[
            _fake_file("azure/template/two/__init__.py"),
            _fake_file("azure/template/two/_native.cp310-win_amd64.pyd"),
            _fake_file("azure_template_two-1.0.0.dist-info/RECORD"),
        ]
    )
    with patch("smoke_test_signed_wheel.metadata.distribution", return_value=fake_dist):
        modules = smoke_test_signed_wheel.find_compiled_modules("azure-template-two")

    assert modules == ["azure.template.two._native"]


def test_find_compiled_modules_mac_so(tmp_path):
    fake_dist = SimpleNamespace(
        files=[
            _fake_file("azure/template/two/_native.cpython-310-darwin.so"),
            _fake_file("azure/template/two/__init__.py"),
        ]
    )
    with patch("smoke_test_signed_wheel.metadata.distribution", return_value=fake_dist):
        modules = smoke_test_signed_wheel.find_compiled_modules("azure-template-two")

    assert modules == ["azure.template.two._native"]


def test_find_compiled_modules_skips_vendored_dependency_libs():
    # delocate vendors a package's native dependencies under `<pkg>/.dylibs/`; auditwheel
    # vendors them under `<dist>.libs/` at the wheel root. Both are signable but neither is an
    # importable Python module, so they must not produce a bogus dotted module path.
    fake_dist = SimpleNamespace(
        files=[
            _fake_file("azure/cosmos/_rust.abi3.so"),
            _fake_file("azure/cosmos/.dylibs/libssl.dylib"),
            _fake_file("azure_cosmos.libs/libcrypto-abcdef.so"),
            _fake_file("azure/cosmos/__init__.py"),
        ]
    )
    with patch("smoke_test_signed_wheel.metadata.distribution", return_value=fake_dist):
        modules = smoke_test_signed_wheel.find_compiled_modules("azure-cosmos")

    assert modules == ["azure.cosmos._rust"]


def test_find_compiled_modules_compiled_init_maps_to_parent_package():
    fake_dist = SimpleNamespace(
        files=[
            _fake_file("azure/cosmos/__init__.cpython-310-x86_64-linux-gnu.so"),
        ]
    )
    with patch("smoke_test_signed_wheel.metadata.distribution", return_value=fake_dist):
        modules = smoke_test_signed_wheel.find_compiled_modules("azure-cosmos")

    assert modules == ["azure.cosmos"]


def test_find_compiled_modules_raises_when_none_found():
    fake_dist = SimpleNamespace(files=[_fake_file("azure/template/two/__init__.py")])
    with patch("smoke_test_signed_wheel.metadata.distribution", return_value=fake_dist):
        modules = smoke_test_signed_wheel.find_compiled_modules("azure-template-two")

    assert modules == []


def test_find_wheel_requires_exactly_one(tmp_path):
    with pytest.raises(FileNotFoundError):
        smoke_test_signed_wheel.find_wheel(str(tmp_path))

    (tmp_path / "a-1.0.0-py3-none-any.whl").touch()
    (tmp_path / "b-1.0.0-py3-none-any.whl").touch()
    with pytest.raises(RuntimeError, match="Expected exactly one wheel"):
        smoke_test_signed_wheel.find_wheel(str(tmp_path))
