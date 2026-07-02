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

    # Trigger at 2048, but cut down toward an explicit 1024 target.
    trimmed = trim_changelog_if_needed(package_path, size_limit=2048, trim_target=1024)

    assert trimmed is True
    content = changelog_path.read_text(encoding="utf-8")

    # min-keep forces keeping the newest entries even past the 1024 target, but never past the
    # hard 2048 limit. Each entry is ~450 bytes, so 4 entries exceed the limit and it settles on 3.
    assert len(content.encode("utf-8")) <= 2048
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
    # Cut to under half the limit (the default target), not merely under the limit. Here the
    # target keeps more than the 4-entry minimum, so min-keep does not raise the size.
    assert len(content.encode("utf-8")) <= 4096 // 2


def test_trim_changelog_keeps_min_entries_past_target(temp_arm_package):
    # Even when the target would keep fewer, at least CHANGELOG_MIN_KEEP_ENTRIES (4) newest entries
    # are retained -- as long as they still fit under the hard size_limit.
    package_path, changelog_path = temp_arm_package
    # Each entry is large enough that only 1 fits under the 4096 target, but 4 fit under 16 KB.
    with open(changelog_path, "w") as f:
        f.write(_make_changelog(10, body_per_version="  - " + "x" * 3000 + "\n"))

    trimmed = trim_changelog_if_needed(package_path, size_limit=16 * 1024, trim_target=4096)

    assert trimmed is True
    content = changelog_path.read_text(encoding="utf-8")
    kept = _version_headers(content)
    # min-keep wins over the small target: exactly the 4 newest entries are kept.
    assert kept == ["10.0.0", "9.0.0", "8.0.0", "7.0.0"]
    assert len(content.encode("utf-8")) <= 16 * 1024


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


def _assert_real_changelog_trim(tmp_path, package_name, newest, oldest, kept_count):
    # Real-world fixtures (~210 KB) trigger trimming (over the 128 KB limit). Trimming aims for the
    # 64 KB target but always keeps at least CHANGELOG_MIN_KEEP_ENTRIES (4) newest entries for
    # usefulness -- unless keeping 4 would exceed the 128 KB hard limit, in which case only as many
    # as fit are kept. The expected trimmed output is checked in for easy review.
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
    # Stays under the 128 KB hard limit. Measure normalized (LF) bytes so the check matches the
    # pipeline (Linux) regardless of the local platform's newline translation.
    assert len(content.encode("utf-8")) <= 128 * 1024

    pkg = package_path.name
    kept = _version_headers(content)
    # The newest entries are kept; the oldest history is removed completely.
    assert len(kept) == kept_count
    assert kept[0] == newest
    assert kept[-1] == oldest
    assert (
        f"> Changelog entries prior to {oldest} were removed to reduce file size. "
        f"See https://pypi.org/project/{pkg}/{oldest}/ for the older history." in content
    )


def test_trim_changelog_azure_mgmt_sql_fixture(tmp_path):
    # The 4.0.0 stable entry alone is ~95 KB, so keeping the 4-entry minimum (~138 KB) would exceed
    # the 128 KB limit; the hard-limit cap reduces it to the 3 newest entries (~127 KB).
    _assert_real_changelog_trim(tmp_path, "azure-mgmt-sql-4.0.0", newest="4.0.0", oldest="4.0.0b24", kept_count=3)


def test_trim_changelog_azure_mgmt_network_fixture(tmp_path):
    # min-keep=4 keeps the 4 newest entries (~121 KB), still under the 128 KB limit.
    _assert_real_changelog_trim(tmp_path, "azure-mgmt-network-31.0.0", newest="31.0.0", oldest="30.1.0", kept_count=4)


def test_trim_changelog_azure_mgmt_datafactory_fixture(tmp_path):
    # min-keep=4 keeps the 4 newest entries (~90 KB), well under the 128 KB limit.
    _assert_real_changelog_trim(
        tmp_path, "azure-mgmt-datafactory-10.0.0b1", newest="10.0.0b1", oldest="9.1.0", kept_count=4
    )


def test_trim_changelog_azure_mgmt_containerservice_fixture(tmp_path):
    # Many small entries: the 64 KB target keeps the 15 newest entries (~60 KB), well above the
    # 4-entry floor and under the 128 KB limit.
    _assert_real_changelog_trim(
        tmp_path, "azure-mgmt-containerservice-41.4.0b1", newest="41.4.0b1", oldest="39.1.0", kept_count=15
    )


def test_trim_changelog_azure_mgmt_cosmosdb_fixture(tmp_path):
    # Many small entries: the 64 KB target keeps the 18 newest entries (~63 KB), well above the
    # 4-entry floor and under the 128 KB limit.
    _assert_real_changelog_trim(
        tmp_path, "azure-mgmt-cosmosdb-10.0.0b6", newest="10.0.0b6", oldest="9.1.0b1", kept_count=18
    )
