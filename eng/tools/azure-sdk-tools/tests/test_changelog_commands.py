"""Tests for the ``azpysdk changelog`` command group."""

import argparse
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch, MagicMock, call

import pytest

from azpysdk.changelog import (
    changelog,
    REPO_ROOT,
    _CHRONUS_BIN_PATH,
    _CHANGE_KINDS,
    _FALLBACK_CHANGE_KINDS,
    _load_change_kinds,
)

# Absolute path of the pinned chronus binary — used as the first element of
# the invocation in all the execution tests below.
_CHRONUS_BIN = os.path.join(REPO_ROOT, _CHRONUS_BIN_PATH)


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

    def test_changelog_add_with_kind(self):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add", "--kind", "breaking"])
        assert args.kind == "breaking"

    def test_changelog_add_with_kind_short(self):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add", "-k", "feature"])
        assert args.kind == "feature"

    def test_changelog_add_with_message(self):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add", "--message", "Fixed the bug"])
        assert args.message == "Fixed the bug"

    def test_changelog_add_with_message_short(self):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add", "-m", "Added new API"])
        assert args.message == "Added new API"

    def test_changelog_add_with_kind_and_message(self):
        parser = _build_parser()
        args = parser.parse_args(
            ["changelog", "add", "sdk/core/azure-core", "--kind", "breaking", "-m", "Removed old API"]
        )
        assert args.package == "sdk/core/azure-core"
        assert args.kind == "breaking"
        assert args.message == "Removed old API"

    def test_changelog_add_invalid_kind_rejected(self):
        parser = _build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["changelog", "add", "--kind", "notakind"])

    def test_changelog_add_all_valid_kinds_accepted(self):
        parser = _build_parser()
        for kind in _CHANGE_KINDS:
            args = parser.parse_args(["changelog", "add", "--kind", kind])
            assert args.kind == kind

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
# _load_change_kinds tests
# ---------------------------------------------------------------------------


