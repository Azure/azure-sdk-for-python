# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Temporary main-branch correspondence checks; permanent auth checks live separately.

Own the primary CRUD read scenarios and the response-header, None-option and
properties-cache read families. Creation-policy and throughput scenarios that
also read properties remain owned by their respective API suites.
"""

import ast
import copy
import io
from pathlib import Path
import re
import subprocess
import zipfile

import pytest
from common.sdk_subprocess import sdk_python_command


ROOT = Path(__file__).resolve().parents[2]
FAMILY = ROOT / "tests" / "read_container"
PREFIX = "sdk/cosmos/azure-cosmos/tests/"
SOURCE_FAMILIES = {
    "test_crud_container", "test_cosmos_responses", "test_none_options",
    "test_container_properties_cache",
}
ADDITIONAL_READ_CASES = {
    (FAMILY / surface / "test_container_properties_cache.py", "TestContainerPropertiesCache", name):
    ["cosmosLong", "cosmosAADLong"]
    for surface, name in (
        ("sync", "test_not_modified_read_preserves_properties_cache"),
        ("aio", "test_not_modified_read_preserves_properties_cache_async"),
    )
}


def _methods(source):
    for cls in ast.parse(source).body:
        if isinstance(cls, ast.ClassDef):
            for method in cls.body:
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and method.name.startswith("test_"):
                    if ast.get_docstring(method) is not None:
                        method.body = method.body[1:]
                    yield cls, method


def _owns_read(filename, method):
    reads = [
        node for node in ast.walk(method)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and node.func.attr == "read"
        and any(word in ast.unparse(node.func.value).lower() for word in ("container", "collection"))
    ]
    if not reads:
        return False
    if filename.startswith("test_crud_container"):
        return (
            method.name.startswith(("test_container_read", "test_read_container"))
            or re.fullmatch(r"test_collection_crud(?:_async)?", method.name) is not None
            or method.name.startswith("test_partitioned_collection")
        )
    return True


@pytest.fixture(scope="module")
def main_inventory():
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT.parents[2], stderr=subprocess.PIPE)

    try:
        revision = git("rev-parse", "origin/main").decode().strip()
        paths = [
            path for path in git("ls-tree", "-r", "--name-only", revision, "--", PREFIX).decode().splitlines()
            if Path(path).stem.removesuffix("_async") in SOURCE_FAMILIES
        ]
        assert paths, "No main read-test sources found"
        archive = git("archive", "--format=zip", revision, *paths)
    except subprocess.CalledProcessError as error:
        pytest.fail("Fetch origin/main before checking read-test migration: " + error.stderr.decode())
    inventory = {}
    with zipfile.ZipFile(io.BytesIO(archive)) as files:
        for path in paths:
            filename = path.removeprefix(PREFIX)
            surface = "aio" if filename.endswith("_async.py") else "sync"
            destination = FAMILY / surface / filename.replace("_async.py", ".py")
            for cls, method in _methods(files.read(path).decode("utf-8-sig")):
                if _owns_read(filename, method):
                    inventory[(destination, cls.name, method.name)] = (filename, cls.decorator_list, method)
    assert inventory, "No main read cases found"
    return inventory


def test_read_copies_preserve_main_inventory_markers_and_assertions_rust(main_inventory):
    actual = set()
    for path in sorted(FAMILY.glob("*/test_*.py")):
        source = path.read_text(encoding="utf-8")
        for cls, method in _methods(source):
            assert method.name.endswith("_rust"), (path, method.name)
            key = (path, cls.name, method.name.removesuffix("_rust"))
            actual.add(key)
            if key in ADDITIONAL_READ_CASES:
                continue
            filename, markers, original = main_inventory[key]
            assert [ast.dump(node) for node in cls.decorator_list] == [ast.dump(node) for node in markers], key
            method.name = original.name
            expected = copy.deepcopy(original)
            if filename.startswith("test_container_properties_cache"):
                # Only this extra cache-loading step differs from main. All
                # original calls, assertions and decorators must remain intact.
                index = next(
                    index for index, statement in enumerate(expected.body)
                    if any(
                        isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "create_item"
                        for node in ast.walk(statement)
                    )
                )
                prefix = "await " if isinstance(method, ast.AsyncFunctionDef) else ""
                expected.body.insert(index + 1, ast.parse(
                    prefix + "created_db.get_container_client(container_name)._get_properties()"
                ).body[0])
                assert "Rust adaptation: item creation no longer warms Python's metadata cache." in source
            assert ast.dump(method) == ast.dump(expected), key
            assert f"Source: tests/{filename}::{cls.name}.{original.name}" in source, key
    assert actual == set(main_inventory) | set(ADDITIONAL_READ_CASES)


def test_read_collection_preserves_markers_and_numbered_skips_rust(main_inventory):
    expected = {}
    for (path, cls, name), (_, markers, method) in main_inventory.items():
        expected[f"{path.relative_to(ROOT).as_posix()}::{cls}::{name}_rust"] = [
            ast.unparse(node).removeprefix("pytest.mark.")
            for node in [*markers, *method.decorator_list]
            if isinstance(node, ast.Attribute) and ast.unparse(node).startswith("pytest.mark.")
        ]
    for (path, cls, name), markers in ADDITIONAL_READ_CASES.items():
        expected[f"{path.relative_to(ROOT).as_posix()}::{cls}::{name}_rust"] = markers
    code = f"""
import re
import pytest

class CheckCollection:
    def pytest_collection_finish(self, session):
        expected = {expected!r}
        assert {{item.nodeid for item in session.items}} == set(expected)
        for item in session.items:
            assert set(expected[item.nodeid]) <= {{mark.name for mark in item.iter_markers()}}
            for name in ("skip", "skipif"):
                for mark in item.iter_markers(name):
                    assert re.search(r"gap[- ]+[0-9]+", mark.kwargs.get("reason", ""), re.I), item.nodeid

raise SystemExit(pytest.main([
    "tests/read_container/sync", "tests/read_container/aio",
    "--import-mode=importlib", "--collect-only", "-q",
], plugins=[CheckCollection()]))
"""
    result = subprocess.run(
        sdk_python_command(code), cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
