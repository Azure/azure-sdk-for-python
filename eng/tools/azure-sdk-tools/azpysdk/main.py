"""azpysdk CLI

A minimal command-line interface using argparse. This file provides a
`main()` entrypoint so the package can be invoked as a module
(e.g. `python -m azpysdk.main`) or installed as a console script.
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence, Optional

from .whl import whl

__all__ = ["main", "build_parser"]
__version__ = "0.0.0"

def build_parser() -> argparse.ArgumentParser:
    """Create and return the top-level ArgumentParser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="azpysdk", description="Azure SDK Python tools (minimal CLI)"
    )
    parser.add_argument("-V", "--version", action="version", version=__version__)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Glob pattern for packages. Defaults to '.', but will match patterns below CWD."
    )

    subparsers = parser.add_subparsers(title="commands", dest="command")

    # register the whl check
    whl().register(subparsers, [common])

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

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    try:
        result = args.func(args)
        return int(result or 0)
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
        return 130
    except Exception as exc:  # pragma: no cover - simple top-level error handling
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
