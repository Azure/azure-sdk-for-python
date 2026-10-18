# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run legacy-derived container throughput reads or replacements with captured results."""

import argparse
import ast
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pytest

from run_database_throughput_parity import _source_for_backend


ROOT = Path(__file__).resolve().parents[2]


def test_files(operation):
    """Reuse original-derived cases shared with neighboring operation families.

    :param str operation: Read or replacement selection.
    :returns: Original-derived test files.
    :rtype: list[pathlib.Path]
    """
    files = sorted((ROOT / "tests" / "get_container_throughput").glob("*/legacy/test_*.py"))
    if operation == "replace":
        excluded = {
            "test_auto_scale.py", "test_auto_scale_async.py",
            "test_backwards_compatibility.py", "test_crud_subpartition.py",
        }
        files = [path for path in files if path.name not in excluded]
        files.extend(sorted((ROOT / "tests" / "replace_throughput").glob("*/legacy/test_*.py")))
    for surface in ("sync", "aio"):
        files.append(ROOT / "tests" / "replace_database_throughput" / surface / "legacy" / "test_auto_scale.py")
        files.append(ROOT / "tests" / "get_database_throughput" / surface / "legacy" / "test_cosmos_responses.py")
        if operation == "get":
            files.append(ROOT / "tests" / "read_container" / surface / "legacy" / "test_crud_container.py")
    return files


def test_targets(path, operation):
    """Select container tests without rerunning unrelated database assertions.

    :param pathlib.Path path: Original or backend-pinned temporary test file.
    :param str operation: Read or replacement selection.
    :returns: Selected pytest method identifiers.
    :rtype: list[str]
    """
    targets = []
    for cls in ast.parse(path.read_text(encoding="utf-8")).body:
        if not isinstance(cls, ast.ClassDef):
            continue
        for method in cls.body:
            if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) or not method.name.startswith("test_"):
                continue
            if path.name == "test_cosmos_responses.py" and "container_replace_throughput" not in method.name:
                continue
            if "read_container" in path.parts and method.name not in (
                "test_partitioned_collection", "test_partitioned_collection_async",
            ):
                continue
            if operation == "replace" and path.name != "test_container_properties_cache.py" and not any(
                isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "replace_throughput" for node in ast.walk(method)
            ):
                continue
            targets.append(f"{path}::{cls.name}::{method.name}")
    if not targets:
        raise AssertionError(f"No container throughput {operation} tests in {path}")
    return targets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True, choices=("core-python", "rust"))
    parser.add_argument("--operation", choices=("get", "replace"), default="get")
    args = parser.parse_args()
    os.chdir(ROOT)
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    os.environ.pop("COSMOS_BACKEND", None)
    os.environ["COSMOS_PARITY_CAPTURE_OP"] = f"{args.operation}_throughput"
    options = [
        "--noconftest", "--import-mode=importlib", "-p", "common.parity_capture_plugin",
        "-p", "no:cacheprovider", "-v", "-s", "--disable-warnings", "--tb=short",
    ]
    files = test_files(args.operation)
    for path in files:
        _source_for_backend(path, "rust")
    if args.backend == "rust":
        return pytest.main(options + [target for path in files for target in test_targets(path, args.operation)])
    artifacts = ROOT / "docs" / "V5" / "_parity_runs"
    artifacts.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="container_throughput_corepy_", dir=artifacts) as temporary:
        baseline_files = []
        for path in files:
            target = Path(temporary) / path.parent.parent.parent.name / path.parent.parent.name / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(_source_for_backend(path, "core-python"), encoding="utf-8")
            baseline_files.extend(test_targets(target, args.operation))
        return pytest.main(options + baseline_files)


if __name__ == "__main__":
    sys.exit(main())
