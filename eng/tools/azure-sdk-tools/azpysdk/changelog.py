import argparse
import os
import shutil
import subprocess
from typing import Optional, List

from .Check import Check, REPO_ROOT
from ci_tools.logging import logger


class changelog(Check):
    """Manage changelogs with Chronus.

    Wraps Chronus CLI commands (add, verify, create, status) so they can be
    invoked through the ``azpysdk`` CLI.  Unlike most checks that operate on
    individual packages, changelog commands run at the **repository root**
    level via ``npx chronus``.
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
                "If omitted, chronus detects modified packages interactively."
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

    def _run_chronus(self, chronus_args: List[str]) -> int:
        """Run a chronus command via ``npx`` from the repository root.

        stdin/stdout/stderr are inherited so that interactive prompts
        (e.g. ``chronus add``) work transparently.
        """
        npx = self._get_npx()
        cmd = [npx, "chronus"] + chronus_args
        logger.info(f"Running: {' '.join(cmd)}")
        return subprocess.call(cmd, cwd=REPO_ROOT)

    # ------------------------------------------------------------------
    # Subcommand handlers
    # ------------------------------------------------------------------

    def _run_add(self, args: argparse.Namespace) -> int:
        """Run ``chronus add`` to interactively add a change entry."""
        chronus_args = ["add"]
        package = getattr(args, "package", None)
        if package:
            chronus_args.append(package)
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
