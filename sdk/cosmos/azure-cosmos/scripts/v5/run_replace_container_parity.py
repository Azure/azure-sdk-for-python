# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Capture unchanged replacement methods using identical, owned setup on either backend.

The core-Python run uses temporary copies changing only the explicit backend pin,
not the test bodies. Original v4 class setup and AAD authentication are not audited.
Run this script in separate processes for the two backends; save stdout for
build_legacy_parity_audit.py --op replace_container --expected-count 18.
"""

import argparse
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pytest


ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True, choices=("core-python", "rust"))
    args = parser.parse_args()
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT / "tests"))
    os.environ.pop("COSMOS_BACKEND", None)
    os.environ["COSMOS_PARITY_CAPTURE_OP"] = "replace_container"
    options = [
        "--noconftest", "--import-mode=importlib", "-p", "common.parity_capture_plugin",
        "-v", "-s", "--disable-warnings", "--tb=short",
    ]
    files = sorted((ROOT / "tests" / "replace_container").glob("*/legacy/test_*.py"))
    if len(files) != 8:
        raise AssertionError(f"Expected eight reviewed legacy files, found {len(files)}")
    if args.backend == "rust":
        return pytest.main(options + [str(path) for path in files])
    artifacts = ROOT / "docs" / "V5" / "_parity_runs"
    artifacts.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="replace_container_corepy_", dir=artifacts) as temporary:
        baseline_files = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            if text.count('_backend="rust"') != 1:
                raise AssertionError(f"Expected exactly one Rust client factory in {path}")
            target = Path(temporary) / path.parent.parent.name / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text.replace('_backend="rust"', '_backend="core-python"'), encoding="utf-8")
            baseline_files.append(str(target))
        return pytest.main(options + baseline_files)


if __name__ == "__main__":
    sys.exit(main())
