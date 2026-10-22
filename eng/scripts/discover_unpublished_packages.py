#!/usr/bin/env python

"""Discovers unreleased azure-mgmt-* packages not yet on PyPI and generates
name-reservation placeholders for each."""

import argparse
import sys

from ci_tools.functions import discover_targeted_packages
from ci_tools.parsing import ParsedSetup
from packaging_tools.generate_namereserve_package import generate_main
from pypi_tools.pypi import PyPIClient

INITIAL_VERSION = "1.0.0b1"


def _is_on_pypi(client, name):
    try:
        result = client.project(name)
        return "info" in result
    except Exception:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--version", default="0.0.0")
    parser.add_argument("--root-dir", default=".")
    args = parser.parse_args()

    folders = discover_targeted_packages("azure-mgmt-*", args.root_dir, filter_type="Build", compatibility_filter=False)
    candidates = [ParsedSetup.from_path(f) for f in folders]
    pypi = PyPIClient()
    to_register = [p for p in candidates if p.version == INITIAL_VERSION and not _is_on_pypi(pypi, p.name)]

    for pkg in to_register:
        print(f"Generating reservation package: {pkg.name}")
        generate_main(["--output_dir", args.output_dir, "--package_version", args.version, pkg.name])

    if not to_register:
        print("No unregistered management packages found.")

    print(f"##vso[task.setvariable variable=HasPackages;isOutput=true]{'true' if to_register else 'false'}")
