# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run 17 copied local helper cases and four non-split live token tests.

Compare saved transcripts with --op get_latest_session_token --expected-count 21.
Only fixture/backend selection changes; original assertions stay intact.
The utility is local Python on both clients, not a Rust driver operation.
"""

import argparse
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pytest

from run_database_throughput_parity import _source_for_backend


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True, choices=("core-python", "rust"))
    args = parser.parse_args()
    for name in ("ACCOUNT_HOST", "ACCOUNT_KEY"):
        if not os.environ.get(name):
            parser.error(f"{name} must be set explicitly")
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT / "tests"))
    os.environ["COSMOS_BACKEND"] = args.backend
    os.environ["COSMOS_PARITY_CAPTURE_OP"] = "get_latest_session_token"
    options = [
        "--noconftest", "--import-mode=importlib", "-p", "common.parity_capture_plugin",
        "-p", "no:cacheprovider", "-v", "-s", "--disable-warnings", "--tb=short",
    ]
    files = [
        ROOT / "tests" / "get_latest_session_token" / surface / "legacy" / name
        for surface, name in (
            ("sync", "test_session_token_helpers.py"),
            ("sync", "test_latest_session_token.py"),
            ("aio", "test_latest_session_token_async.py"),
        )
    ]
    for path in files:
        _source_for_backend(path, "rust")
    if args.backend == "rust":
        return pytest.main(options + [str(path) for path in files])
    artifacts = ROOT / "docs" / "V5" / "_parity_runs"
    artifacts.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="token_corepy_", dir=artifacts) as temporary:
        baseline_files = []
        for path in files:
            target = Path(temporary) / path.parent.parent.name / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(_source_for_backend(path, "core-python"), encoding="utf-8")
            baseline_files.append(str(target))
        return pytest.main(options + baseline_files)


if __name__ == "__main__":
    sys.exit(main())
