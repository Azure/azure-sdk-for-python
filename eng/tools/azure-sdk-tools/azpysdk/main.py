"""azpysdk CLI

A minimal command-line interface using argparse. This file provides a
`main()` entrypoint so the package can be invoked as a module
(e.g. `python -m azpysdk.main`) or installed as a console script.
"""

from __future__ import annotations

import argparse
import sys
import os
from typing import Sequence, Optional

from .import_all import import_all
from .mypy import mypy
from .next_mypy import next_mypy
from .pylint import pylint
from .next_pylint import next_pylint
from .sphinx import sphinx
from .next_sphinx import next_sphinx
from .black import black
from .pyright import pyright
from .next_pyright import next_pyright
from .ruff import ruff
from .verifytypes import verifytypes
from .apistub import apistub
from .verify_sdist import verify_sdist
from .whl import whl
from .verify_whl import verify_whl
from .bandit import bandit
from .verify_keywords import verify_keywords
from .generate import generate
from .breaking import breaking
from .devtest import devtest

from ci_tools.logging import configure_logging, logger

__all__ = ["main", "build_parser"]
__version__ = "0.0.0"


def build_parser() -> argparse.ArgumentParser:
    """Create and return the top-level ArgumentParser for the CLI."""
    parser = argparse.ArgumentParser(prog="azpysdk", description="Azure SDK Python tools (minimal CLI)")
    parser.add_argument("-V", "--version", action="version", version=__version__)
    # global flag: allow --isolate to appear before the subcommand as well
    parser.add_argument(
        "--isolate", action="store_true", default=False, help="If set, run in an isolated virtual environment."
    )

    # mutually exclusive logging options
    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument(
        "--quiet", action="store_true", default=False, help="Enable quiet mode (only shows ERROR logs)"
    )
    log_group.add_argument(
        "--verbose", action="store_true", default=False, help="Enable verbose mode (shows DEBUG logs)"
    )
    log_group.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARN", "ERROR", "FATAL"], help="Set the logging level."
    )

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "target",
        nargs="?",
        default="**",
        help="Glob pattern for packages. Defaults to '**', but will match patterns below CWD if a value is provided.",
    )
    # allow --isolate to be specified after the subcommand as well
    common.add_argument(
        "--isolate", action="store_true", default=False, help="If set, run in an isolated virtual environment."
    )

    subparsers = parser.add_subparsers(title="commands", dest="command")

    # register our checks with the common params as their parent
    import_all().register(subparsers, [common])
    mypy().register(subparsers, [common])
    next_mypy().register(subparsers, [common])
    pylint().register(subparsers, [common])
    next_pylint().register(subparsers, [common])
    sphinx().register(subparsers, [common])
    next_sphinx().register(subparsers, [common])
    black().register(subparsers, [common])
    pyright().register(subparsers, [common])
    next_pyright().register(subparsers, [common])
    ruff().register(subparsers, [common])
    verifytypes().register(subparsers, [common])
    apistub().register(subparsers, [common])
    verify_sdist().register(subparsers, [common])
    whl().register(subparsers, [common])
    verify_whl().register(subparsers, [common])
    bandit().register(subparsers, [common])
    verify_keywords().register(subparsers, [common])
    generate().register(subparsers, [common])
    breaking().register(subparsers, [common])
    devtest().register(subparsers, [common])

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entrypoint.

    Args:
        argv: Optional list of arguments to parse (defaults to sys.argv[1:]).

    Returns:
        Exit code to return to the OS.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(args)

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    try:
        result = args.func(args)
        return int(result or 0)
    except KeyboardInterrupt:
        logger.error("Interrupted by user")
        return 130
    except Exception as exc:  # pragma: no cover - simple top-level error handling
        logger.error(f"Error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
