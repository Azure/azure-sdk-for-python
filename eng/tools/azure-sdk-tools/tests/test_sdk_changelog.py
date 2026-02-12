import pytest
from unittest.mock import patch
from pathlib import Path
import tempfile
import shutil

from packaging_tools.sdk_changelog import main as changelog_main


@pytest.fixture
def temp_package():
    temp_dir = tempfile.mkdtemp()
    package_path = Path(temp_dir)
    changelog_path = package_path / "CHANGELOG.md"
    with open(changelog_path, "w") as f:
        f.write("# Release History\n\n")

    yield package_path, changelog_path

    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_arm_package():
    temp_dir = tempfile.mkdtemp()
    package_path = Path(temp_dir) / "azure-mgmt-test"
    package_path.mkdir(parents=True, exist_ok=True)
    changelog_path = package_path / "CHANGELOG.md"
    with open(changelog_path, "w") as f:
        f.write("# Release History\n\n")

    yield package_path, changelog_path

    shutil.rmtree(temp_dir)


@patch("packaging_tools.sdk_changelog.get_changelog_content")
def test_update_changelog_new_version(mock_get_changelog_content, temp_package):
    package_path, changelog_path = temp_package
    mock_get_changelog_content.return_value = ("### Features\n\n- New feature", "1.0.0")

    changelog_main(package_path)

    with open(changelog_path, "r") as f:
        content = f.read()

    assert "## 0.0.0 (UnReleased)" in content
    assert "### Features\n\n- New feature" in content


@patch("packaging_tools.sdk_changelog.get_changelog_content")
def test_update_changelog_initial_version(mock_get_changelog_content, temp_package):
    package_path, changelog_path = temp_package
    mock_get_changelog_content.return_value = ("", None)

    changelog_main(package_path)

    with open(changelog_path, "r") as f:
        content = f.read()

    assert "## 0.0.0 (UnReleased)" in content
    assert "- Initial version" in content


def test_changelog_error_log_for_arm_sdk(monkeypatch, temp_arm_package):
    package_path, _ = temp_arm_package
    log_level = None
    called = False

    def mock_get_changelog_content(*args, **kwargs):
        return ("", None)

    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level, called
        called = True
        log_level = enable_log_error

    monkeypatch.setattr("packaging_tools.sdk_changelog.get_changelog_content", mock_get_changelog_content)
    monkeypatch.setattr("packaging_tools.sdk_changelog.log_failed_message", mock_log_failed_message)
    changelog_main(package_path)

    assert called
    assert (
        log_level is True
    ), "Expected error log to be enabled for invalid changelog content in ARM SDK if not in pipeline"


def test_valid_changelog_no_log_for_arm_sdk(monkeypatch, temp_arm_package):
    package_path, _ = temp_arm_package
    log_level = None
    called = False

    def mock_get_changelog_content(*args, **kwargs):
        return ("### Features Added", None)

    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level, called
        called = True
        log_level = enable_log_error

    monkeypatch.setattr("packaging_tools.sdk_changelog.get_changelog_content", mock_get_changelog_content)
    monkeypatch.setattr("packaging_tools.sdk_changelog.log_failed_message", mock_log_failed_message)
    changelog_main(package_path)

    assert not called
    assert log_level is None, "Expected no error log for valid changelog content in ARM SDK"


def test_changelog_warning_log_for_arm_sdk(monkeypatch, temp_arm_package):
    package_path, _ = temp_arm_package
    log_level = None
    called = False

    def mock_get_changelog_content(*args, **kwargs):
        return ("", "3.0.0")

    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level, called
        called = True
        log_level = enable_log_error

    monkeypatch.setattr("packaging_tools.sdk_changelog.get_changelog_content", mock_get_changelog_content)
    monkeypatch.setattr("packaging_tools.sdk_changelog.log_failed_message", mock_log_failed_message)
    package_result = {"test": True}
    changelog_main(package_path, package_result=package_result)

    changelog = package_result.get("changelog") or {}
    assert isinstance(changelog, dict), "Expected changelog entry in package_result for ARM SDK"
    assert changelog.get("content") == "", "Expected no changelog content in package_result for ARM SDK"
    assert changelog.get("hasBreakingChange") is False
    assert changelog.get("breakingChangeItems") == []
    assert package_result.get("version") == "3.0.0"

    assert called
    assert (
        log_level is False
    ), "Expected warning log to be enabled for invalid changelog content in ARM SDK if in pipeline"


