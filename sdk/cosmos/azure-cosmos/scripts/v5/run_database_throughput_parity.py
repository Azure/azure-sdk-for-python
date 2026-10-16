# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run the four database-throughput legacy copies with owned fixtures.

Only the explicit backend selection changes in the temporary core-Python
copies. Original shared class setup is not audited. Save each run separately
and compare with build_legacy_parity_audit.py --op get_database_throughput
--expected-count 4.
"""

import argparse
import ast
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pytest


ROOT = Path(__file__).resolve().parents[2]


def _source_for_backend(path, backend):
    text = path.read_text(encoding="utf-8")
    pins = [
        node.value for node in ast.walk(ast.parse(text))
        if isinstance(node, ast.keyword) and node.arg == "_backend"
        and isinstance(node.value, ast.Constant) and node.value.value == "rust"
    ]
    if len(pins) != 1:
        raise AssertionError(f"Expected exactly one Rust client factory in {path}")
    value = pins[0]
    lines = text.splitlines(keepends=True)
    line = lines[value.lineno - 1]
    lines[value.lineno - 1] = line[:value.col_offset] + repr(backend) + line[value.end_col_offset:]
    return "".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True, choices=("core-python", "rust"))
    args = parser.parse_args()
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT / "tests"))
    os.environ.pop("COSMOS_BACKEND", None)
    os.environ["COSMOS_PARITY_CAPTURE_OP"] = "get_database_throughput"
    options = [
        "--noconftest", "--import-mode=importlib", "-p", "common.parity_capture_plugin",
        "-p", "no:cacheprovider", "-v", "-s", "--disable-warnings", "--tb=short",
    ]
    files = [
        ROOT / "tests" / "get_database_throughput" / surface / "legacy" / filename
        for surface in ("sync", "aio")
        for filename in ("test_crud_database.py", "test_auto_scale.py")
    ]
    for path in files:
        _source_for_backend(path, "rust")
    if args.backend == "rust":
        return pytest.main(options + [str(path) for path in files])
    artifacts = ROOT / "docs" / "V5" / "_parity_runs"
    artifacts.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="database_throughput_corepy_", dir=artifacts) as temporary:
        baseline_files = []
        for path in files:
            target = Path(temporary) / path.parent.parent.name / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                _source_for_backend(path, "core-python"),
                encoding="utf-8",
            )
            baseline_files.append(str(target))
        return pytest.main(options + baseline_files)


if __name__ == "__main__":
    sys.exit(main())
