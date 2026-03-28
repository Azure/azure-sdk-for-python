"""
Unit tests for red_team._utils.file_utils module.
"""

import json
import logging
import os
import tempfile

import pytest
from unittest.mock import MagicMock, patch

from azure.ai.evaluation.red_team._utils.file_utils import (
    FileManager,
    create_file_manager,
)


@pytest.fixture(scope="function")
def tmp_dir():
    """Provide a temporary directory cleaned up after each test."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture(scope="function")
def fm(tmp_dir):
    """Create a FileManager rooted in the temporary directory."""
    return FileManager(base_output_dir=tmp_dir)


@pytest.fixture(scope="function")
def fm_with_logger(tmp_dir):
    """Create a FileManager with a mock logger."""
    logger = MagicMock(spec=logging.Logger)
    return FileManager(base_output_dir=tmp_dir, logger=logger), logger


@pytest.mark.unittest
class TestFileManagerInit:
    """Test FileManager initialisation."""

    def test_default_base_output_dir(self):
        """Base output dir defaults to '.' when not supplied."""
        fm = FileManager()
        assert fm.base_output_dir == "."
        assert fm.logger is None

    def test_custom_base_output_dir(self, tmp_dir):
        """Custom base output dir is stored."""
        fm = FileManager(base_output_dir=tmp_dir)
        assert fm.base_output_dir == tmp_dir

    def test_logger_is_stored(self):
        """Logger is stored on the instance."""
        logger = MagicMock()
        fm = FileManager(logger=logger)
        assert fm.logger is logger


@pytest.mark.unittest
class TestEnsureDirectory:
    """Test ensure_directory method."""

    def test_creates_new_directory(self, fm, tmp_dir):
        """Directories that do not exist are created."""
        target = os.path.join(tmp_dir, "a", "b", "c")
        result = fm.ensure_directory(target)

        assert os.path.isdir(result)
        assert os.path.isabs(result)

    def test_existing_directory_is_no_op(self, fm, tmp_dir):
        """Existing directories are handled without error."""
        result = fm.ensure_directory(tmp_dir)
        assert os.path.isdir(result)

    def test_returns_absolute_path(self, fm):
        """Return value is always an absolute path."""
        result = fm.ensure_directory(".")
        assert os.path.isabs(result)


@pytest.mark.unittest
class TestGenerateUniqueFilename:
    """Test generate_unique_filename method."""

    def test_basic_unique_filename(self, fm):
        """Filename contains a UUID and is non-empty."""
        name = fm.generate_unique_filename()
        assert len(name) > 0

    def test_with_prefix(self, fm):
        """Prefix appears at the start of the filename."""
        name = fm.generate_unique_filename(prefix="scan")
        assert name.startswith("scan_")

    def test_with_suffix(self, fm):
        """Suffix appears at the end of the filename (before extension)."""
        name = fm.generate_unique_filename(suffix="final")
        assert name.endswith("final")

    def test_with_prefix_and_suffix(self, fm):
        """Both prefix and suffix are included."""
        name = fm.generate_unique_filename(prefix="pre", suffix="suf")
        assert name.startswith("pre_")
        assert name.endswith("suf")

    def test_with_extension_no_dot(self, fm):
        """Extension supplied without a dot gets a dot prepended."""
        name = fm.generate_unique_filename(extension="json")
        assert name.endswith(".json")

    def test_with_extension_with_dot(self, fm):
        """Extension supplied with a dot is used as-is."""
        name = fm.generate_unique_filename(extension=".jsonl")
        assert name.endswith(".jsonl")
        assert ".." not in name

    def test_with_timestamp(self, fm):
        """Timestamp is embedded when use_timestamp=True."""
        name = fm.generate_unique_filename(use_timestamp=True)
        # Timestamp pattern: YYYYMMDD_HHMMSS — at least 15 chars
        parts = name.split("_")
        assert len(parts) >= 2

    def test_uniqueness(self, fm):
        """Two successive calls produce different filenames."""
        a = fm.generate_unique_filename()
        b = fm.generate_unique_filename()
        assert a != b


@pytest.mark.unittest
class TestGetScanOutputPath:
    """Test get_scan_output_path method."""

    def test_non_debug_creates_hidden_dir(self, fm, tmp_dir):
        """Outside DEBUG mode the scan directory is dot-prefixed."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DEBUG", None)
            path = fm.get_scan_output_path("scan123")

        expected_dir = os.path.join(tmp_dir, ".scan123")
        assert os.path.normcase(path) == os.path.normcase(expected_dir)
        assert os.path.isdir(path)

    def test_non_debug_creates_gitignore(self, fm, tmp_dir):
        """.gitignore is written inside the scan dir when not in debug mode."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DEBUG", None)
            path = fm.get_scan_output_path("scan_gi")

        gitignore = os.path.join(path, ".gitignore")
        assert os.path.isfile(gitignore)
        with open(gitignore, "r", encoding="utf-8") as f:
            assert f.read() == "*\n"

    def test_debug_creates_non_hidden_dir(self, fm, tmp_dir):
        """In DEBUG mode the scan directory has no dot prefix."""
        with patch.dict(os.environ, {"DEBUG": "true"}):
            path = fm.get_scan_output_path("scan456")

        expected_dir = os.path.join(tmp_dir, "scan456")
        assert os.path.normcase(path) == os.path.normcase(expected_dir)
        assert os.path.isdir(path)

    @pytest.mark.parametrize("debug_val", ["true", "1", "yes", "y", "TRUE", "Yes"])
    def test_debug_env_values(self, fm, tmp_dir, debug_val):
        """All truthy DEBUG values produce the non-hidden directory."""
        with patch.dict(os.environ, {"DEBUG": debug_val}):
            path = fm.get_scan_output_path("scanD")

        expected_dir = os.path.join(tmp_dir, "scanD")
        assert os.path.normcase(path) == os.path.normcase(expected_dir)

    def test_debug_no_gitignore(self, fm, tmp_dir):
        """In DEBUG mode no .gitignore is created."""
        with patch.dict(os.environ, {"DEBUG": "1"}):
            path = fm.get_scan_output_path("scan_nogi")

        gitignore = os.path.join(path, ".gitignore")
        assert not os.path.exists(gitignore)

    def test_with_filename(self, fm, tmp_dir):
        """When filename is provided the return value includes it."""
        with patch.dict(os.environ, {"DEBUG": "true"}):
            path = fm.get_scan_output_path("scan789", filename="results.json")

        assert path.endswith("results.json")
        assert os.path.isdir(os.path.dirname(path))

    def test_without_filename(self, fm, tmp_dir):
        """When filename is empty the return value is the directory itself."""
        with patch.dict(os.environ, {"DEBUG": "true"}):
            path = fm.get_scan_output_path("scandir")

        assert os.path.isdir(path)

    def test_gitignore_not_overwritten(self, fm, tmp_dir):
        """Existing .gitignore is not overwritten on second call."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DEBUG", None)
            fm.get_scan_output_path("scanonce")

            # Overwrite .gitignore manually
            gi_path = os.path.join(tmp_dir, ".scanonce", ".gitignore")
            with open(gi_path, "w", encoding="utf-8") as f:
                f.write("custom\n")

            fm.get_scan_output_path("scanonce")

        with open(gi_path, "r", encoding="utf-8") as f:
            assert f.read() == "custom\n"


