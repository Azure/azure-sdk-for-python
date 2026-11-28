# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Protect unchanged replacement assertions and distinct sync/aio collection."""

import ast
import importlib.util
from pathlib import Path
import subprocess

import pytest
from common.sdk_subprocess import sdk_python_command


ROOT = Path(__file__).resolve().parents[2]
FAMILY = ROOT / "tests" / "replace_container"


def _methods(source):
    """Map every test method in a file to its parsed form, keyed by class and name.

    Parsing rather than importing means the comparison below does not need the
    test's dependencies or an account.
    """
    tree = ast.parse(source)
    methods = {
        (cls.name, method.name): method
        for cls in tree.body if isinstance(cls, ast.ClassDef)
        for method in cls.body
        if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
        and method.name.startswith("test_")
    }
    for method in methods.values():
        if ast.get_docstring(method) is not None:
            method.body = method.body[1:]
    return methods


@pytest.fixture(scope="module")
def main_inventory():
    spec = importlib.util.spec_from_file_location(
        "replacement_copy_generator", ROOT / "scripts" / "v5" / "copy_replace_container_legacy.py",
    )
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    inventory = {}
    for filename, source in generator.main_sources().items():
        methods = _methods(source)
        for cls, method in generator.replacement_cases(source):
            inventory[(generator.destination(filename), cls.name, method.name)] = (
                methods[(cls.name, method.name)], cls.decorator_list,
            )
    return inventory


def _replacement_assertions(method):
    start = next(
        index for index, node in enumerate(method.body)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "replace_container" for target in node.targets)
    )
    return ast.dump(ast.Module(body=method.body[start:start + 5], type_ignores=[]))


def test_replacement_methods_match_originals_rust(main_inventory):
    """Keep main's complete inventory, bodies and markers, with explicit API adaptations."""
    actual = set()
    for path in sorted(FAMILY.glob("*/test_*.py")):
        source = path.read_text(encoding="utf-8")
        if "# Source:" not in source:
            continue
        classes = {node.name: node for node in ast.parse(source).body if isinstance(node, ast.ClassDef)}
        for (cls, name), method in _methods(source).items():
            assert name.endswith("_rust"), (path, name)
            key = (path, cls, name.removesuffix("_rust"))
            actual.add(key)
            original, markers = main_inventory[key]
            assert [ast.dump(node) for node in classes[cls].decorator_list] == [
                ast.dump(node) for node in markers
            ], key
            decorators = []
            for decorator in method.decorator_list:
                if isinstance(decorator, ast.Call) and ast.unparse(decorator.func) == "pytest.mark.skip":
                    assert not decorator.args and len(decorator.keywords) == 1
                    reason = decorator.keywords[0]
                    assert reason.arg == "reason" and reason.value.value.startswith("environment-gap:")
                    decorator = decorator.func
                decorators.append(decorator)
            assert [ast.dump(node) for node in decorators] == [
                ast.dump(node) for node in original.decorator_list
            ], key
            method.decorator_list = decorators
            method.name = original.name
            if original.name.startswith("test_session_token_compatibility"):
                # This removed argument must raise TypeError, not retain main's ignored-input behavior.
                assert "Contract change:" in source
            elif original.name.startswith("test_etag_match_condition_compatibility"):
                assert _replacement_assertions(method) == _replacement_assertions(original), key
            else:
                assert ast.dump(method) == ast.dump(original), key
    assert actual == set(main_inventory)


def test_replacement_collection_keeps_both_surfaces_rust():
    """The copied tests are all actually collected, sync and async alike.

    Matching the source text is not enough; a copy that cannot be collected
    never runs and protects nothing. A real pytest collection is done in a
    separate process and its results must match the set found by parsing --
    exactly, in both directions, so neither a missing test nor an unexpected
    extra one passes unnoticed.

    The subprocess starts from a clean environment, so collection reflects the files themselves rather than whatever the
    current session happens to be set up for.
    """
    files = sorted(
        path for path in FAMILY.glob("*/test_*.py")
        if "# Source:" in path.read_text(encoding="utf-8")
    )
    expected = {
        f"{path.relative_to(ROOT).as_posix()}::{cls}::{method}"
        for path in files for cls, method in _methods(path.read_text(encoding="utf-8"))
    }
    result = subprocess.run(
        sdk_python_command(
            "import pytest; raise SystemExit(pytest.main(sys.argv[1:]))",
            "--import-mode=importlib", "--collect-only", "-q", *map(str, files),
        ),
        cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    collected = {line for line in result.stdout.splitlines() if "::test_" in line}
    assert collected == expected
