#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import logging
import os
import shutil
from typing import List


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def find_isolate_dirs(repo_root: str) -> List[str]:
    """Find azpysdk isolate directories under the repository-managed virtual environment root."""
    isolate_root = os.path.join(os.path.abspath(repo_root), ".venv")
    if not os.path.isdir(isolate_root):
        return []

    isolate_dirs = []
    with os.scandir(isolate_root) as packages:
        for package in packages:
            if package.is_symlink() or not package.is_dir(follow_symlinks=False):
                continue
            with os.scandir(package.path) as environments:
                isolate_dirs.extend(
                    environment.path
                    for environment in environments
                    if environment.name.startswith(".venv_")
                    and not environment.is_symlink()
                    and environment.is_dir(follow_symlinks=False)
                )
    return sorted(isolate_dirs)


def cleanup_isolate_dirs(repo_root: str) -> int:
    """Remove azpysdk isolate directories and return the number that could not be removed."""
    isolate_dirs = find_isolate_dirs(repo_root)
    if not isolate_dirs:
        logger.info("No azpysdk isolate directories found for cleanup.")
        return 0

    failures = 0
    for isolate_dir in isolate_dirs:
        try:
            logger.info("Removing azpysdk isolate directory %s", isolate_dir)
            shutil.rmtree(isolate_dir)
        except OSError as exc:
            failures += 1
            logger.warning(
                "Failed to remove isolate directory %s: %s", isolate_dir, exc
            )

    logger.info(
        "Isolate directory cleanup complete: %d removed, %d failed.",
        len(isolate_dirs) - failures,
        failures,
    )
    return failures


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove azpysdk isolate directories after coverage reporting."
    )
    parser.add_argument(
        "--repo-root",
        default=root_dir,
        help="Repository root containing the azpysdk .venv directory.",
    )
    args = parser.parse_args()
    raise SystemExit(1 if cleanup_isolate_dirs(args.repo_root) else 0)
