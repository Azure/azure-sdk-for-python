import pytest
import tempfile
import shutil
import time
from pathlib import Path

from packaging_tools.sdk_update_version import main as update_version_main


@pytest.fixture
def temp_package():
    temp_dir = tempfile.mkdtemp()
    package_path = Path(temp_dir)

    yield package_path

    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_arm_package():
    temp_dir = tempfile.mkdtemp()
    package_path = Path(temp_dir) / "azure-mgmt-test"
    package_path.mkdir(parents=True, exist_ok=True)

    yield package_path

    shutil.rmtree(temp_dir)


def test_preview_to_stable_version_update(temp_package):
    package_path = temp_package

    # seed version file
    version_file = package_path / "_version.py"
    version_file.write_text('VERSION = "1.0.0b2"\n')

    # seed changelog
    changelog = package_path / "CHANGELOG.md"
    changelog.write_text("## 1.0.0b2 (Unreleased)\n\n### Features\n\n- Something\n")

    package_result = {
        "version": "1.0.0b2",
        "tagIsStable": True,
        "changelog": {"content": "### Features"},
    }

    update_version_main(package_path, package_result=package_result)

    # version file updated to stable
    assert 'VERSION = "1.0.0"' in version_file.read_text()

    # changelog first line updated
    first_line = changelog.read_text().splitlines()[0]
    assert first_line.startswith("## 1.0.0 (")


def test_initial_version_generated(temp_package):
    pkg = temp_package
    (pkg / "_version.py").write_text('VERSION = "0.0.0"\n')
    (pkg / "CHANGELOG.md").write_text("## 0.0.0 (Unreleased)\n\n### Features\n")
    package_result = {"version": "", "tagIsStable": False, "changelog": {"content": "### Features"}}
    update_version_main(pkg, package_result=package_result)
    assert 'VERSION = "1.0.0b1"' in (pkg / "_version.py").read_text()
    assert (pkg / "CHANGELOG.md").read_text().splitlines()[0].startswith("## 1.0.0b1 (")


def test_bugfix_increments_patch_beta(temp_package):
    pkg = temp_package
    (pkg / "_version.py").write_text('VERSION = "1.0.0"\n')
    (pkg / "CHANGELOG.md").write_text("## 1.0.0 (Unreleased)\n\n### Bugs Fixed\n- Fix\n")
    package_result = {"version": "1.0.0", "tagIsStable": False, "changelog": {"content": "### Bugs Fixed"}}
    update_version_main(pkg, package_result=package_result)
    assert 'VERSION = "1.0.1b1"' in (pkg / "_version.py").read_text()
    assert (pkg / "CHANGELOG.md").read_text().splitlines()[0].startswith("## 1.0.1b1 (")


def test_preview_increments_beta_counter(temp_package):
    pkg = temp_package
    (pkg / "_version.py").write_text('VERSION = "1.2.0b3"\n')
    (pkg / "CHANGELOG.md").write_text("## 1.2.0b3 (Unreleased)\n\n### Features\n")
    package_result = {"version": "1.2.0b3", "tagIsStable": False, "changelog": {"content": "### Features"}}
    update_version_main(pkg, package_result=package_result)
    assert 'VERSION = "1.2.0b4"' in (pkg / "_version.py").read_text()
    assert (pkg / "CHANGELOG.md").read_text().splitlines()[0].startswith("## 1.2.0b4 (")


def test_breaking_change_increments_major_beta(temp_package):
    pkg = temp_package
    (pkg / "_version.py").write_text('VERSION = "1.4.2"\n')
    (pkg / "CHANGELOG.md").write_text("## 1.4.2 (Unreleased)\n\n### Breaking Changes\n- Remove X\n")
    package_result = {"version": "1.4.2", "tagIsStable": False, "changelog": {"content": "### Breaking Changes"}}
    update_version_main(pkg, package_result=package_result)
    assert 'VERSION = "2.0.0b1"' in (pkg / "_version.py").read_text()
    assert (pkg / "CHANGELOG.md").read_text().splitlines()[0].startswith("## 2.0.0b1 (")


def test_feature_change_increments_minor_beta(temp_package):
    pkg = temp_package
    (pkg / "_version.py").write_text('VERSION = "1.4.2"\n')
    (pkg / "CHANGELOG.md").write_text("## 1.4.2 (Unreleased)\n\n### Features\n- Add Y\n")
    package_result = {"version": "1.4.2", "tagIsStable": False, "changelog": {"content": "### Features"}}
    update_version_main(pkg, package_result=package_result)
    assert 'VERSION = "1.5.0b1"' in (pkg / "_version.py").read_text()
    assert (pkg / "CHANGELOG.md").read_text().splitlines()[0].startswith("## 1.5.0b1 (")


def test_initial_version_generated_without_package_result(temp_package):
    # Ensure code path works when package_result is None (falsy)
    pkg = temp_package
    (pkg / "_version.py").write_text('VERSION = "0.0.0"\n')
    (pkg / "CHANGELOG.md").write_text("## 0.0.0 (Unreleased)\n\n### Features\n")
    # Call without a package_result dict to exercise else branch logic
    update_version_main(pkg)  # type: ignore[arg-type]
    # Should compute first preview version
    assert 'VERSION = "1.0.0b1"' in (pkg / "_version.py").read_text()
    assert (pkg / "CHANGELOG.md").read_text().splitlines()[0].startswith("## 1.0.0b1 (")


