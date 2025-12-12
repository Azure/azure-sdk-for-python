"""Utilities for generating a placeholder package to reserve a name on PyPI."""

import argparse
import shutil
import tempfile
from pathlib import Path
import logging
from typing import Optional

from ci_tools.build import build_packages

logger = logging.getLogger("azure-sdk-tools.packaging.name-reserve")


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a minimal Python distribution that can be published to PyPI "
            "in order to reserve a package name."
        )
    )
    parser.add_argument(
        "--working-dir",
        help=(
            "Temporary workspace used to author the placeholder project. "
            "Defaults to the current platform temp directory."
        ),
        default=None,
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where the built distributions will be written.",
    )
    parser.add_argument(
        "--package_version",
        default="0.0.0",
        help="The distribution version to reserve on PyPI (Defaults to 0.0.0).",
    )

    parser.add_argument(
        "package_name",
        help="The distribution name to reserve on PyPI (e.g. azure-mgmt-servicename).",
    )
    return parser.parse_args(argv)


def _normalise_module_name(dist_name: str) -> str:
    return dist_name.replace("-", "_")


def _write_placeholder_project(project_dir: Path, package_name: str) -> None:
    module_name = _normalise_module_name(package_name)
    src_dir = project_dir / "src" / module_name
    src_dir.mkdir(parents=True, exist_ok=True)

    readme = project_dir / "README.md"
    readme.write_text(
        (
            f"""
# This package will be `{package_name}`

The `Azure SDK` team develops packages in public. As such, there is a window of time from when a package name is
chosen publically, and when it becomes available on PyPI.

This name-only package is being published by the Python team to prevent rename churn during this gap.
"""
        ),
        encoding="utf-8",
    )

    pyproject = project_dir / "pyproject.toml"
    pyproject.write_text(
        (
            f"""
[build-system]
requires = ["setuptools>=77.0.3", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
authors = [
    {{name = "Microsoft Corporation", email = "azuresdkengsysadmins@microsoft.com"}},
]
description = "This package will be released in the near future. Stay tuned!"
keywords = ["azure", "azure sdk"]
requires-python = ">=3.9"
license = "MIT"
version = "0.0.0"
classifiers = [
    "Development Status :: 1 - Planning",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
]
dependencies = []
dynamic = ["readme"]

[project.urls]
"Bug Reports" = "https://github.com/Azure/azure-sdk-for-python/issues"
repository = "https://github.com/Azure/azure-sdk-for-python"

[tool.setuptools.dynamic]
readme = {{file = ["README.md"], content-type = "text/markdown"}}
"""
        ),
        encoding="utf-8",
    )


def _build_distributions(project_dir: str, output_dir: str) -> None:
    build_packages([project_dir], distribution_directory=output_dir)


def generate_main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)

    work_root = Path(args.working_dir) if args.working_dir else Path(tempfile.gettempdir())
    work_root.mkdir(parents=True, exist_ok=True)

    project_dir = work_root / f"{args.package_name}"

    if project_dir.exists():
        logger.info("Removing existing project directory %s", project_dir)
        shutil.rmtree(project_dir)

    project_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Creating placeholder project for %s in %s", args.package_name, project_dir)
    _write_placeholder_project(project_dir, args.package_name)

    try:
        _build_distributions(str(project_dir), args.output_dir)
    finally:
        logger.info("Cleaning up working directory %s", project_dir)
        shutil.rmtree(project_dir, ignore_errors=True)

    logger.info("Finished generating distributions for %s", args.package_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(generate_main())
