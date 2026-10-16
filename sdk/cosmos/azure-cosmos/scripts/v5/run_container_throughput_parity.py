# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run five legacy-derived container throughput tests with captured inputs and outputs."""

import argparse
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pytest

from run_database_throughput_parity import _source_for_backend


ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True, choices=("core-python", "rust"))
    args = parser.parse_args()
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT / "tests"))
    os.environ.pop("COSMOS_BACKEND", None)
    os.environ["COSMOS_PARITY_CAPTURE_OP"] = "read_offer"
    options = [
        "--noconftest", "--import-mode=importlib", "-p", "common.parity_capture_plugin",
        "-p", "no:cacheprovider", "-v", "-s", "--disable-warnings", "--tb=short",
    ]
    files = [
        ROOT / "tests" / "read_offer" / surface / "legacy" / name
        for surface, names in (
            ("sync", ("test_crud_container.py", "test_backwards_compatibility.py", "test_auto_scale.py")),
            ("aio", ("test_crud_container_async.py", "test_auto_scale_async.py")),
        )
        for name in names
    ]
    for path in files:
        _source_for_backend(path, "rust")
    if args.backend == "rust":
        return pytest.main(options + [str(path) for path in files])
    artifacts = ROOT / "docs" / "V5" / "_parity_runs"
    artifacts.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="container_throughput_corepy_", dir=artifacts) as temporary:
        baseline_files = []
        for path in files:
            target = Path(temporary) / path.parent.parent.name / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(_source_for_backend(path, "core-python"), encoding="utf-8")
            baseline_files.append(str(target))
        return pytest.main(options + baseline_files)


if __name__ == "__main__":
    sys.exit(main())
