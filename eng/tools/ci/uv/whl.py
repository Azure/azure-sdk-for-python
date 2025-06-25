#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "wheel==0.45.1",
#   "packaging==24.2",
#   "urllib3==2.2.3",
#   "tomli==2.2.1",
#   "build==1.2.2.post1",
#   "pytest==8.3.5",
#   "pytest-cov==5.0.0",
#   "azure-sdk-tools",
#   "setuptools",
#   "pytest-asyncio==0.24.0",
#   "pytest-custom-exit-code==0.3.0",
#   "pytest-xdist==3.2.1",
#   "coverage==7.6.1",
#   "bandit==1.6.2",
#   "pyproject-api==1.8.0",
#   "jinja2==3.1.6",
#   "json-delta==2.0.2",
#   "readme-renderer==43.0",
#   "python-dotenv==1.0.1",
#   "pyyaml==6.0.2",
#   "six==1.17.0",
# ]
#
# [tool.uv.sources]
# azure-sdk-tools = { path = "../../../../tools/azure-sdk-tools", editable = true }
# ///

import os
import argparse

from ci_tools.functions import discover_targeted_packages

from ci_tools.uv.UVConfig import UVConfig
from ci_tools.variables import discover_repo_root

# — mimic tox’s setenv =
os.environ.setdefault("SPHINX_APIDOC_OPTIONS", "members,undoc-members,inherited-members")
os.environ.setdefault("PROXY_URL", "http://localhost:5000")
os.environ.setdefault("VIRTUALENV_WHEEL", "0.45.1")
os.environ.setdefault("VIRTUALENV_PIP", "24.0")
os.environ.setdefault("VIRTUALENV_SETUPTOOLS", "75.3.2")
os.environ.setdefault("PIP_EXTRA_INDEX_URL", "https://pypi.python.org/simple")

def main():
    parser = argparse.ArgumentParser(
        description="Run dev tooling against a given package directory"
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="azure-core",
        help="Path to the target package folder (default: current directory)",
    )
    args = parser.parse_args()

    # todo: add some path params
    print(args.target)
    target_root_dir=discover_repo_root()
    print(target_root_dir)

    breakpoint()
    targeted = discover_targeted_packages(args.target, target_root_dir)

    breakpoint()


if __name__ == "__main__":
    main()
