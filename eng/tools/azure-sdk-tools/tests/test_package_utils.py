from pathlib import Path
import os
import json
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


def _write_mgmt_version_file(package_dir: Path, sdk_version: str):
    version_file = package_dir / "azure" / "mgmt" / package_dir.name.replace("azure-mgmt-", "") / "_version.py"
    version_file.parent.mkdir(parents=True, exist_ok=True)
    version_file.write_text(f'VERSION = "{sdk_version}"\n')


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


def test_preview_api_with_stable_sdk_version_adds_changelog_warning(tmp_path):
    package_name = "azure-mgmt-foo"
    package_dir = _create_basic_package(
        tmp_path,
        package_name,
        "## 1.0.0 (2026-07-27)\n\n### Features Added\n\n  - Initial version",
    )
    (package_dir / "_metadata.json").write_text(json.dumps({"apiVersion": "2026-01-01-preview"}))
    _write_mgmt_version_file(package_dir, "1.0.0")

    checker = pu.CheckFile(package_dir)
    checker.check_preview_api_version()
    checker.check_preview_api_version()

    changelog_content = (package_dir / "CHANGELOG.md").read_text()
    expected_warning = pu.PREVIEW_API_STABLE_VERSION_WARNING.format(
        sdk_version="1.0.0",
        api_version="2026-01-01-preview",
    )
    assert changelog_content.count(expected_warning) == 1
    assert ("## 1.0.0 (2026-07-27)\n\n" f"{expected_warning}\n\n" "### Features Added") in changelog_content


def test_stable_api_with_stable_sdk_version_does_not_add_changelog_warning(tmp_path):
    package_name = "azure-mgmt-foo"
    package_dir = _create_basic_package(
        tmp_path,
        package_name,
        "## 1.0.0 (2026-07-27)\n\n### Features Added\n\n  - Initial version",
    )
    (package_dir / "_metadata.json").write_text(json.dumps({"apiVersions": {"Foo": "2026-01-01"}}))
    _write_mgmt_version_file(package_dir, "1.0.0")

    pu.CheckFile(package_dir).check_preview_api_version()

    assert pu.PREVIEW_API_STABLE_VERSION_WARNING_PREFIX not in (package_dir / "CHANGELOG.md").read_text()


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


def test_get_version_info_skips_package_specific_version():
    with patch("pypi_tools.pypi.PyPIClient") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.get_ordered_versions.return_value = [Version("0.9.0"), Version("1.0.0b1")]

        result = pu.get_version_info("azure-mgmt-datatransfer", tag_is_stable=False)

    assert result == ("0.9.0", "0.9.0")
