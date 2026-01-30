#!/usr/bin/env python
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Script to run red team tests with the correct requirements.

This script installs dependencies from dev_requirements_redteam.txt and runs
the red team e2e tests. Use this for local development and dedicated CI jobs.

Usage:
    python scripts/run_redteam_tests.py [pytest_args...]

Example:
    python scripts/run_redteam_tests.py -v -k "test_foundry"
    python scripts/run_redteam_tests.py --collect-only
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    # Get the package root directory
    script_dir = Path(__file__).parent
    package_root = script_dir.parent

    # Path to redteam requirements file
    redteam_requirements = package_root / "dev_requirements_redteam.txt"

    if not redteam_requirements.exists():
        print(f"Error: {redteam_requirements} not found", file=sys.stderr)
        sys.exit(1)

    # Install redteam requirements
    print(f"Installing requirements from {redteam_requirements}...")
    install_result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(redteam_requirements)],
        cwd=str(package_root),
    )
    if install_result.returncode != 0:
        print("Error: Failed to install redteam requirements", file=sys.stderr)
        sys.exit(install_result.returncode)

    # Install the package with redteam extra
    print("Installing azure-ai-evaluation[redteam]...")
    install_pkg_result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", ".[redteam]"],
        cwd=str(package_root),
    )
    if install_pkg_result.returncode != 0:
        print("Error: Failed to install package", file=sys.stderr)
        sys.exit(install_pkg_result.returncode)

    # Build pytest command
    test_dir = package_root / "tests" / "e2etests"
    pytest_args = [
        sys.executable,
        "-m",
        "pytest",
        str(test_dir),
        "-v",
        "--tb=short",
    ]

    # Add any additional arguments passed to this script
    if len(sys.argv) > 1:
        pytest_args.extend(sys.argv[1:])

    # Run tests
    print(f"Running red team tests in {test_dir}...")
    print(f"Command: {' '.join(pytest_args)}")
    test_result = subprocess.run(pytest_args, cwd=str(package_root))

    sys.exit(test_result.returncode)


if __name__ == "__main__":
    main()