@pytest.mark.unittest
class TestJsonIO:
    """Test write_json and read_json methods."""

    def test_write_read_roundtrip(self, fm, tmp_dir):
        """Data survives a write/read roundtrip."""
        data = {"key": "value", "nested": {"a": [1, 2, 3]}}
        filepath = os.path.join(tmp_dir, "test.json")

        written_path = fm.write_json(data, filepath)
        assert os.path.isfile(written_path)

        result = fm.read_json(written_path)
        assert result == data

    def test_write_json_returns_absolute_path(self, fm, tmp_dir):
        """write_json returns an absolute path."""
        filepath = os.path.join(tmp_dir, "abs.json")
        result = fm.write_json({}, filepath)
        assert os.path.isabs(result)

    def test_write_json_creates_parent_dirs(self, fm, tmp_dir):
        """write_json with ensure_dir=True creates parent directories."""
        filepath = os.path.join(tmp_dir, "deep", "nested", "file.json")
        fm.write_json({"ok": True}, filepath, ensure_dir=True)
        assert os.path.isfile(filepath)

    def test_write_json_ensure_dir_false(self, fm, tmp_dir):
        """write_json with ensure_dir=False does not create parent dirs."""
        filepath = os.path.join(tmp_dir, "missing_parent", "file.json")
        with pytest.raises(FileNotFoundError):
            fm.write_json({"ok": True}, filepath, ensure_dir=False)

    def test_write_json_custom_indent(self, fm, tmp_dir):
        """Custom indent is reflected in the written file."""
        filepath = os.path.join(tmp_dir, "indent.json")
        fm.write_json({"a": 1}, filepath, indent=4)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        assert "    " in content  # 4-space indent

    def test_write_json_logger_debug(self, fm_with_logger, tmp_dir):
        """Logger.debug is called on successful write."""
        fm, logger = fm_with_logger
        filepath = os.path.join(tmp_dir, "log.json")
        fm.write_json({"x": 1}, filepath)
        logger.debug.assert_called_once()

    def test_read_json_missing_file(self, fm, tmp_dir):
        """read_json raises on missing file."""
        with pytest.raises(FileNotFoundError):
            fm.read_json(os.path.join(tmp_dir, "no_such.json"))

    def test_read_json_invalid_json(self, fm, tmp_dir):
        """read_json raises on malformed JSON."""
        filepath = os.path.join(tmp_dir, "bad.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("{not valid json")
        with pytest.raises(json.JSONDecodeError):
            fm.read_json(filepath)

    def test_read_json_logger_debug(self, fm_with_logger, tmp_dir):
        """Logger.debug is called on successful read."""
        fm, logger = fm_with_logger
        filepath = os.path.join(tmp_dir, "ok.json")
        fm.write_json({"k": "v"}, filepath)
        logger.reset_mock()
        fm.read_json(filepath)
        logger.debug.assert_called_once()

    def test_read_json_logger_error_on_failure(self, fm_with_logger, tmp_dir):
        """Logger.error is called when read fails."""
        fm, logger = fm_with_logger
        with pytest.raises(Exception):
            fm.read_json(os.path.join(tmp_dir, "missing.json"))
        logger.error.assert_called_once()

    def test_write_read_unicode(self, fm, tmp_dir):
        """Unicode data roundtrips correctly."""
        data = {"greeting": "こんにちは", "emoji": "🔥"}
        filepath = os.path.join(tmp_dir, "unicode.json")
        fm.write_json(data, filepath)
        result = fm.read_json(filepath)
        assert result == data


@pytest.mark.unittest
class TestJsonlIO:
    """Test write_jsonl and read_jsonl methods."""

    def test_write_read_roundtrip(self, fm, tmp_dir):
        """JSONL data survives a write/read roundtrip."""
        data = [{"a": 1}, {"b": 2}, {"c": 3}]
        filepath = os.path.join(tmp_dir, "test.jsonl")

        written_path = fm.write_jsonl(data, filepath)
        assert os.path.isfile(written_path)

        result = fm.read_jsonl(written_path)
        assert result == data

    def test_write_jsonl_returns_absolute_path(self, fm, tmp_dir):
        """write_jsonl returns an absolute path."""
        filepath = os.path.join(tmp_dir, "abs.jsonl")
        result = fm.write_jsonl([], filepath)
        assert os.path.isabs(result)

    def test_write_jsonl_creates_parent_dirs(self, fm, tmp_dir):
        """write_jsonl with ensure_dir=True creates parent directories."""
        filepath = os.path.join(tmp_dir, "sub", "dir", "file.jsonl")
        fm.write_jsonl([{"ok": True}], filepath, ensure_dir=True)
        assert os.path.isfile(filepath)

    def test_write_jsonl_ensure_dir_false(self, fm, tmp_dir):
        """write_jsonl with ensure_dir=False does not create parent dirs."""
        filepath = os.path.join(tmp_dir, "no_parent", "file.jsonl")
        with pytest.raises(FileNotFoundError):
            fm.write_jsonl([{"ok": True}], filepath, ensure_dir=False)

    def test_read_jsonl_skips_blank_lines(self, fm, tmp_dir):
        """Blank lines in JSONL are silently skipped."""
        filepath = os.path.join(tmp_dir, "blanks.jsonl")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write('{"a":1}\n\n\n{"b":2}\n')

        result = fm.read_jsonl(filepath)
        assert result == [{"a": 1}, {"b": 2}]

    def test_read_jsonl_skips_invalid_lines_with_logger(self, fm_with_logger, tmp_dir):
        """Invalid JSON lines are skipped and logged when logger is present."""
        fm, logger = fm_with_logger
        filepath = os.path.join(tmp_dir, "mixed.jsonl")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write('{"good":1}\n')
            f.write("not json\n")
            f.write('{"also_good":2}\n')

        result = fm.read_jsonl(filepath)
        assert result == [{"good": 1}, {"also_good": 2}]
        logger.warning.assert_called_once()

    def test_read_jsonl_skips_invalid_lines_without_logger(self, fm, tmp_dir):
        """Invalid JSON lines are silently skipped when no logger is set."""
        filepath = os.path.join(tmp_dir, "nolog.jsonl")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("bad\n")
            f.write('{"ok":1}\n')

        result = fm.read_jsonl(filepath)
        assert result == [{"ok": 1}]

    def test_read_jsonl_missing_file(self, fm):
        """read_jsonl raises on missing file."""
        with pytest.raises(FileNotFoundError):
            fm.read_jsonl("nonexistent.jsonl")

    def test_read_jsonl_logger_debug(self, fm_with_logger, tmp_dir):
        """Logger.debug is called on successful read."""
        fm, logger = fm_with_logger
        filepath = os.path.join(tmp_dir, "ok.jsonl")
        fm.write_jsonl([{"x": 1}], filepath)
        logger.reset_mock()
        fm.read_jsonl(filepath)
        logger.debug.assert_called_once()

    def test_read_jsonl_logger_error_on_failure(self, fm_with_logger, tmp_dir):
        """Logger.error is called on file-level read failure."""
        fm, logger = fm_with_logger
        with pytest.raises(Exception):
            fm.read_jsonl(os.path.join(tmp_dir, "missing.jsonl"))
        logger.error.assert_called_once()

    def test_write_jsonl_logger_debug(self, fm_with_logger, tmp_dir):
        """Logger.debug is called on successful write."""
        fm, logger = fm_with_logger
        filepath = os.path.join(tmp_dir, "wlog.jsonl")
        fm.write_jsonl([{"a": 1}], filepath)
        logger.debug.assert_called_once()

    def test_empty_roundtrip(self, fm, tmp_dir):
        """Empty list roundtrips correctly."""
        filepath = os.path.join(tmp_dir, "empty.jsonl")
        fm.write_jsonl([], filepath)
        result = fm.read_jsonl(filepath)
        assert result == []

    def test_unicode_roundtrip(self, fm, tmp_dir):
        """Unicode content survives JSONL roundtrip."""
        data = [{"text": "café ☕"}, {"text": "日本語テスト"}]
        filepath = os.path.join(tmp_dir, "uni.jsonl")
        fm.write_jsonl(data, filepath)
        result = fm.read_jsonl(filepath)
        assert result == data


@pytest.mark.unittest
class TestSafeFilename:
    """Test safe_filename method."""

    def test_passthrough_safe_name(self, fm):
        """Already safe names are returned unchanged."""
        assert fm.safe_filename("hello_world") == "hello_world"

    def test_replaces_invalid_chars(self, fm):
        """Invalid filesystem characters are replaced with underscores."""
        assert fm.safe_filename('a<b>c:d"e/f\\g|h?i*j') == "a_b_c_d_e_f_g_h_i_j"

    def test_replaces_spaces(self, fm):
        """Spaces are replaced with underscores."""
        assert fm.safe_filename("my file name") == "my_file_name"

    def test_truncation(self, fm):
        """Names longer than max_length are truncated with '...'."""
        long_name = "a" * 300
        result = fm.safe_filename(long_name, max_length=20)
        assert len(result) <= 20
        assert result.endswith("...")

    def test_no_truncation_within_limit(self, fm):
        """Names within max_length are not truncated."""
        name = "short"
        assert fm.safe_filename(name, max_length=255) == "short"

    def test_exact_max_length(self, fm):
        """Name exactly at max_length is not truncated."""
        name = "a" * 255
        assert fm.safe_filename(name) == name

    def test_empty_string(self, fm):
        """Empty string is returned as-is."""
        assert fm.safe_filename("") == ""


@pytest.mark.unittest
class TestGetFileSize:
    """Test get_file_size method."""

    def test_returns_correct_size(self, fm, tmp_dir):
        """Reported size matches the bytes written."""
        filepath = os.path.join(tmp_dir, "sized.txt")
        content = "hello"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        size = fm.get_file_size(filepath)
        assert size == os.path.getsize(filepath)
        assert size > 0

    def test_missing_file_raises(self, fm, tmp_dir):
        """get_file_size raises for a non-existent file."""
        with pytest.raises(OSError):
            fm.get_file_size(os.path.join(tmp_dir, "nope.txt"))


@pytest.mark.unittest
class TestFileExists:
    """Test file_exists method."""

    def test_existing_file(self, fm, tmp_dir):
        """Returns True for an existing file."""
        filepath = os.path.join(tmp_dir, "exists.txt")
        with open(filepath, "w") as f:
            f.write("data")
        assert fm.file_exists(filepath) is True

    def test_non_existing_file(self, fm, tmp_dir):
        """Returns False for a non-existing file."""
        assert fm.file_exists(os.path.join(tmp_dir, "nope.txt")) is False

    def test_directory_returns_false(self, fm, tmp_dir):
        """Returns False for a directory (os.path.isfile semantics)."""
        assert fm.file_exists(tmp_dir) is False


@pytest.mark.unittest
class TestCleanupFile:
    """Test cleanup_file method."""

    def test_deletes_existing_file(self, fm, tmp_dir):
        """Existing file is removed and True is returned."""
        filepath = os.path.join(tmp_dir, "to_delete.txt")
        with open(filepath, "w") as f:
            f.write("bye")

        result = fm.cleanup_file(filepath)
        assert result is True
        assert not os.path.exists(filepath)

    def test_nonexistent_file_returns_true(self, fm, tmp_dir):
        """Non-existing file returns True (nothing to delete)."""
        result = fm.cleanup_file(os.path.join(tmp_dir, "missing.txt"))
        assert result is True

    def test_ignore_errors_true_returns_false(self, fm, tmp_dir):
        """When deletion fails and ignore_errors=True, returns False."""
        filepath = os.path.join(tmp_dir, "fail.txt")
        with open(filepath, "w") as f:
            f.write("x")

        with patch("os.remove", side_effect=PermissionError("denied")):
            result = fm.cleanup_file(filepath, ignore_errors=True)

        assert result is False

    def test_ignore_errors_false_raises(self, fm, tmp_dir):
        """When deletion fails and ignore_errors=False, the exception propagates."""
        filepath = os.path.join(tmp_dir, "fail2.txt")
        with open(filepath, "w") as f:
            f.write("x")

        with patch("os.remove", side_effect=PermissionError("denied")):
            with pytest.raises(PermissionError):
                fm.cleanup_file(filepath, ignore_errors=False)

    def test_cleanup_logger_debug(self, fm_with_logger, tmp_dir):
        """Logger.debug is called when file is deleted."""
        fm, logger = fm_with_logger
        filepath = os.path.join(tmp_dir, "logged.txt")
        with open(filepath, "w") as f:
            f.write("log me")

        fm.cleanup_file(filepath)
        logger.debug.assert_called_once()

    def test_cleanup_logger_warning_on_error(self, fm_with_logger, tmp_dir):
        """Logger.warning is called when deletion fails with ignore_errors=True."""
        fm, logger = fm_with_logger
        filepath = os.path.join(tmp_dir, "warn.txt")
        with open(filepath, "w") as f:
            f.write("x")

        with patch("os.remove", side_effect=PermissionError("denied")):
            fm.cleanup_file(filepath, ignore_errors=True)

        logger.warning.assert_called_once()


@pytest.mark.unittest
class TestCreateFileManager:
    """Test create_file_manager factory function."""

    def test_returns_file_manager(self):
        """Factory returns a FileManager instance."""
        fm = create_file_manager()
        assert isinstance(fm, FileManager)

    def test_passes_base_output_dir(self, tmp_dir):
        """base_output_dir is forwarded to the FileManager."""
        fm = create_file_manager(base_output_dir=tmp_dir)
        assert fm.base_output_dir == tmp_dir

    def test_passes_logger(self):
        """Logger is forwarded to the FileManager."""
        logger = MagicMock()
        fm = create_file_manager(logger=logger)
        assert fm.logger is logger

    def test_defaults(self):
        """Defaults match FileManager defaults."""
        fm = create_file_manager()
        assert fm.base_output_dir == "."
        assert fm.logger is None