def test_explicit_version_and_release_date_used(temp_package):
    pkg = temp_package
    (pkg / "_version.py").write_text('VERSION = "0.0.0"\n')
    (pkg / "CHANGELOG.md").write_text("## 0.0.0 (Unreleased)\n\n### Features\n")
    desired_version = "2.3.4b5"
    desired_date = "2025-02-15"
    update_version_main(pkg, version=desired_version, release_date=desired_date, release_type="beta")
    assert f'VERSION = "{desired_version}"' in (pkg / "_version.py").read_text()
    first_line = (pkg / "CHANGELOG.md").read_text().splitlines()[0]
    assert first_line == f"## {desired_version} ({desired_date})"  # exact match


def test_invalid_version_format_fallbacks_to_calculated(temp_package):
    pkg = temp_package
    (pkg / "_version.py").write_text('VERSION = "0.0.0"\n')
    (pkg / "CHANGELOG.md").write_text("## 0.0.0 (Unreleased)\n\n### Features\n")
    # Provide invalid version string; should be ignored and computed as 1.0.0b1
    update_version_main(pkg, version="v1.0.0", release_type="beta")
    assert 'VERSION = "1.0.0b1"' in (pkg / "_version.py").read_text()
    first_line = (pkg / "CHANGELOG.md").read_text().splitlines()[0]
    assert first_line.startswith("## 1.0.0b1 (")


def test_invalid_release_type_defaults_to_beta_flow(temp_package):
    pkg = temp_package
    (pkg / "_version.py").write_text('VERSION = "0.0.0"\n')
    (pkg / "CHANGELOG.md").write_text("## 0.0.0 (Unreleased)\n\n### Features\n")
    # release_type invalid; treated as beta; initial version should be computed preview
    update_version_main(pkg, release_type="foo")
    assert 'VERSION = "1.0.0b1"' in (pkg / "_version.py").read_text()
    lines = (pkg / "CHANGELOG.md").read_text()
    assert lines.splitlines()[0].startswith("## 1.0.0b1 (")
    # Unreleased should be replaced with date
    assert "## 0.0.0 (Unreleased)" not in "".join(lines)


def test_invalid_release_date_uses_current_date(temp_package):
    pkg = temp_package
    (pkg / "_version.py").write_text('VERSION = "0.0.0"\n')
    (pkg / "CHANGELOG.md").write_text("## 0.0.0 (Unreleased)\n\n### Features\n")
    today = time.strftime("%Y-%m-%d", time.localtime())
    # Provide invalid release_date; should fall back to today's date
    update_version_main(pkg, release_date="13-2025-11")
    first_line = (pkg / "CHANGELOG.md").read_text().splitlines()[0]
    assert first_line.startswith("## 1.0.0b1 ("), "Expected computed version line"
    assert today in first_line, f"Expected fallback date {today} in changelog line"


def test_invalid_changelog_warning_log_for_arm_sdk(monkeypatch, temp_arm_package):
    package_path = temp_arm_package
    log_level = None

    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level
        log_level = enable_log_error

    package_result = {
        "changelog": {
            "content": "",
        }
    }

    monkeypatch.setattr("packaging_tools.sdk_update_version.log_failed_message", mock_log_failed_message)
    update_version_main(package_path, package_result=package_result)

    assert (
        log_level is False
    ), "Expected warning log to be enabled for invalid changelog content in ARM SDK if in pipeline"


def test_invalid_changelog_error_log_for_arm_sdk(monkeypatch, temp_arm_package):
    package_path = temp_arm_package
    log_level = None

    def mock_get_changelog_content(*args, **kwargs):
        return ("", "")

    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level
        log_level = enable_log_error

    monkeypatch.setattr("packaging_tools.sdk_update_version.get_changelog_content", mock_get_changelog_content)
    monkeypatch.setattr("packaging_tools.sdk_update_version.log_failed_message", mock_log_failed_message)
    update_version_main(package_path)

    assert (
        log_level is True
    ), "Expected error log to be enabled for invalid changelog content in ARM SDK if not in pipeline"


def test_valid_changelog_no_log_for_arm_sdk(monkeypatch, temp_arm_package):
    package_path = temp_arm_package
    log_level = None

    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level
        log_level = enable_log_error

    package_result = {
        "changelog": {
            "content": "### Features Added\n- New feature",
        }
    }

    monkeypatch.setattr("packaging_tools.sdk_update_version.log_failed_message", mock_log_failed_message)
    update_version_main(package_path, package_result=package_result)

    assert log_level is None, "Expected no error log for valid changelog content in ARM SDK"


def test_invalid_changelog_no_log_for_non_arm_sdk(monkeypatch, temp_package):
    package_path = temp_package
    log_level = None

    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level
        log_level = enable_log_error

    package_result = {
        "changelog": {
            "content": "### Features Added\n- New feature",
        }
    }

    monkeypatch.setattr("packaging_tools.sdk_update_version.log_failed_message", mock_log_failed_message)
    update_version_main(package_path, package_result=package_result)

    assert log_level is None, "Expected no error log for valid changelog content in non-ARM SDK"


def test_invalid_changelog_no_log_for_arm_sdk_with_version(monkeypatch, temp_arm_package):
    package_path = temp_arm_package
    log_level = None

    def mock_get_changelog_content(*args, **kwargs):
        return ("", "")

    def mock_log_failed_message(message: str, enable_log_error: bool):
        nonlocal log_level
        log_level = enable_log_error

    monkeypatch.setattr("packaging_tools.sdk_update_version.get_changelog_content", mock_get_changelog_content)
    monkeypatch.setattr("packaging_tools.sdk_update_version.log_failed_message", mock_log_failed_message)
    update_version_main(package_path, version="1.0.0")

    assert (
        log_level is None
    ), "Expected no error log for invalid changelog content in ARM SDK when version is explicitly provided"
