import argparse
import os
import shutil
import subprocess
import sys
from typing import NoReturn, Optional, List

from .Check import Check, REPO_ROOT
from ci_tools.functions import get_package_from_repo
from ci_tools.logging import logger

# Chronus is pinned as a dev dependency in .github/chronus/package.json with
# a committed lockfile so both the top-level version and all transitive
# dependencies are reproducible.
_CHRONUS_INSTALL_DIR = os.path.join(".github", "chronus")
_CHRONUS_BIN_NAME = "chronus.cmd" if os.name == "nt" else "chronus"
_CHRONUS_BIN_PATH = os.path.join(_CHRONUS_INSTALL_DIR, "node_modules", ".bin", _CHRONUS_BIN_NAME)

_FALLBACK_CHANGE_KINDS = ["breaking changes", "features added", "deprecation", "fix", "dependencies", "internal"]


def _load_change_kinds() -> List[str]:
    """Read valid change kinds from ``.chronus/config.yaml``.

    Falls back to a hardcoded list if the config file is missing or
    cannot be parsed (e.g. pyyaml not installed).
    """
    config_path = os.path.join(REPO_ROOT, ".chronus", "config.yaml")
    try:
        import yaml

        with open(config_path) as f:
            config = yaml.safe_load(f)
        kinds = list(config.get("changeKinds", {}).keys())
        if kinds:
            return kinds
    except Exception:
        pass
    return list(_FALLBACK_CHANGE_KINDS)


_CHANGE_KINDS = _load_change_kinds()


def _add_package_argument(parser: argparse.ArgumentParser, action: str) -> None:
    """Add the common ``package`` positional argument to a subparser."""
    parser.add_argument(
        "package",
        nargs="?",
        default=None,
        help=(f"Package path (e.g. sdk/storage/azure-storage-blob) to {action}. "),
    )


