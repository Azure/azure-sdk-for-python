"""azpysdk CLI

A minimal command-line interface using argparse. This file provides a
`main()` entrypoint so the package can be invoked as a module
(e.g. `python -m azpysdk.main`) or installed as a console script.
"""

from __future__ import annotations

import argparse
import shutil
import os
import sys
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
from .sdist import sdist
from .whl_no_aio import whl_no_aio
from .verify_whl import verify_whl
from .bandit import bandit
from .verify_keywords import verify_keywords
from .generate import generate
from .breaking import breaking
from .mindependency import mindependency
from .latestdependency import latestdependency
from .samples import samples
from .devtest import devtest
from .optional import optional
from .update_snippet import update_snippet
from .changelog import changelog

from ci_tools.logging import configure_logging, logger

__all__ = ["main", "build_parser"]
__version__ = "0.0.0"

CFS_INDEX_URL = "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/"


def build_parser() -> argparse.ArgumentParser:
    """Create and return the top-level ArgumentParser for the CLI."""
    parser = argparse.ArgumentParser(prog="azpysdk", description="Azure SDK Python tools (minimal CLI)")
    parser.add_argument("-V", "--version", action="version", version=__version__)
    # global flag: allow --isolate to appear before the subcommand as well
    parser.add_argument(
        "--isolate", action="store_true", default=False, help="If set, run in an isolated virtual environment."
    )
    parser.add_argument(
        "--pypi",
        action="store_true",
        default=False,
        help="Use PyPI directly instead of the CFS (Central Feed Services) feed.",
    )
    parser.add_argument(
        "--python",
        default=None,
        dest="python_version",
        metavar="VERSION",
        help=(
            "Python version to use when creating the isolated venv (e.g. 3.13). "
            "Passed through to 'uv venv --python'. Requires --isolate and uv."
        ),
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
    # allow --isolate and --pypi to be specified after the subcommand as well
    # use SUPPRESS so the subparser default doesn't overwrite a value set by the global parser
    common.add_argument(
        "--isolate",
        action="store_true",
        default=argparse.SUPPRESS,
        help="If set, run in an isolated virtual environment.",
    )
    common.add_argument(
        "--pypi",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Use PyPI directly instead of the CFS (Central Feed Services) feed.",
    )
    common.add_argument(
        "--python",
        default=argparse.SUPPRESS,
        dest="python_version",
        metavar="VERSION",
        help=(
            "Python version to use when creating the isolated venv (e.g. 3.13). "
            "Passed through to 'uv venv --python'. Requires --isolate and uv."
        ),
    )
    common.add_argument(
        "--service",
        default=None,
        help="Name of service directory (under sdk/) to scope package discovery. 'auto' is treated as unset.",
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
    sdist().register(subparsers, [common])
    whl_no_aio().register(subparsers, [common])
    verify_whl().register(subparsers, [common])
    bandit().register(subparsers, [common])
    verify_keywords().register(subparsers, [common])
    generate().register(subparsers, [common])
    breaking().register(subparsers, [common])
    mindependency().register(subparsers, [common])
    latestdependency().register(subparsers, [common])
    samples().register(subparsers, [common])
    devtest().register(subparsers, [common])
    optional().register(subparsers, [common])
    update_snippet().register(subparsers, [common])
    changelog().register(subparsers, [common])

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entrypoint.

    Args:
        argv: Optional list of arguments to parse (defaults to sys.argv[1:]).

    Returns:
        Exit code to return to the OS.
    """
    original_cwd = os.getcwd()
    # Save original env vars so we can restore them when azpysdk finishes
    original_pip_index = os.environ.get("PIP_INDEX_URL")
    original_uv_index = os.environ.get("UV_DEFAULT_INDEX")

    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(args)

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    # default to uv if available, but respect an explicit TOX_PIP_IMPL setting
    if "TOX_PIP_IMPL" not in os.environ:
        uv_path = shutil.which("uv")
        if uv_path:
            os.environ["TOX_PIP_IMPL"] = "uv"

    # default to CFS feed unless --pypi is specified, but allow explicit env var override (e.g. for CI)
    if args.pypi:
        # Explicitly set PyPI URLs to override uv.toml CFS default
        os.environ["PIP_INDEX_URL"] = "https://pypi.org/simple/"
        os.environ["UV_DEFAULT_INDEX"] = "https://pypi.org/simple/"
        logger.info("Installing from PyPI (--pypi flag set)")
    else:
        if not os.environ.get("PIP_INDEX_URL"):
            os.environ["PIP_INDEX_URL"] = CFS_INDEX_URL
        if not os.environ.get("UV_DEFAULT_INDEX"):
            os.environ["UV_DEFAULT_INDEX"] = CFS_INDEX_URL

        # Log the feed being used
        if os.environ.get("TOX_PIP_IMPL", None) == "uv":
            logger.info("Installing from feed: %s", os.environ.get("UV_DEFAULT_INDEX"))
        else:
            logger.info("Installing from feed: %s", os.environ.get("PIP_INDEX_URL"))

    # --python requires both --isolate and uv
    python_version = getattr(args, "python_version", None)
    if python_version:
        isolate = getattr(args, "isolate", False)
        if not isolate:
            parser.error(
                "--python requires --isolate to create a virtual environment with the specified Python version."
            )

        pip_impl = os.environ.get("TOX_PIP_IMPL", "pip").lower()
        if pip_impl != "uv":
            parser.error("--python requires uv as the backend. Install uv or set TOX_PIP_IMPL=uv.")

    try:
        result = args.func(args)
        print(f"{args.command} check completed with exit code {result}")
        return int(result or 0)
    except KeyboardInterrupt:
        logger.error("Interrupted by user")
        return 130
    except Exception as exc:  # pragma: no cover - simple top-level error handling
        logger.error(f"Error: {exc}")
        return 2
    finally:
        os.chdir(original_cwd)
        # Restore original env vars (or remove them if they weren't set before)
        if original_pip_index is None:
            os.environ.pop("PIP_INDEX_URL", None)
        else:
            os.environ["PIP_INDEX_URL"] = original_pip_index
        if original_uv_index is None:
            os.environ.pop("UV_DEFAULT_INDEX", None)
        else:
            os.environ["UV_DEFAULT_INDEX"] = original_uv_index


if __name__ == "__main__":
    raise SystemExit(main())
