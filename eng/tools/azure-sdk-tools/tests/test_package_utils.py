from pathlib import Path
import os
from unittest.mock import patch, MagicMock
from packaging.version import Version

try:
    import tomllib as toml
except Exception:  # pragma: no cover
    import tomli as toml  # type: ignore

import packaging_tools.package_utils as pu


def _create_basic_package(tmp_path: Path, package_name: str, version_line: str):
    package_dir = tmp_path / package_name
    package_dir.mkdir()

    # nested package init path per implementation logic
    nested_init_path = package_dir / package_name.replace("-", "/")
    nested_init_path.mkdir(parents=True, exist_ok=True)
    (nested_init_path / "__init__.py").write_text("__all__ = ['FooClient']\n")

    # changelog with version line
    (package_dir / "CHANGELOG.md").write_text(f"{version_line}\n")

    # minimal pyproject (can be empty, but create one to assert modifications)
    (package_dir / "pyproject.toml").write_text("[project]\nname='example'\n")

    # readme containing placeholder to be replaced
    (package_dir / "README.md").write_text("This is MyService client library.\n")

    return package_dir


def test_check_file_populates_pyproject_stable(tmp_path, monkeypatch):
    package_name = "azure-ai-foo"
    package_dir = _create_basic_package(tmp_path, package_name, "## 1.2.3 (2025-01-01)")

    # stub out build_packaging to avoid external side effects
    monkeypatch.setattr(pu, "build_packaging", lambda **kwargs: None)

    # run the function under test
    pu.check_file(package_dir)

    # validate pyproject.toml modifications
    with open(package_dir / "pyproject.toml", "rb") as fd:
        data = toml.load(fd)

    assert data["packaging"]["title"] == "FooClient"
    assert data["packaging"]["is_stable"] is True
    assert data["tool"]["azure-sdk-build"]["breaking"] is False
    assert data["tool"]["azure-sdk-build"]["pyright"] is False
    assert data["tool"]["azure-sdk-build"]["mypy"] is False

    # README placeholder replaced with pprint name ("Foo")
    readme_content = (package_dir / "README.md").read_text()
    assert "Foo" in readme_content and "MyService" not in readme_content


def test_check_file_sets_is_stable_false_for_beta(tmp_path, monkeypatch):
    package_name = "azure-ai-bar"
    package_dir = _create_basic_package(tmp_path, package_name, "## 2.0.0b1 (2025-01-01)")

    monkeypatch.setattr(pu, "build_packaging", lambda **kwargs: None)

    pu.check_file(package_dir)

    with open(package_dir / "pyproject.toml", "rb") as fd:
        data = toml.load(fd)

    assert data["packaging"]["is_stable"] is False
    # title still populated
    assert data["packaging"]["title"] == "FooClient"


def test_get_version_info_treats_0_0_0_as_invalid():
    """get_version_info should return empty strings when the latest PyPI version is 0.0.0."""
    with patch("pypi_tools.pypi.PyPIClient") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.get_ordered_versions.return_value = [Version("0.0.0")]

        result = pu.get_version_info("azure-some-package", tag_is_stable=False)

    assert result == ("", "")


def test_get_version_info_treats_0_0_0_prerelease_as_invalid():
    """get_version_info should return empty strings when the latest PyPI version is 0.0.0b1."""
    with patch("pypi_tools.pypi.PyPIClient") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.get_ordered_versions.return_value = [Version("0.0.0b1")]

        result = pu.get_version_info("azure-some-package", tag_is_stable=False)

    assert result == ("", "")


def test_get_version_info_does_not_filter_0_0_0_1():
    """get_version_info should NOT filter 0.0.0.1 — its base version is not 0.0.0."""
    with patch("pypi_tools.pypi.PyPIClient") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.get_ordered_versions.return_value = [Version("0.0.0.1")]

        result = pu.get_version_info("azure-some-package", tag_is_stable=False)

    assert result == ("0.0.0.1", "0.0.0.1")
