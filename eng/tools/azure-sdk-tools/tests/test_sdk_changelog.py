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
    
    def mock_get_changelog_content(*args, **kwargs):
        return ("", None)
    
    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level
        log_level = enable_log_error
    
    monkeypatch.setattr("packaging_tools.sdk_changelog.get_changelog_content", mock_get_changelog_content)
    monkeypatch.setattr("packaging_tools.sdk_changelog.log_failed_message", mock_log_failed_message)
    changelog_main(package_path)
    
    assert log_level is True, "Expected error log to be enabled for invalid changelog content in ARM SDK if not in pipeline"

def test_valid_changelog_no_log_for_arm_sdk(monkeypatch, temp_arm_package):
    package_path, _ = temp_arm_package
    log_level = None
    
    def mock_get_changelog_content(*args, **kwargs):
        return ("### Features Added", None)
    
    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level
        log_level = enable_log_error
    
    monkeypatch.setattr("packaging_tools.sdk_changelog.get_changelog_content", mock_get_changelog_content)
    monkeypatch.setattr("packaging_tools.sdk_changelog.log_failed_message", mock_log_failed_message)
    changelog_main(package_path)
    
    assert log_level is None, "Expected no error log for valid changelog content in ARM SDK"

def test_changelog_warning_log_for_arm_sdk(monkeypatch, temp_arm_package):
    package_path, _ = temp_arm_package
    log_level = None
    
    def mock_get_changelog_content(*args, **kwargs):
        return ("", "1.0.0")
    
    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level
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
    assert package_result.get("version") == "1.0.0"
    
    assert log_level is False, "Expected warning log to be enabled for invalid changelog content in ARM SDK if in pipeline"

def test_invalid_changelog_no_log_for_non_arm_sdk(monkeypatch, temp_package):
    package_path, _ = temp_package
    log_level = None
    
    def mock_get_changelog_content(*args, **kwargs):
        return ("", None)
    
    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level
        log_level = enable_log_error
    
    monkeypatch.setattr("packaging_tools.sdk_changelog.get_changelog_content", mock_get_changelog_content)
    monkeypatch.setattr("packaging_tools.sdk_changelog.log_failed_message", mock_log_failed_message)
    changelog_main(package_path)
    
    assert log_level is None, "Expected no error log for invalid changelog content in data-plane SDK"