class TestLoadChangeKinds:
    """Verify that change kinds are loaded dynamically from config."""

    def test_loaded_kinds_match_config_file(self):
        """_CHANGE_KINDS should match the keys in .chronus/config.yaml."""
        import yaml

        config_path = os.path.join(REPO_ROOT, ".chronus", "config.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        expected = list(config["changeKinds"].keys())
        assert _CHANGE_KINDS == expected

    def test_fallback_when_config_missing(self):
        """When the config file doesn't exist, fall back to hardcoded list."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            kinds = _load_change_kinds()
        assert kinds == _FALLBACK_CHANGE_KINDS

    def test_fallback_when_yaml_parse_fails(self):
        """When YAML parsing fails, fall back to hardcoded list."""
        with patch("builtins.open", side_effect=Exception("bad yaml")):
            kinds = _load_change_kinds()
        assert kinds == _FALLBACK_CHANGE_KINDS


# ---------------------------------------------------------------------------
# Execution tests (chronus invocation)
# ---------------------------------------------------------------------------


class TestChangelogExecution:
    """Verify that each subcommand invokes chronus with the right arguments.

    All tests in this class patch ``_is_chronus_installed`` to return True
    so the installation check is bypassed.  Chronus is invoked via the
    pinned binary at ``.github/chronus/node_modules/.bin/chronus``.
    """

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    def test_add_calls_chronus_add(self, mock_call, _mock_installed):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add"])
        # Run from repo root so CWD detection does NOT inject a package
        with patch("os.getcwd", return_value=REPO_ROOT):
            result = args.func(args)
        assert result == 0
        mock_call.assert_called_once()
        cmd = mock_call.call_args[0][0]
        assert cmd == [_CHRONUS_BIN, "add"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    def test_add_with_package_passes_package(self, mock_call, _mock_installed):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add", "sdk/core/azure-core"])
        result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == [_CHRONUS_BIN, "add", "azure-core"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    def test_add_with_kind_passes_flag(self, mock_call, _mock_installed):
        """The --kind flag should be forwarded to chronus."""
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add", "--kind", "breaking"])
        with patch("os.getcwd", return_value=REPO_ROOT):
            result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == [_CHRONUS_BIN, "add", "--kind", "breaking"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    def test_add_with_message_passes_flag(self, mock_call, _mock_installed):
        """The --message flag should be forwarded to chronus."""
        parser = _build_parser()
        args = parser.parse_args(["changelog", "add", "-m", "Fixed upload bug"])
        with patch("os.getcwd", return_value=REPO_ROOT):
            result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == [_CHRONUS_BIN, "add", "--message", "Fixed upload bug"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    def test_add_with_kind_message_and_package(self, mock_call, _mock_installed):
        """All flags (package, --kind, --message) should be forwarded together."""
        parser = _build_parser()
        args = parser.parse_args(
            [
                "changelog",
                "add",
                "sdk/core/azure-core",
                "--kind",
                "breaking",
                "-m",
                "Removed deprecated API",
            ]
        )
        result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == [
            _CHRONUS_BIN,
            "add",
            "azure-core",
            "--kind",
            "breaking",
            "--message",
            "Removed deprecated API",
        ]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    def test_verify_calls_chronus_verify(self, mock_call, _mock_installed):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "verify"])
        result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == [_CHRONUS_BIN, "verify"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    def test_create_calls_chronus_changelog(self, mock_call, _mock_installed):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "create", "sdk/core/azure-core"])
        result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == [_CHRONUS_BIN, "changelog", "--package", "azure-core"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    def test_status_calls_chronus_status(self, mock_call, _mock_installed):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "status"])
        with patch("os.getcwd", return_value=REPO_ROOT):
            result = args.func(args)
        assert result == 0
        cmd = mock_call.call_args[0][0]
        assert cmd == [_CHRONUS_BIN, "status"]

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=0)
    def test_chronus_runs_from_repo_root(self, mock_call, _mock_installed):
        """Chronus must run from the repository root directory."""
        parser = _build_parser()
        args = parser.parse_args(["changelog", "verify"])
        args.func(args)
        _, kwargs = mock_call.call_args
        assert kwargs["cwd"] == REPO_ROOT

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=True)
    @patch("azpysdk.changelog.subprocess.call", return_value=1)
    def test_nonzero_exit_code_propagated(self, mock_call, _mock_installed):
        parser = _build_parser()
        args = parser.parse_args(["changelog", "verify"])
        result = args.func(args)
        assert result == 1


# ---------------------------------------------------------------------------
# Package resolution unit tests
# ---------------------------------------------------------------------------


class TestResolvePackage:
    """Test the _resolve_package helper that uses get_package_from_repo."""

    @patch("azpysdk.changelog.get_package_from_repo")
    def test_explicit_path_resolves_name(self, mock_get_pkg):
        mock_get_pkg.return_value = SimpleNamespace(name="azure-core")
        result = changelog._resolve_package("sdk/core/azure-core")
        assert result == "azure-core"
        mock_get_pkg.assert_called_once_with("sdk/core/azure-core", REPO_ROOT)

    @patch("azpysdk.changelog.get_package_from_repo")
    def test_bare_name_resolves(self, mock_get_pkg):
        mock_get_pkg.return_value = SimpleNamespace(name="azure-core")
        result = changelog._resolve_package("azure-core")
        assert result == "azure-core"
        mock_get_pkg.assert_called_once_with("azure-core", REPO_ROOT)

    @patch("azpysdk.changelog.get_package_from_repo", side_effect=RuntimeError("not found"))
    def test_bare_name_passthrough_when_not_found(self, mock_get_pkg):
        result = changelog._resolve_package("some-nonexistent-package-name")
        assert result == "some-nonexistent-package-name"

    def test_none_returns_none(self):
        assert changelog._resolve_package(None) is None


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
    def test_non_interactive_with_auto_install_env(self, mock_stdin, mock_which, mock_call, mock_installed):
        """In non-interactive mode with AZPYSDK_AUTO_INSTALL=1, npm ci runs."""
        mock_stdin.isatty.return_value = False
        c = changelog()
        with patch.dict(os.environ, {"AZPYSDK_AUTO_INSTALL": "1"}):
            c._ensure_chronus_installed()  # should not raise
        mock_call.assert_called_once()
        cmd = mock_call.call_args[0][0]
        assert cmd == ["/usr/bin/npm", "ci"]
        # And it must run from the .github/chronus directory, not repo root.
        _, kwargs = mock_call.call_args
        assert kwargs["cwd"].endswith(os.path.join(".github", "chronus"))

    @patch("azpysdk.changelog.changelog._is_chronus_installed", return_value=False)
    @patch("azpysdk.changelog.shutil.which", return_value="/usr/bin/npm")
    @patch("azpysdk.changelog.sys.stdin")
    def test_non_interactive_without_env_exits(self, mock_stdin, mock_which, mock_installed):
        """In non-interactive mode without AZPYSDK_AUTO_INSTALL, exit with error."""
        mock_stdin.isatty.return_value = False
        c = changelog()
        with patch.dict(os.environ, {}, clear=False):
            # Ensure AZPYSDK_AUTO_INSTALL is not set
            os.environ.pop("AZPYSDK_AUTO_INSTALL", None)
            with pytest.raises(SystemExit):
                c._ensure_chronus_installed()

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
        with patch.dict(os.environ, {"AZPYSDK_AUTO_INSTALL": "1"}):
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
        with patch.dict(os.environ, {"AZPYSDK_AUTO_INSTALL": "1"}):
            with pytest.raises(SystemExit):
                c._ensure_chronus_installed()

    def test_is_chronus_installed_checks_bin(self):
        """_is_chronus_installed should check for the chronus binary file."""
        c = changelog()
        expected_path = os.path.join(REPO_ROOT, _CHRONUS_BIN_PATH)
        with patch("os.path.isfile", return_value=True) as mock_isfile:
            assert c._is_chronus_installed() is True
            mock_isfile.assert_called_once_with(expected_path)
        with patch("os.path.isfile", return_value=False) as mock_isfile:
            assert c._is_chronus_installed() is False
