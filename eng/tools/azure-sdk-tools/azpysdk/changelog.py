import argparse
import os
import shutil
import subprocess
import sys
from typing import Optional, List

from .Check import Check, REPO_ROOT
from ci_tools.logging import logger

# The expected Chronus package name in node_modules
_CHRONUS_PACKAGE = "@chronus/chronus"
_CHRONUS_MODULE_PATH = os.path.join("node_modules", "@chronus", "chronus")

# Valid change kinds from .chronus/config.yaml.  Kept in sync manually
# so the CLI can validate before calling out to chronus.
_CHANGE_KINDS = ["breaking", "feature", "deprecation", "fix", "dependencies", "internal"]


class changelog(Check):
    """Manage changelogs with Chronus.

    Wraps Chronus CLI commands (add, verify, create, status) so they can be
    invoked through the ``azpysdk`` CLI.  Commands can be run from the
    repository root **or** from within a package directory — the tool will
    detect the package path automatically when possible.
    """

    def __init__(self) -> None:
        super().__init__()

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
            "--kind", "-k",
            choices=_CHANGE_KINDS,
            default=None,
            help=(
                "Kind of change (e.g. breaking, feature, fix). "
                "If omitted, chronus will prompt interactively."
            ),
        )
        add_p.add_argument(
            "--message", "-m",
            default=None,
            help=(
                "Short description of the change. "
                "If omitted, chronus will prompt interactively."
            ),
        )
        add_p.set_defaults(func=self._run_add)

        # changelog verify
        verify_p = changelog_sub.add_parser("verify", help="Verify all modified packages have change entries")
        verify_p.set_defaults(func=self._run_verify)

        # changelog create
        create_p = changelog_sub.add_parser(
            "create", help="Generate CHANGELOG.md from pending chronus entries"
        )
        create_p.set_defaults(func=self._run_create)

        # changelog status
        status_p = changelog_sub.add_parser(
            "status", help="Show a summary of pending changes and resulting version bumps"
        )
        status_p.set_defaults(func=self._run_status)

        # Default behaviour when no subcommand is given
        p.set_defaults(func=self._no_subcommand, _changelog_parser=p)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _no_subcommand(self, args: argparse.Namespace) -> int:
        """Print help when no changelog subcommand is provided."""
        args._changelog_parser.print_help()
        return 1

    def _get_npx(self) -> str:
        """Locate the ``npx`` executable on *PATH*."""
        npx = shutil.which("npx")
        if not npx:
            logger.error(
                "npx is not installed. Chronus requires Node.js. "
                "Please install Node.js (LTS) from https://nodejs.org/ and try again."
            )
            raise FileNotFoundError("npx not found on PATH")
        return npx

    def _is_chronus_installed(self) -> bool:
        """Return ``True`` if Chronus is installed locally in *node_modules*."""
        return os.path.isdir(os.path.join(REPO_ROOT, _CHRONUS_MODULE_PATH))

    def _ensure_chronus_installed(self) -> None:
        """Verify that Chronus is installed locally, offering to install if not.

        Security: we **never** allow ``npx`` to silently download packages
        from the npm registry.  Instead we check for a local installation
        and, when missing, run ``npm install`` against the repo-root
        ``package.json`` so only declared dependencies are resolved.

        Raises ``SystemExit`` if the user declines or installation fails.
        """
        if self._is_chronus_installed():
            return

        npm = shutil.which("npm")
        if not npm:
            logger.error(
                "Chronus is not installed and npm was not found on PATH.\n"
                "Please install Node.js (LTS) from https://nodejs.org/ then run:\n\n"
                f"    cd {REPO_ROOT}\n"
                "    npm install\n"
            )
            raise SystemExit(1)

       
        if sys.stdin.isatty():
            print(
                "\nChronus is not installed locally. It is listed as a dev dependency\n"
                f"in {os.path.join(REPO_ROOT, 'package.json')}.\n"
            )
            answer = input("Run 'npm install' in the repo root to install it? [Y/n] ").strip().lower()
            if answer not in ("", "y", "yes"):
                logger.info("Skipped Chronus installation.")
                raise SystemExit(1)
        else:
            logger.info("Chronus not installed — running 'npm install' automatically (non-interactive).")
       
        logger.info(f"Running: npm install  (cwd: {REPO_ROOT})")
        rc = subprocess.call([npm, "install"], cwd=REPO_ROOT)
        if rc != 0:
            logger.error("'npm install' failed. Please resolve npm errors and try again.")
            raise SystemExit(rc)

        if not self._is_chronus_installed():
            logger.error(
                "'npm install' succeeded but Chronus was not found in node_modules.\n"
                f"Expected: {os.path.join(REPO_ROOT, _CHRONUS_MODULE_PATH)}\n"
                "Please verify that package.json lists @chronus/chronus as a dependency."
            )
            raise SystemExit(1)

    def _detect_package_from_cwd(self) -> Optional[str]:
        """If CWD is inside a package directory (``sdk/<service>/<package>``),
        return the relative path from the repository root.  Otherwise return
        ``None``.

        The chronus config uses the pattern ``sdk/*/*`` for packages, so we
        look for CWD being at or below ``<REPO_ROOT>/sdk/<service>/<pkg>``.
        """
        try:
            cwd = os.path.abspath(os.getcwd())
            repo = os.path.abspath(REPO_ROOT)
            rel = os.path.relpath(cwd, repo)
        except ValueError:
            # On Windows, relpath raises ValueError when paths are on different drives
            return None

        # rel should start with "sdk/<service>/<package>" (at least 3 components)
        parts = rel.replace("\\", "/").split("/")
        if len(parts) >= 3 and parts[0] == "sdk":
            # Return the first 3 components: sdk/<service>/<package>
            return "/".join(parts[:3])
        return None

    def _run_chronus(self, chronus_args: List[str]) -> int:
        """Run a chronus command via ``npx`` from the repository root.

        Before execution the method verifies that Chronus is installed
        locally and uses ``npx --no`` to prevent automatic downloads
        from the npm registry (supply-chain safety).

        stdin/stdout/stderr are inherited so that interactive prompts
        (e.g. ``chronus add``) work transparently.
        """
        self._ensure_chronus_installed()
        npx = self._get_npx()
        cmd = [npx, "--no", "chronus"] + chronus_args
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
        package = getattr(args, "package", None)
        if not package:
            package = self._detect_package_from_cwd()
            if package:
                logger.info(f"Detected package from current directory: {package}")
        if package:
            chronus_args.append(package)

        kind = getattr(args, "kind", None)
        if kind:
            chronus_args.extend(["--kind", kind])

        message = getattr(args, "message", None)
        if message:
            chronus_args.extend(["--message", message])

        return self._run_chronus(chronus_args)

    def _run_verify(self, args: argparse.Namespace) -> int:
        """Run ``chronus verify`` to check for missing change entries."""
        return self._run_chronus(["verify"])

    def _run_create(self, args: argparse.Namespace) -> int:
        """Run ``chronus changelog`` to generate CHANGELOG.md files."""
        return self._run_chronus(["changelog"])

    def _run_status(self, args: argparse.Namespace) -> int:
        """Run ``chronus status`` to show pending changes."""
        return self._run_chronus(["status"])
