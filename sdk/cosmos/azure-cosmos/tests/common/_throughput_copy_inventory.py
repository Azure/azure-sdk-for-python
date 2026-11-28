# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Select the original-derived throughput tests that offline inventory checks inspect.

Database and container throughput reads and replacements are spread across
neighboring operation families. These functions list the copied test files
(``# Source:`` headers) and the methods that exercise each operation, so unit
tests can check that every original contract is still covered.
"""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _has_call(method, attribute):
    return any(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == attribute
        for node in ast.walk(method)
    )


def _test_methods(path):
    for cls in ast.parse(path.read_text(encoding="utf-8")).body:
        if not isinstance(cls, ast.ClassDef):
            continue
        for method in cls.body:
            if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and method.name.startswith("test_"):
                yield cls, method


def database_test_files(operation):
    """Return copied database throughput files for ``"get"`` or ``"replace"``."""
    family = f"{operation}_database_throughput"
    files = sorted(
        path for path in (ROOT / "tests" / family).glob("*/test_*.py")
        if "# Source:" in path.read_text(encoding="utf-8")
    )
    if operation == "get":
        files.extend(
            ROOT / "tests" / "replace_database_throughput" / surface / "test_auto_scale.py"
            for surface in ("sync", "aio")
        )
        files.append(ROOT / "tests" / "get_container_throughput" / "sync" / "test_backwards_compatibility.py")
    else:
        files.extend(
            ROOT / "tests" / "get_database_throughput" / surface / filename
            for surface in ("sync", "aio")
            for filename in ("test_cosmos_responses.py", "test_crud_response_payload_on_write_disabled.py")
        )
    return files


def database_test_targets(path, operation):
    """Return pytest node IDs in ``path`` that read or replace database throughput."""
    if operation == "get" and path.name != "test_cosmos_responses.py":
        return [str(path)]
    targets = [
        f"{path}::{cls.name}::{method.name}"
        for cls, method in _test_methods(path)
        if not method.name.startswith("test_container_") and _has_call(method, "replace_throughput")
    ]
    if not targets:
        raise AssertionError(f"No throughput replacement tests in {path}")
    return targets


def container_test_files(operation):
    """Return copied container throughput files for ``"get"`` or ``"replace"``."""
    files = sorted((ROOT / "tests" / "get_container_throughput").glob("*/test_*.py"))
    if operation == "replace":
        excluded = {
            "test_auto_scale.py", "test_auto_scale_async.py",
            "test_backwards_compatibility.py", "test_crud_subpartition.py", "test_none_options.py",
        }
        files = [path for path in files if path.name not in excluded]
        files.extend(sorted((ROOT / "tests" / "replace_throughput").glob("*/test_*.py")))
    for surface in ("sync", "aio"):
        files.append(ROOT / "tests" / "replace_database_throughput" / surface / "test_auto_scale.py")
        files.append(ROOT / "tests" / "get_database_throughput" / surface / "test_cosmos_responses.py")
        if operation == "get":
            files.append(ROOT / "tests" / "read_container" / surface / "test_crud_container.py")
    return [path for path in files if "# Source:" in path.read_text(encoding="utf-8")]


def container_test_targets(path, operation):
    """Return pytest node IDs in ``path`` that read or replace container throughput."""
    targets = []
    for cls, method in _test_methods(path):
        if path.name == "test_cosmos_responses.py" and "container_replace_throughput" not in method.name:
            continue
        if "read_container" in path.parts and method.name not in (
            "test_partitioned_collection_rust", "test_partitioned_collection_async_rust",
        ):
            continue
        if (
            operation == "replace" and path.name != "test_container_properties_cache.py"
            and not _has_call(method, "replace_throughput")
        ):
            continue
        targets.append(f"{path}::{cls.name}::{method.name}")
    if not targets:
        raise AssertionError(f"No container throughput {operation} tests in {path}")
    return targets
