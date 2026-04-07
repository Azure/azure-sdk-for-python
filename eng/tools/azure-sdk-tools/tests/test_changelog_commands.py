"""Tests for the ``azpysdk changelog`` command group."""

import argparse
import os
import sys
from unittest.mock import patch, MagicMock, call

import pytest

from azpysdk.changelog import changelog, REPO_ROOT, _CHRONUS_MODULE_PATH


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
    """Verify that each subcommand invokes chronus with the right arguments.

    All tests in this class patch ``_is_chronus_installed`` to return True
    so the installation check is bypassed.
    """

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_add_calls_chronus_add(self, mock_which, mock_call, _mock_installed):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add"])
        # Run from repo root so CWD detection does NOT inject a package
        with patch("os.getcwd", return_value=REPO_ROOT):
            result = args.func(args)
        assert result == 0
        mock_call.assert_called_once()
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "--no", "chronus", "add"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_add_with_package_passes_package(self, mock_which, mock_call, _mock_installed):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add", "sdk/core/azure-core"])
        result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "--no", "chronus", "add", "sdk/core/azure-core"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_add_detects_package_from_cwd(self, mock_which, mock_call, _mock_installed):
        """When CWD is inside a package dir and no package arg is given, detect it."""
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add"])
        pkg_dir = os.path.join(REPO_ROOT, "sdk", "storage", "azure-storage-blob")
        with patch("os.getcwd", return_value=pkg_dir):
            result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "--no", "chronus", "add", "sdk/storage/azure-storage-blob"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_add_detects_package_from_subdirectory(self, mock_which, mock_call, _mock_installed):
        """When CWD is a subdirectory of a package, detect the package root."""
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add"])
        sub_dir = os.path.join(REPO_ROOT, "sdk", "storage", "azure-storage-blob", "azure", "storage", "blob")
        with patch("os.getcwd", return_value=sub_dir):
            result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "--no", "chronus", "add", "sdk/storage/azure-storage-blob"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_add_explicit_package_overrides_cwd(self, mock_which, mock_call, _mock_installed):
        """An explicit package argument takes precedence over CWD detection."""
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add", "sdk/core/azure-core"])
        pkg_dir = os.path.join(REPO_ROOT, "sdk", "storage", "azure-storage-blob")
        with patch("os.getcwd", return_value=pkg_dir):
            result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "--no", "chronus", "add", "sdk/core/azure-core"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_verify_calls_chronus_verify(self, mock_which, mock_call, _mock_installed):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "verify"])
        result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "--no", "chronus", "verify"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_create_calls_chronus_changelog(self, mock_which, mock_call, _mock_installed):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "create"])
        result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "--no", "chronus", "changelog"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_status_calls_chronus_status(self, mock_which, mock_call, _mock_installed):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "status"])
        result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npx", "--no", "chronus", "status"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_chronus_runs_from_repo_root(self, mock_which, mock_call, _mock_installed):
        """Chronus must run from the repository root directory."""
        parser = _build_parser()
        args = parser.parse_args(["changelog", "verify"])
        args.func(args)
        _, kwargs = mock_call.call_args
        assert kwargs["cwd"] == REPO_ROOT

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=1)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npx")
    def test_nonzero_exit_code_propagated(self, mock_which, mock_call, _mock_installed):
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

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.shutil.which", return_value=None)
    def test_npx_not_found_raises(self, mock_which, _mock_installed):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "verify"])
        with pytest.raises(FileNotFoundError, match="npx not found"):
            args.func(args)


# ---------------------------------------------------------------------------
# Chronus installation check tests
# ---------------------------------------------------------------------------


class TestEnsureChronusInstalled:
    """Verify the _ensure_chronus_installed safety gate."""

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    def test_already_installed_returns_immediately(self, mock_installed):
        """When Chronus is already installed, no action is needed."""
        c = changelog()
        c._ensure_chronus_installed()  # should not raise

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=False)
    @patch("azpysdk.changelog.shutil.which", return_value=None)
    def test_npm_not_found_exits(self, mock_which, mock_installed):
        """When npm is not on PATH, exit with an error."""
        c = changelog()
        with pytest.raises(SystemExit):
            c._ensure_chronus_installed()

    @patch("azpysdk.changelog.changelog._is_chronus_installed", side_effect=[False, True])
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npm")
    @patch("azpysdk.changelog.sys.stdin")
    def test_non_interactive_installs_automatically(self, mock_stdin, mock_which, mock_call, mock_installed):
        """In non-interactive mode, npm install runs without prompting."""
        mock_stdin.isatty.return_value = False
        c = changelog()
        c._ensure_chronus_installed()  # should not raise
        mock_call.assert_called_once()
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npm", "install"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", side_effect=[False, True])
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npm")
    @patch("builtins.input", return_value="y")
    @patch("azpysdk.changelog.sys.stdin")
    def test_interactive_user_accepts_install(self, mock_stdin, mock_input, mock_which, mock_call, mock_installed):
        """When the user says 'y', npm install is executed."""
        mock_stdin.isatty.return_value = True
        c = changelog()
        c._ensure_chronus_installed()  # should not raise
        mock_call.assert_called_once()

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=False)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npm")
    @patch("builtins.input", return_value="n")
    @patch("azpysdk.changelog.sys.stdin")
    def test_interactive_user_declines_exits(self, mock_stdin, mock_input, mock_which, mock_installed):
        """When the user says 'n', exit without installing."""
        mock_stdin.isatty.return_value = True
        c = changelog()
        with pytest.raises(SystemExit):
            c._ensure_chronus_installed()

    @patch("azpysdk.changelog.changelog._is_chronus_installed", side_effect=[False, False])
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npm")
    @patch("azpysdk.changelog.sys.stdin")
    def test_install_succeeds_but_chronus_still_missing(self, mock_stdin, mock_which, mock_call, mock_installed):
        """If npm install succeeds but chronus isn't found, exit with error."""
        mock_stdin.isatty.return_value = False
        c = changelog()
        with pytest.raises(SystemExit):
            c._ensure_chronus_installed()

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=False)
    @patch("azpysdk.changelog.subprocess.call", return_value=1)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npm")
    @patch("azpysdk.changelog.sys.stdin")
    def test_npm_install_failure_exits(self, mock_stdin, mock_which, mock_call, mock_installed):
        """If npm install fails, exit with the npm exit code."""
        mock_stdin.isatty.return_value = False
        c = changelog()
        with pytest.raises(SystemExit):
            c._ensure_chronus_installed()

    def test_is_chronus_installed_checks_node_modules(self):
        """_is_chronus_installed should check for the chronus directory in node_modules."""
        c = changelog()
        expected_path = os.path.join(REPO_ROOT, _CHRONUS_MODULE_PATH)
        with patch("os.path.isdir", return_value=True) as mock_isdir:
            assert c._is_chronus_installed() is True
            mock_isdir.assert_called_once_with(expected_path)
        with patch("os.path.isdir", return_value=False) as mock_isdir:
            assert c._is_chronus_installed() is False
