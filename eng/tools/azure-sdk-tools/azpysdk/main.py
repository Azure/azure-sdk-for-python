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
from subprocess import check_call

from .whl import whl
from .import_all import import_all
from .mypy import mypy

from ci_tools.scenario import install_into_venv, get_venv_python
from ci_tools.functions import get_venv_call
from ci_tools.variables import discover_repo_root

# right now, we are assuming you HAVE to be in the azure-sdk-tools repo
# we assume this because we don't know how a dev has installed this package, and might be
# being called from within a site-packages folder. Due to that, we can't trust the location of __file__
REPO_ROOT = discover_repo_root()

__all__ = ["main", "build_parser"]
__version__ = "0.0.0"

def build_parser() -> argparse.ArgumentParser:
    """Create and return the top-level ArgumentParser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="azpysdk", description="Azure SDK Python tools (minimal CLI)"
    )
    parser.add_argument("-V", "--version", action="version", version=__version__)
    # global flag: allow --isolate to appear before the subcommand as well
    parser.add_argument("--isolate", action="store_true", default=False,
                        help="If set, run in an isolated virtual environment.")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Glob pattern for packages. Defaults to '.', but will match patterns below CWD if a value is provided."
    )
    # allow --isolate to be specified after the subcommand as well
    common.add_argument(
        "--isolate",
        action="store_true",
        default=False,
        help="If set, run in an isolated virtual environment."
    )

    subparsers = parser.add_subparsers(title="commands", dest="command")

    # register our checks with the common params as their parent
    whl().register(subparsers, [common])
    import_all().register(subparsers, [common])
    mypy().register(subparsers, [common])

    return parser

def handle_venv(isolate: bool, args: argparse.Namespace) -> None:
    """Handle virtual environment commands."""
    # we are already in an isolated venv and so do not need to recurse
    if(os.getenv("AZURE_SDK_TOOLS_VENV", None)):
        return

    # however, if we are not already in an isolated venv, and should be, then we need to
    # call
    if (isolate):
        os.environ["AZURE_SDK_TOOLS_VENV"] = "1"

        venv_cmd = get_venv_call()
        venv_location = os.path.join(REPO_ROOT, f".venv_{args.command}")
        # todo, make this a consistent directory based on the command
        # I'm seriously thinking we should move handle_venv within each check's main(),
        # which will mean that we will _know_ what folder we're in.
        # however, that comes at the cost of not having every check be able to handle one or multiple packages
        # I don't want to get into an isolation loop where every time we need a new venv, we create it, call it,
        # and now as we foreach across the targeted packages we've lost our spot.
        check_call(venv_cmd + [venv_location])

        # now use the current virtual environment to install os.path.join(REPO_ROOT, eng/tools/azure-sdk-tools[build])
        # into the NEW virtual env
        install_into_venv(venv_location, os.path.join(REPO_ROOT, "eng/tools/azure-sdk-tools"), False, "build")
        venv_python_exe = get_venv_python(venv_location)
        command_args = [venv_python_exe, "-m", "azpysdk.main"] + sys.argv[1:]
        check_call(command_args)

def main(argv: Optional[Sequence[str]] = None) -> int:#
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
        # scbedd 8/25 I'm betting that this would be best placed within the check itself,
        # but leaving this for now
        handle_venv(args.isolate, args)
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
