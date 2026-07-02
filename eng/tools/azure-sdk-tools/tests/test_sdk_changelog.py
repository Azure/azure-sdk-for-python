import pytest
from unittest.mock import patch
from pathlib import Path
import json
import tempfile
import shutil

from packaging_tools.sdk_changelog import main as changelog_main
from packaging_tools.sdk_changelog import trim_changelog_if_needed


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


@patch("packaging_tools.sdk_changelog.get_changelog_content")
def test_timeout_forwarded_to_get_changelog_content(mock_get_changelog_content, temp_package):
    package_path, _ = temp_package
    mock_get_changelog_content.return_value = ("### Features Added\n\n- New feature", "1.0.0")

    changelog_main(package_path, timeout=60)

    mock_get_changelog_content.assert_called_once()
    _, kwargs = mock_get_changelog_content.call_args
    assert kwargs["timeout"] == 60


@patch("packaging_tools.sdk_changelog.get_changelog_content")
def test_timeout_default_is_900(mock_get_changelog_content, temp_package):
    package_path, _ = temp_package
    mock_get_changelog_content.return_value = ("### Features Added\n\n- New feature", "1.0.0")

    changelog_main(package_path)

    mock_get_changelog_content.assert_called_once()
    _, kwargs = mock_get_changelog_content.call_args
    assert kwargs["timeout"] == 900


@patch("packaging_tools.sdk_changelog.get_changelog_content")
def test_output_json_detector_mode_breaking(mock_get_changelog_content, temp_arm_package):
    package_path, changelog_path = temp_arm_package
    md_output = "### Features Added\n\n  - foo\n\n### Breaking Changes\n\n  - dropped bar\n"
    mock_get_changelog_content.return_value = (md_output, "1.2.3")
    output_json = package_path / "changes.json"

    changelog_main(package_path, output_json=output_json)

    # JSON output is written with the expected shape
    assert output_json.exists()
    with open(output_json, "r", encoding="utf-8") as f:
        result = json.load(f)
    assert result["changes"] == md_output
    assert result["hasBreakingChange"] is True
    assert "breakingChangeItems" not in result

    # CHANGELOG.md must NOT be modified in detector mode
    with open(changelog_path, "r") as f:
        assert f.read() == "# Release History\n\n"


@patch("packaging_tools.sdk_changelog.get_changelog_content")
def test_output_json_detector_mode_no_breaking(mock_get_changelog_content, temp_arm_package):
    package_path, changelog_path = temp_arm_package
    md_output = "### Features Added\n\n  - only feature\n"
    mock_get_changelog_content.return_value = (md_output, "1.0.0")
    output_json = package_path / "nested" / "changes.json"

    changelog_main(package_path, output_json=output_json)

    # Nested output directory is created and JSON written
    assert output_json.exists()
    with open(output_json, "r", encoding="utf-8") as f:
        result = json.load(f)
    assert result["changes"] == md_output
    assert result["hasBreakingChange"] is False
    assert "breakingChangeItems" not in result

    # CHANGELOG.md must NOT be modified in detector mode
    with open(changelog_path, "r") as f:
        assert f.read() == "# Release History\n\n"


def _make_changelog(num_versions: int, body_per_version: str = "  - some change\n") -> str:
    lines = ["# Release History\n", "\n"]
    # Newest version first (highest number), matching real CHANGELOG ordering.
    for v in range(num_versions, 0, -1):
        lines.append(f"## {v}.0.0 (2024-01-01)\n")
        lines.append("\n")
        lines.append("### Features Added\n")
        lines.append("\n")
        lines.append(body_per_version)
        lines.append("\n")
    return "".join(lines)


def _version_headers(content: str) -> list[str]:
    import re

    header_re = re.compile(r"^##\s+\S+")
    return [line.split()[1] for line in content.splitlines() if header_re.match(line)]


def test_trim_changelog_when_over_limit(temp_arm_package):
    package_path, changelog_path = temp_arm_package
    # 10 sizeable version entries so the file is well over the tiny limit.
    with open(changelog_path, "w") as f:
        f.write(_make_changelog(10, body_per_version="  - " + "x" * 400 + "\n"))

    # Trigger at 2048, but cut down to an explicit 1024 target.
    trimmed = trim_changelog_if_needed(package_path, size_limit=2048, trim_target=1024)

    assert trimmed is True
    content = changelog_path.read_text(encoding="utf-8")

    # File is cut down to under the target (which is below the trigger limit) and header kept.
    assert len(content.encode("utf-8")) <= 1024
    assert content.startswith("# Release History\n")

    kept = _version_headers(content)
    # Newest entry is always kept; the oldest ones are completely removed.
    assert "10.0.0" in kept
    assert "1.0.0" not in kept
    # The note references exactly the oldest kept version.
    oldest_kept = kept[-1]
    assert f"> Changelog entries prior to {oldest_kept} were removed" in content
    assert f"https://pypi.org/project/azure-mgmt-test/{oldest_kept}/" in content
    assert content.count("> Changelog entries prior to") == 1


