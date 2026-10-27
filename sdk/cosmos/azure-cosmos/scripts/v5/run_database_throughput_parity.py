# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run database throughput read or replacement copies with owned fixtures.

Only the explicit backend selection changes in the temporary core-Python
copies. Original shared class setup is not audited. Save each run separately
and compare with build_legacy_parity_audit.py using get_database_throughput
or replace_database_throughput as the operation. The read selection has 15
tests; the replacement selection has eight.
"""

import argparse
import ast
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pytest


ROOT = Path(__file__).resolve().parents[2]


def test_files(operation):
    """Include reads owned by neighboring operation families without copying them again."""
    family = f"{operation}_database_throughput"
    files = sorted((ROOT / "tests" / family).glob("*/legacy/test_*.py"))
    if operation == "get":
        files.extend(
            ROOT / "tests" / "replace_database_throughput" / surface / "legacy" / "test_auto_scale.py"
            for surface in ("sync", "aio")
        )
        files.append(
            ROOT / "tests" / "get_container_throughput" / "sync" / "legacy" / "test_backwards_compatibility.py"
        )
    else:
        files.extend(
            ROOT / "tests" / "get_database_throughput" / surface / "legacy" / filename
            for surface in ("sync", "aio")
            for filename in ("test_cosmos_responses.py", "test_crud_response_payload_on_write_disabled.py")
        )
    return files


def test_targets(path, operation):
    """Reuse original copies, selecting only methods that replace throughput.

    :param path: Original-derived test file.
    :type path: pathlib.Path
    :param operation: Throughput operation to select.
    :type operation: str
    :return: File or method node IDs to pass to pytest.
    :rtype: list[str]
    """
    if operation == "get" and path.name != "test_cosmos_responses.py":
        return [str(path)]
    targets = [
        f"{path}::{cls.name}::{method.name}"
        for cls in ast.parse(path.read_text(encoding="utf-8")).body
        if isinstance(cls, ast.ClassDef)
        for method in cls.body
        if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and method.name.startswith("test_")
        and not method.name.startswith("test_container_")
        and any(
            isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "replace_throughput"
            for node in ast.walk(method)
        )
    ]
    if not targets:
        raise AssertionError(f"No throughput replacement tests in {path}")
    return targets


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
    parser.add_argument("--operation", choices=("get", "replace"), default="get")
    args = parser.parse_args()
    os.chdir(ROOT)
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    os.environ.pop("COSMOS_BACKEND", None)
    operation = f"{args.operation}_database_throughput"
    os.environ["COSMOS_PARITY_CAPTURE_OP"] = operation
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
    with TemporaryDirectory(prefix="database_throughput_corepy_", dir=artifacts) as temporary:
        baseline_files = []
        for path in files:
            target = Path(temporary) / path.parent.parent.parent.name / path.parent.parent.name / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                _source_for_backend(path, "core-python"),
                encoding="utf-8",
            )
            baseline_files.extend(test_targets(target, args.operation))
        return pytest.main(options + baseline_files)


if __name__ == "__main__":
    sys.exit(main())
