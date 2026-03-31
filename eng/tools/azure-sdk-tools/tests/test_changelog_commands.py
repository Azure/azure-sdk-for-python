"""Tests for the ``azpysdk changelog`` command group."""

import argparse
from unittest.mock import patch, MagicMock

import pytest

from azpysdk.changelog import changelog


# ---------------------------------------------------------------------------
# Helper – build a minimal parser that includes the changelog subcommands
# ---------------------------------------------------------------------------

def _build_parser():
    parser = argparse.ArgumentParser(prog="azpysdk")
    subparsers = parser.add_subparsers(title="commands", dest="command")
    changelog().register(subparsers)
    return parser


# ---------------------------------------------------------------------------
# Parser / registration tests
# ---------------------------------------------------------------------------


class TestChangelogRegistration:
    """Verify that the changelog command is registered correctly."""

    def test_changelog_subcommand_exists(self):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "verify"])
        assert args.command == "changelog"
        assert args.changelog_command == "verify"

    def test_changelog_add_without_package(self):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add"])
        assert args.changelog_command == "add"
        assert args.package is None

    def test_changelog_add_with_package(self):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add", "sdk/storage/azure-storage-blob"])
        assert args.changelog_command == "add"
        assert args.package == "sdk/storage/azure-storage-blob"

    def test_changelog_create(self):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "create"])
        assert args.changelog_command == "create"

    def test_changelog_status(self):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "status"])
        assert args.changelog_command == "status"

    def test_changelog_no_subcommand_prints_help(self):
        """When no subcommand is given, the handler should print help and return 1."""
        parser = _build_parser()
        args = parser.parse_args(["changelog"])
        assert hasattr(args, "func")
        # func should be the _no_subcommand method
        result = args.func(args)
        assert result == 1


# ---------------------------------------------------------------------------
# Execution tests (npx / chronus invocation)
# ---------------------------------------------------------------------------


class TestChangelogExecution:
    """Verify that each subcommand invokes chronus with the right arguments."""

    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_add_calls_chronus_add(self, mock_which, mock_call):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add"])
        result = args.func(args)
        assert result == 0
        mock_call.assert_called_once()
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "chronus", "add"]

    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_add_with_package_passes_package(self, mock_which, mock_call):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add", "sdk/core/azure-core"])
        result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "chronus", "add", "sdk/core/azure-core"]

    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_verify_calls_chronus_verify(self, mock_which, mock_call):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "verify"])
        result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "chronus", "verify"]

    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_create_calls_chronus_changelog(self, mock_which, mock_call):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "create"])
        result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "chronus", "changelog"]

    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_status_calls_chronus_status(self, mock_which, mock_call):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "status"])
        result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "chronus", "status"]

    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_chronus_runs_from_repo_root(self, mock_which, mock_call):
        """Chronus must run from the repository root directory."""
        parser = _build_parser()
        args = parser.parse_args(["changelog", "verify"])
        args.func(args)
        _, kwargs = mock_call.call_args
        from azpysdk.changelog import REPO_ROOT
        assert kwargs["cwd"] == REPO_ROOT

    @patch("azpysdk.changelog.subprocess.call", return_value=1)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_nonzero_exit_code_propagated(self, mock_which, mock_call):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "verify"])
        result = args.func(args)
        assert result == 1


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------


class TestChangelogErrors:
    """Verify error handling when prerequisites are missing."""

    @patch("azpysdk.changelog.shutil.which", return_value=None)
    def test_npx_not_found_raises(self, mock_which):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "verify"])
        with pytest.raises(FileNotFoundError, match="npx not found"):
            args.func(args)