def test_trim_changelog_target_defaults_to_half_limit(temp_arm_package):
    # When trim_target is not given it defaults to half of size_limit, leaving headroom below the
    # trigger limit so the file is not immediately re-trimmed on the next release.
    package_path, changelog_path = temp_arm_package
    with open(changelog_path, "w") as f:
        f.write(_make_changelog(20, body_per_version="  - " + "x" * 200 + "\n"))

    trimmed = trim_changelog_if_needed(package_path, size_limit=4096)

    assert trimmed is True
    content = changelog_path.read_text(encoding="utf-8")
    # Cut to under half the limit (the default target), not merely under the limit.
    assert len(content.encode("utf-8")) <= 4096 // 2


def test_trim_changelog_noop_when_under_limit(temp_arm_package):
    package_path, changelog_path = temp_arm_package
    original = _make_changelog(6)
    with open(changelog_path, "w") as f:
        f.write(original)

    trimmed = trim_changelog_if_needed(package_path, size_limit=1024 * 1024)

    assert trimmed is False
    with open(changelog_path, "r") as f:
        assert f.read() == original


def test_trim_changelog_skips_when_single_entry(temp_arm_package):
    # With only one version entry there is nothing to trim, even if it is over the limit.
    package_path, changelog_path = temp_arm_package
    original = _make_changelog(1, body_per_version="  - " + "x" * 2000 + "\n")
    with open(changelog_path, "w") as f:
        f.write(original)

    trimmed = trim_changelog_if_needed(package_path, size_limit=1024)

    assert trimmed is False
    with open(changelog_path, "r") as f:
        assert f.read() == original


def test_trim_changelog_idempotent(temp_arm_package):
    package_path, changelog_path = temp_arm_package
    with open(changelog_path, "w") as f:
        f.write(_make_changelog(10, body_per_version="  - " + "x" * 400 + "\n"))

    assert trim_changelog_if_needed(package_path, size_limit=2048) is True
    with open(changelog_path, "r") as f:
        first = f.read()

    # Second run: file is now under the limit, so nothing changes and the note is not duplicated.
    trim_changelog_if_needed(package_path, size_limit=2048)
    with open(changelog_path, "r") as f:
        second = f.read()

    assert first == second
    assert second.count("> Changelog entries prior to") == 1


def test_trim_changelog_preserves_note_when_single_entry(temp_arm_package):
    # A large file that already has a trim note but now has a single version entry and is still
    # over the limit must keep its note (regression for destructive no-op mutation).
    package_path, changelog_path = temp_arm_package
    changelog = _make_changelog(1, body_per_version="  - " + "x" * 2000 + "\n")
    note = (
        "> Changelog entries prior to 1.0.0 were removed to reduce file size. "
        "See https://pypi.org/project/azure-mgmt-test/1.0.0/ for the older history.\n"
    )
    original = changelog + "\n" + note
    with open(changelog_path, "w") as f:
        f.write(original)

    trimmed = trim_changelog_if_needed(package_path, size_limit=1024)

    assert trimmed is False
    with open(changelog_path, "r") as f:
        content = f.read()
    assert content == original
    assert note in content


def _assert_real_changelog_trim(tmp_path, package_name, newest, oldest):
    # Real-world fixtures (~210 KB) trigger trimming (over the 192 KB limit) and are cut down to
    # under the 96 KB target, keeping the newest entries that fit. The expected trimmed output is
    # checked in for easy review.
    data_dir = Path(__file__).parent / "data"
    fixture = data_dir / f"{package_name}-CHANGELOG.md"
    expected = (data_dir / f"{package_name}-CHANGELOG.trimmed.md").read_text(encoding="utf-8")

    package_path = tmp_path / package_name.rsplit("-", 1)[0]
    package_path.mkdir()
    shutil.copy(fixture, package_path / "CHANGELOG.md")

    trimmed = trim_changelog_if_needed(package_path)

    assert trimmed is True
    content = (package_path / "CHANGELOG.md").read_text(encoding="utf-8")

    # Trimmed output matches the checked-in expected fixture exactly.
    assert content == expected
    # Cut down to under the 96 KB target (which leaves headroom below the 192 KB limit). Measure
    # normalized (LF) bytes so the check matches the pipeline (Linux) regardless of the local
    # platform's newline translation.
    assert len(content.encode("utf-8")) <= 96 * 1024

    pkg = package_path.name
    kept = _version_headers(content)
    # Newest entries kept; the oldest history is removed completely.
    assert kept[0] == newest
    assert kept[-1] == oldest
    assert (
        f"> Changelog entries prior to {oldest} were removed to reduce file size. "
        f"See https://pypi.org/project/{pkg}/{oldest}/ for the older history." in content
    )


def test_trim_changelog_azure_mgmt_sql_fixture(tmp_path):
    # The 4.0.0 stable entry alone is ~95 KB (~half the limit), so trimming to the 96 KB target
    # keeps only that newest entry.
    _assert_real_changelog_trim(tmp_path, "azure-mgmt-sql-4.0.0", newest="4.0.0", oldest="4.0.0")


def test_trim_changelog_azure_mgmt_network_fixture(tmp_path):
    # The 31.0.0 entry (~71 KB) plus the next entry would exceed the 96 KB target, so only the
    # newest entry is kept.
    _assert_real_changelog_trim(tmp_path, "azure-mgmt-network-31.0.0", newest="31.0.0", oldest="31.0.0")
