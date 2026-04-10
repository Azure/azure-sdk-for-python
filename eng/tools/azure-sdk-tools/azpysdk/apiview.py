"""azpysdk apiview subcommand – generates api.md for Python SDK packages.

Running ``azpysdk apiview`` is equivalent to ``azpysdk apistub --md``:
it generates the APIView token JSON **and** the human-readable ``api.md``
file, placing ``api.md`` in the package directory so it can be tracked by git.
"""

from __future__ import annotations

import argparse
from typing import List, Optional

from .apistub import apistub


class apiview(apistub):
    """apiview subcommand: wraps apistub with ``--md`` enabled by default.

    Designed for mass-regeneration of ``api.md`` across the repository.
    The output ``api.md`` is written into the package directory (tracked by
    git), making it easy to detect changes and open a PR.
    """

    def register(
        self,
        subparsers: "argparse._SubParsersAction",
        parent_parsers: Optional[List[argparse.ArgumentParser]] = None,
    ) -> None:
        """Register the apiview subcommand."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "apiview",
            parents=parents,
            help=(
                "Generate api.md for a package using the API stub generator. "
                "api.md is written into the package directory by default "
                "(equivalent to ``azpysdk apistub --md``)."
            ),
        )
        p.add_argument(
            "--dest-dir",
            dest="dest_dir",
            default=None,
            help="Destination directory for generated API stub token files.",
        )
        p.add_argument(
            "--md",
            dest="generate_md",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Generate api.md from the token JSON file (enabled by default for apiview; use --no-md to skip).",
        )
        p.set_defaults(func=self.run)
