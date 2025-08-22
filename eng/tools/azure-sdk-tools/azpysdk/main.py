"""azpysdk CLI

A minimal command-line interface using argparse. This file provides a
`main()` entrypoint so the package can be invoked as a module
(e.g. `python -m azpysdk.main`) or installed as a console script.
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence, Optional

__all__ = ["main", "build_parser"]
__version__ = "0.0.0"


def _cmd_greet(args: argparse.Namespace) -> int:
    """Simple greet command: prints a greeting."""
    name = args.name or "world"
    print(f"Hello, {name}!")
    return 0


def _cmd_echo(args: argparse.Namespace) -> int:
    """Echo command: prints back the provided message."""
    print(args.message)
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    """Run command: placeholder for running a task or pipeline."""
    print(f"Running task: {args.task}")
    # TODO: implement real behaviour
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Create and return the top-level ArgumentParser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="azpysdk", description="Azure SDK Python tools (minimal CLI)"
    )
    parser.add_argument("-V", "--version", action="version", version=__version__)

    subparsers = parser.add_subparsers(title="commands", dest="command")

    # greet
    p = subparsers.add_parser("greet", help="Greet someone")
    p.add_argument("-n", "--name", help="Name to greet")
    p.set_defaults(func=_cmd_greet)

    # echo
    p = subparsers.add_parser("echo", help="Echo a message")
    p.add_argument("message", help="Message to echo")
    p.set_defaults(func=_cmd_echo)

    # run
    p = subparsers.add_parser("run", help="Run a placeholder task")
    p.add_argument("-t", "--task", default="default", help="Task name to run")
    p.set_defaults(func=_cmd_run)

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