@patch("packaging_tools.sdk_changelog.get_changelog_content")
def test_regeneration_replaces_existing_unreleased_section(mock_get_changelog_content, temp_package):
    """When re-generating, an existing unreleased version section should be replaced, not duplicated."""
    package_path, changelog_path = temp_package

    # Simulate a CHANGELOG after a previous generation + version update
    with open(changelog_path, "w") as f:
        f.write(
            "# Release History\n"
            "\n"
            "## 1.1.0b2 (2025-10-08)\n"
            "\n"
            "### Features Added\n"
            "\n"
            "  - Old feature\n"
            "\n"
            "## 1.1.0b1 (2025-09-01)\n"
            "\n"
            "### Other Changes\n"
            "\n"
            "  - Initial version\n"
        )

    # Re-generate with last_version = "1.1.0b1" (from PyPI), so "1.1.0b2" is unreleased
    mock_get_changelog_content.return_value = ("### Features Added\n\n  - New feature\n", "1.1.0b1")
    changelog_main(package_path)

    with open(changelog_path, "r") as f:
        content = f.read()

    # Should have the new content replacing the old unreleased section
    assert content.count("## 0.0.0 (UnReleased)") == 1, "Should have exactly one version entry for unreleased"
    assert "  - New feature" in content
    assert "  - Old feature" not in content
    # The previous released version should still be present
    assert "## 1.1.0b1 (2025-09-01)" in content
    assert "  - Initial version" in content


@patch("packaging_tools.sdk_changelog.get_changelog_content")
def test_regeneration_replaces_unreleased_placeholder(mock_get_changelog_content, temp_package):
    """When re-generating before version update, the 0.0.0 placeholder should be replaced."""
    package_path, changelog_path = temp_package

    # Simulate a CHANGELOG after a previous generation (before version update)
    with open(changelog_path, "w") as f:
        f.write(
            "# Release History\n"
            "\n"
            "## 0.0.0 (UnReleased)\n"
            "\n"
            "### Features Added\n"
            "\n"
            "  - Old feature\n"
            "\n"
            "## 1.0.0 (2025-01-01)\n"
            "\n"
            "### Other Changes\n"
            "\n"
            "  - Initial version\n"
        )

    mock_get_changelog_content.return_value = ("### Features Added\n\n  - Updated feature\n", "1.0.0")
    changelog_main(package_path)

    with open(changelog_path, "r") as f:
        content = f.read()

    # Should replace the existing 0.0.0 section, not create a duplicate
    assert content.count("## 0.0.0 (UnReleased)") == 1
    assert "  - Updated feature" in content
    assert "  - Old feature" not in content
    assert "## 1.0.0 (2025-01-01)" in content


@patch("packaging_tools.sdk_changelog.get_changelog_content")
def test_normal_insert_when_top_version_is_released(mock_get_changelog_content, temp_package):
    """When the topmost version matches last_version (already released), insert a new section above."""
    package_path, changelog_path = temp_package

    # CHANGELOG has the already-released version at the top
    with open(changelog_path, "w") as f:
        f.write(
            "# Release History\n"
            "\n"
            "## 1.0.0 (2025-01-01)\n"
            "\n"
            "### Other Changes\n"
            "\n"
            "  - Initial version\n"
        )

    # last_version matches the top entry, so a new section should be inserted
    mock_get_changelog_content.return_value = ("### Features Added\n\n  - New feature\n", "1.0.0")
    changelog_main(package_path)

    with open(changelog_path, "r") as f:
        content = f.read()

    # Should have both the new unreleased section and the old released section
    assert "## 0.0.0 (UnReleased)" in content
    assert "  - New feature" in content
    assert "## 1.0.0 (2025-01-01)" in content
    assert "  - Initial version" in content


def test_invalid_changelog_no_log_for_non_arm_sdk(monkeypatch, temp_package):
    package_path, _ = temp_package
    log_level = None
    called = False

    def mock_get_changelog_content(*args, **kwargs):
        return ("", None)

    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level, called
        called = True
        log_level = enable_log_error

    monkeypatch.setattr("packaging_tools.sdk_changelog.get_changelog_content", mock_get_changelog_content)
    monkeypatch.setattr("packaging_tools.sdk_changelog.log_failed_message", mock_log_failed_message)
    changelog_main(package_path)

    assert not called
    assert log_level is None, "Expected no error log for invalid changelog content in data-plane SDK"