class changelog(Check):
    """Manage changelogs with Chronus.

    Wraps Chronus CLI commands (add, verify, create, status) so they can be
    invoked through the ``azpysdk`` CLI.  Commands can be run from the
    repository root **or** from within a package directory — the tool will
    detect the package path automatically when possible.
    """

    def __init__(self) -> None:
        super().__init__()
        self._parser: Optional[argparse.ArgumentParser] = None

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        # parent_parsers intentionally unused — changelog commands operate at
        # the repository level via Chronus, not on individual packages.
        p = subparsers.add_parser(
            "changelog",
            help="Manage changelogs with Chronus (add, verify, create, status)",
        )
        self._parser = p
        sub = p.add_subparsers(title="changelog commands", dest="changelog_command")

        # changelog add
        add_p = sub.add_parser("add", help="Add a chronus change entry for modified packages")
        _add_package_argument(add_p, "add an entry for")
        add_p.add_argument(
            "--kind",
            "-k",
            choices=_CHANGE_KINDS,
            default=None,
            help="Kind of change (e.g. breaking changes, features added, fix). If omitted, chronus will prompt interactively.",
        )
        add_p.add_argument(
            "--message",
            "-m",
            default=None,
            help="Short description of the change. If omitted, chronus will prompt interactively.",
        )
        add_p.set_defaults(func=self._run_add)

        # changelog verify
        verify_p = sub.add_parser("verify", help="Verify all modified packages have change entries")
        verify_p.set_defaults(func=self._run_verify)

        # changelog create
        create_p = sub.add_parser("create", help="Generate CHANGELOG.md from pending chronus entries")
        _add_package_argument(create_p, "generate changelog for")
        create_p.set_defaults(func=self._run_create)

        # changelog status
        status_p = sub.add_parser("status", help="Show a summary of pending changes and resulting version bumps")
        _add_package_argument(status_p, "show status for")
        status_p.set_defaults(func=self._run_status)

        p.set_defaults(func=self._no_subcommand)

    # Internal helpers

    def _no_subcommand(self, args: argparse.Namespace) -> int:
        """Print help when no changelog subcommand is provided."""
        if self._parser:
            self._parser.print_help()
        return 1

    @staticmethod
    def _is_chronus_installed() -> bool:
        """Return ``True`` if Chronus is installed locally in *node_modules*."""
        return os.path.isfile(os.path.join(REPO_ROOT, _CHRONUS_BIN_PATH))

    def _ensure_chronus_installed(self) -> None:
        """Verify Chronus is installed locally, offering to install if not.

        Runs ``npm ci`` against ``.github/chronus`` so only the exact
        versions recorded in ``package-lock.json`` are installed.
        Raises ``SystemExit`` if the user declines or installation fails.
        """
        if self._is_chronus_installed():
            return

        install_dir = os.path.join(REPO_ROOT, _CHRONUS_INSTALL_DIR)

        npm = shutil.which("npm")
        if not npm:
            self._fail_no_npm(install_dir)

        self._prompt_or_autoinstall(install_dir)
        self._npm_ci(npm, install_dir)

    @staticmethod
    def _fail_no_npm(install_dir: str) -> NoReturn:
        logger.error(
            "Chronus is not installed and npm was not found on PATH.\n"
            "Please install Node.js (LTS) from https://nodejs.org/ then run:\n\n"
            f"    cd {install_dir}\n"
            "    npm ci\n"
        )
        raise SystemExit(1)

    @staticmethod
    def _prompt_or_autoinstall(install_dir: str) -> None:
        """Prompt for installation interactively, or check env var in CI."""
        if sys.stdin.isatty():
            print(
                f"\nChronus is not installed locally. It is pinned as a dev dependency\n"
                f"in {os.path.join(install_dir, 'package.json')}.\n"
            )
            answer = input(f"Run 'npm ci' in {_CHRONUS_INSTALL_DIR} to install it? [Y/n] ").strip().lower()
            if answer not in ("", "y", "yes"):
                logger.info("Skipped Chronus installation.")
                raise SystemExit(1)
        elif not os.environ.get("AZPYSDK_AUTO_INSTALL"):
            logger.error(
                "Chronus is not installed and running in non-interactive mode.\n"
                "Set AZPYSDK_AUTO_INSTALL=1 to allow automatic installation, or run:\n\n"
                f"    cd {install_dir}\n"
                "    npm ci\n"
            )
            raise SystemExit(1)
        else:
            logger.info("AZPYSDK_AUTO_INSTALL set — running 'npm ci' automatically.")

    def _npm_ci(self, npm: str, install_dir: str) -> None:
        """Run ``npm ci`` and verify Chronus was installed."""
        logger.info(f"Running: npm ci  (cwd: {install_dir})")
        rc = subprocess.call([npm, "ci"], cwd=install_dir)
        if rc != 0:
            logger.error("'npm ci' failed. Please resolve npm errors and try again.")
            raise SystemExit(rc)

        if not self._is_chronus_installed():
            logger.error(
                "'npm ci' succeeded but Chronus was not found in node_modules.\n"
                f"Expected: {os.path.join(REPO_ROOT, _CHRONUS_BIN_PATH)}\n"
                f"Please verify that {os.path.join(_CHRONUS_INSTALL_DIR, 'package.json')} "
                "lists @chronus/chronus as a dependency."
            )
            raise SystemExit(1)

    @staticmethod
    def _resolve_package(package_arg: Optional[str]) -> Optional[str]:
        """Resolve a package argument to a Chronus package name."""
        if not package_arg:
            return None
        # Resolve relative paths (e.g. ".") to absolute so get_package_from_repo
        # doesn't accidentally glob against the repo root.
        target = os.path.abspath(package_arg) if os.path.exists(package_arg) else package_arg
        try:
            parsed = get_package_from_repo(target, REPO_ROOT)
            return parsed.name if parsed else package_arg
        except RuntimeError:
            return package_arg  # passthrough for unresolvable names

    def _run_chronus(self, chronus_args: List[str]) -> int:
        """Run a chronus command from the repository root."""
        self._ensure_chronus_installed()
        cmd = [os.path.join(REPO_ROOT, _CHRONUS_BIN_PATH), *chronus_args]
        logger.info(f"Running: {' '.join(cmd)}")
        return subprocess.call(cmd, cwd=REPO_ROOT)

    # Subcommand handlers

    def _run_add(self, args: argparse.Namespace) -> int:
        """Run ``chronus add`` to interactively add a change entry."""
        chronus_args = ["add"]
        package = self._resolve_package(args.package)
        if package:
            chronus_args.append(package)
        if args.kind:
            chronus_args.extend(["--kind", args.kind])
        if args.message:
            chronus_args.extend(["--message", args.message])
        return self._run_chronus(chronus_args)

    def _run_verify(self, args: argparse.Namespace) -> int:
        """Run ``chronus verify`` to check for missing change entries."""
        return self._run_chronus(["verify"])

    def _run_create(self, args: argparse.Namespace) -> int:
        """Run ``chronus changelog`` to generate CHANGELOG.md files."""
        package = self._resolve_package(args.package)
        if not package:
            logger.error(
                "No package specified and could not detect one from the current directory.\n"
                "Either run from within a package directory (e.g. sdk/core/azure-core) or\n"
                "pass the package path explicitly:\n\n"
                "    azpysdk changelog create sdk/core/azure-core\n"
            )
            return 1

        rc = self._run_chronus(["changelog", "--package", package])
        if rc != 0:
            logger.info(
                "Hint: if Chronus reported 'No release action found', it means there are no\n"
                "pending change entries for this package. Run 'azpysdk changelog add' first to\n"
                "create a change entry, then re-run 'azpysdk changelog create'."
            )
        return rc

    def _run_status(self, args: argparse.Namespace) -> int:
        """Run ``chronus status`` to show pending changes."""
        chronus_args = ["status"]
        package = self._resolve_package(args.package)
        if package:
            chronus_args.extend(["--only", package])
        return self._run_chronus(chronus_args)
