"""Tests for the ``azpysdk changelog`` command group."""

import argparse
import os
from unittest.mock import patch, MagicMock

import pytest

from azpysdk.changelog import changelog, REPO_ROOT


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
        # Run from repo root so CWD detection does NOT inject a package
        with patch("os.getcwd", return_value=REPO_ROOT):
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
    def test_add_detects_package_from_cwd(self, mock_which, mock_call):
        """When CWD is inside a package dir and no package arg is given, detect it."""
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add"])
        pkg_dir = os.path.join(REPO_ROOT, "sdk", "storage", "azure-storage-blob")
        with patch("os.getcwd", return_value=pkg_dir):
            result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "chronus", "add", "sdk/storage/azure-storage-blob"]

    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_add_detects_package_from_subdirectory(self, mock_which, mock_call):
        """When CWD is a subdirectory of a package, detect the package root."""
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add"])
        sub_dir = os.path.join(REPO_ROOT, "sdk", "storage", "azure-storage-blob", "azure", "storage", "blob")
        with patch("os.getcwd", return_value=sub_dir):
            result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "chronus", "add", "sdk/storage/azure-storage-blob"]

    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_add_explicit_package_overrides_cwd(self, mock_which, mock_call):
        """An explicit package argument takes precedence over CWD detection."""
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add", "sdk/core/azure-core"])
        pkg_dir = os.path.join(REPO_ROOT, "sdk", "storage", "azure-storage-blob")
        with patch("os.getcwd", return_value=pkg_dir):
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
        assert kwargs["cwd"] == REPO_ROOT

    @patch("azpysdk.changelog.subprocess.call", return_value=1)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_nonzero_exit_code_propagated(self, mock_which, mock_call):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "verify"])
        result = args.func(args)
        assert result == 1


# ---------------------------------------------------------------------------
# CWD detection unit tests
# ---------------------------------------------------------------------------


class TestDetectPackageFromCwd:
    """Test the _detect_package_from_cwd helper directly."""

    def test_at_package_root(self):
        c = changelog()
        with patch("os.getcwd", return_value=os.path.join(REPO_ROOT, "sdk", "core", "azure-core")):
            assert c._detect_package_from_cwd() == "sdk/core/azure-core"

    def test_inside_package_subdir(self):
        c = changelog()
        with patch("os.getcwd", return_value=os.path.join(REPO_ROOT, "sdk", "core", "azure-core", "azure", "core")):
            assert c._detect_package_from_cwd() == "sdk/core/azure-core"

    def test_at_repo_root(self):
        c = changelog()
        with patch("os.getcwd", return_value=REPO_ROOT):
            assert c._detect_package_from_cwd() is None

    def test_at_sdk_dir(self):
        c = changelog()
        with patch("os.getcwd", return_value=os.path.join(REPO_ROOT, "sdk")):
            assert c._detect_package_from_cwd() is None

    def test_at_service_dir(self):
        c = changelog()
        with patch("os.getcwd", return_value=os.path.join(REPO_ROOT, "sdk", "storage")):
            assert c._detect_package_from_cwd() is None

    def test_outside_repo(self):
        c = changelog()
        with patch("os.getcwd", return_value="/tmp"):
            assert c._detect_package_from_cwd() is None


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
