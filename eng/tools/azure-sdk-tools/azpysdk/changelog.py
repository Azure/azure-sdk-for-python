import argparse
import os
import shutil
import subprocess
import sys
from typing import Optional, List

from .Check import Check, REPO_ROOT
from ci_tools.functions import discover_targeted_packages
from ci_tools.logging import logger
from ci_tools.parsing import ParsedSetup

# The expected Chronus package name and on-disk install location.
# Chronus is pinned as a dev dependency in .github/chronus/package.json with
# a committed lockfile so both the top-level version and all transitive
# dependencies are reproducible.
_CHRONUS_PACKAGE = "@chronus/chronus"
_CHRONUS_INSTALL_DIR = os.path.join(".github", "chronus")
_CHRONUS_BIN_NAME = "chronus.cmd" if os.name == "nt" else "chronus"
_CHRONUS_BIN_PATH = os.path.join(_CHRONUS_INSTALL_DIR, "node_modules", ".bin", _CHRONUS_BIN_NAME)

_FALLBACK_CHANGE_KINDS = ["breaking", "feature", "deprecation", "fix", "dependencies", "internal"]


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
        """Register the ``changelog`` command group.

        The *parent_parsers* (common args like ``target``, ``--isolate``) are
        intentionally **not** used here because changelog commands operate at
        the repository level via Chronus, not on individual packages.
        """
        p = subparsers.add_parser(
            "changelog",
            help="Manage changelogs with Chronus (add, verify, create, status)",
        )
        self._parser = p

        changelog_sub = p.add_subparsers(title="changelog commands", dest="changelog_command")

        # changelog add
        add_p = changelog_sub.add_parser("add", help="Add a chronus change entry for modified packages")
        add_p.add_argument(
            "package",
            nargs="?",
            default=None,
            help=(
                "Package path (e.g. sdk/storage/azure-storage-blob) to add an entry for. "
                "If omitted and CWD is inside a package directory, the package is detected "
                "automatically. Otherwise chronus detects modified packages interactively."
            ),
        )
        add_p.add_argument(
            "--kind",
            "-k",
            choices=_CHANGE_KINDS,
            default=None,
            help=("Kind of change (e.g. breaking, feature, fix). " "If omitted, chronus will prompt interactively."),
        )
        add_p.add_argument(
            "--message",
            "-m",
            default=None,
            help=("Short description of the change. " "If omitted, chronus will prompt interactively."),
        )
        add_p.set_defaults(func=self._run_add)

        # changelog verify
        verify_p = changelog_sub.add_parser("verify", help="Verify all modified packages have change entries")
        verify_p.set_defaults(func=self._run_verify)

        # changelog create
        create_p = changelog_sub.add_parser("create", help="Generate CHANGELOG.md from pending chronus entries")
        create_p.add_argument(
            "package",
            nargs="?",
            default=None,
            help=(
                "Package path (e.g. sdk/storage/azure-storage-blob) to generate changelog for. "
                "If omitted and CWD is inside a package directory, the package is detected "
                "automatically. Otherwise chronus generates changelogs for all packages."
            ),
        )
        create_p.set_defaults(func=self._run_create)

        # changelog status
        status_p = changelog_sub.add_parser(
            "status", help="Show a summary of pending changes and resulting version bumps"
        )
        status_p.add_argument(
            "package",
            nargs="?",
            default=None,
            help=(
                "Package path (e.g. sdk/storage/azure-storage-blob) to show status for. "
                "If omitted and CWD is inside a package directory, the package is detected "
                "automatically. Otherwise chronus shows status for all packages."
            ),
        )
        status_p.set_defaults(func=self._run_status)

        # Default behaviour when no subcommand is given
        p.set_defaults(func=self._no_subcommand)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _no_subcommand(self, args: argparse.Namespace) -> int:
        """Print help when no changelog subcommand is provided."""
        if self._parser is not None:
            self._parser.print_help()
        return 1

    def _is_chronus_installed(self) -> bool:
        """Return ``True`` if Chronus is installed locally in *node_modules*."""
        return os.path.isfile(os.path.join(REPO_ROOT, _CHRONUS_BIN_PATH))

    def _ensure_chronus_installed(self) -> None:
        """Verify that Chronus is installed locally, offering to install if not.

        Security: we **never** allow ``npx`` to silently download packages
        from the npm registry.  Instead we check for a local installation
        and, when missing, run ``npm ci`` against ``.github/chronus`` so
        only the exact versions recorded in ``package-lock.json`` are
        installed (with integrity-hash verification).

        Raises ``SystemExit`` if the user declines or installation fails.
        """
        if self._is_chronus_installed():
            return

        install_dir = os.path.join(REPO_ROOT, _CHRONUS_INSTALL_DIR)
        npm = shutil.which("npm")
        if not npm:
            logger.error(
                "Chronus is not installed and npm was not found on PATH.\n"
                "Please install Node.js (LTS) from https://nodejs.org/ then run:\n\n"
                f"    cd {install_dir}\n"
                "    npm ci\n"
            )
            raise SystemExit(1)

        if sys.stdin.isatty():
            print(
                "\nChronus is not installed locally. It is pinned as a dev dependency\n"
                f"in {os.path.join(install_dir, 'package.json')}.\n"
            )
            answer = input(f"Run 'npm ci' in {_CHRONUS_INSTALL_DIR} to install it? [Y/n] ").strip().lower()
            if answer not in ("", "y", "yes"):
                logger.info("Skipped Chronus installation.")
                raise SystemExit(1)
        else:
            if not os.environ.get("AZPYSDK_AUTO_INSTALL"):
                logger.error(
                    "Chronus is not installed and running in non-interactive mode.\n"
                    "Set AZPYSDK_AUTO_INSTALL=1 to allow automatic installation, or run:\n\n"
                    f"    cd {install_dir}\n"
                    "    npm ci\n"
                )
                raise SystemExit(1)
            logger.info("AZPYSDK_AUTO_INSTALL set — running 'npm ci' automatically.")

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

    def _find_package_root_from_cwd(self) -> Optional[str]:
        """Find the package root directory when CWD is at or below ``sdk/<service>/<package>``.

        Walks up from the current directory to locate the package root,
        unlike ``get_targeted_directories(target=".")`` which only works
        when CWD is exactly the package root.  This lets developers run
        changelog commands from subdirectories such as
        ``sdk/core/azure-core/tests/``.

        Returns the absolute path to the package root, or ``None`` if CWD
        is not inside an ``sdk/<service>/<package>`` tree.
        """
        try:
            cwd = os.path.abspath(os.getcwd())
            repo = os.path.abspath(REPO_ROOT)
            rel = os.path.relpath(cwd, repo)
        except ValueError:
            # On Windows, relpath raises ValueError when paths are on different drives
            return None

        parts = rel.replace("\\", "/").split("/")
        if len(parts) >= 3 and parts[0] == "sdk":
            return os.path.join(repo, parts[0], parts[1], parts[2])
        return None

    def _resolve_package(self, package_arg: Optional[str]) -> Optional[str]:
        """Resolve a package argument or CWD to a Chronus package name.

        Uses ``discover_targeted_packages`` — the same discovery function
        that powers ``get_targeted_directories`` — to locate packages by
        path or bare name.  When *package_arg* is ``None``, the method
        detects the package from CWD by walking up to the nearest
        ``sdk/<service>/<package>`` directory.
        """
        if package_arg:
            found = discover_targeted_packages(package_arg, REPO_ROOT)
            if found:
                try:
                    return ParsedSetup.from_path(found[0]).name
                except Exception:
                    return os.path.basename(found[0])
            # Not found by discovery — pass through as-is
            return package_arg

        # No explicit package — detect from CWD
        pkg_root = self._find_package_root_from_cwd()
        if pkg_root is None:
            return None
        try:
            return ParsedSetup.from_path(pkg_root).name
        except Exception:
            return os.path.basename(os.path.normpath(pkg_root))

    def _run_chronus(self, chronus_args: List[str]) -> int:
        """Run a chronus command from the repository root.

        Before execution the method verifies that Chronus is installed in
        ``.github/chronus/node_modules`` and invokes the pinned binary
        directly (rather than via ``npx``) to avoid any registry lookup or
        ambient resolution.  stdin/stdout/stderr are inherited so that
        interactive prompts (e.g. ``chronus add``) work transparently.
        """
        self._ensure_chronus_installed()
        chronus_bin = os.path.join(REPO_ROOT, _CHRONUS_BIN_PATH)
        cmd = [chronus_bin] + chronus_args
        logger.info(f"Running: {' '.join(cmd)}")
        return subprocess.call(cmd, cwd=REPO_ROOT)

    # ------------------------------------------------------------------
    # Subcommand handlers
    # ------------------------------------------------------------------

    def _run_add(self, args: argparse.Namespace) -> int:
        """Run ``chronus add`` to interactively add a change entry.

        When no *package* argument is given but CWD is inside a package
        directory (``sdk/<service>/<package>``), the package path is detected
        automatically so the developer doesn't have to specify it.

        Optional ``--kind`` and ``--message`` flags are forwarded to chronus
        so the developer can skip the interactive prompts (e.g.
        ``azpysdk changelog add --kind breaking -m "Removed foo API"``).
        """
        chronus_args = ["add"]
        detected_from_cwd = not args.package
        package = self._resolve_package(args.package)
        if package and detected_from_cwd:
            logger.info(f"Detected package from current directory: {package}")
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
        """Run ``chronus changelog`` to generate CHANGELOG.md files.

        When no *package* argument is given but CWD is inside a package
        directory, the package path is detected automatically and passed
        via ``--package`` so only that package's changelog is generated.
        """
        chronus_args = ["changelog"]
        detected_from_cwd = not args.package
        package = self._resolve_package(args.package)
        if package and detected_from_cwd:
            logger.info(f"Detected package from current directory: {package}")
        if not package:
            logger.error(
                "No package specified and could not detect one from the current directory.\n"
                "Either run from within a package directory (e.g. sdk/core/azure-core) or\n"
                "pass the package path explicitly:\n\n"
                "    azpysdk changelog create sdk/core/azure-core\n"
            )
            return 1
        chronus_args.extend(["--package", package])
        rc = self._run_chronus(chronus_args)
        if rc != 0:
            logger.info(
                "Hint: if Chronus reported 'No release action found', it means there are no\n"
                "pending change entries for this package. Run 'azpysdk changelog add' first to\n"
                "create a change entry, then re-run 'azpysdk changelog create'."
            )
        return rc

    def _run_status(self, args: argparse.Namespace) -> int:
        """Run ``chronus status`` to show pending changes.

        When no *package* argument is given but CWD is inside a package
        directory, the package path is detected automatically and passed
        via ``--only`` so only that package's status is shown.
        """
        chronus_args = ["status"]
        detected_from_cwd = not args.package
        package = self._resolve_package(args.package)
        if package and detected_from_cwd:
            logger.info(f"Detected package from current directory: {package}")
        if package:
            chronus_args.extend(["--only", package])
        return self._run_chronus(chronus_args)
