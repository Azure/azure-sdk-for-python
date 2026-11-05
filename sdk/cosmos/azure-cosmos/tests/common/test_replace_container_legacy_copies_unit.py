# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Protect unchanged replacement assertions and distinct sync/aio collection."""

import ast
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import pytest


ROOT = Path(__file__).resolve().parents[2]
FAMILY = ROOT / "tests" / "replace_container"


@pytest.mark.parametrize("operation", ["read_item", "session_token", "replace_container"])
def test_local_baseline_keeps_surface_paths_distinct_rust(monkeypatch, tmp_path, operation):
    scripts = ROOT / "scripts" / "v5"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location(
        f"layout_{operation}_runner", scripts / f"run_{operation}_parity.py"
    )
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(sys, "argv", ["runner", "--backend", "core-python"])
    monkeypatch.setenv("ACCOUNT_HOST", "https://localhost:8081/")
    monkeypatch.setenv("ACCOUNT_KEY", "unused-offline-test")
    monkeypatch.setenv("COSMOS_BACKEND", "core-python")
    monkeypatch.setenv("COSMOS_PARITY_CAPTURE_OP", operation)
    monkeypatch.setattr(
        runner, "TemporaryDirectory", lambda **kwargs: TemporaryDirectory(dir=tmp_path)
    )

    def inspect_baselines(options):
        paths = [Path(option) for option in options if option.endswith(".py")]
        assert len(paths) == len(set(paths))
        assert {path.parent.name for path in paths} == {"sync", "aio"}
        family = "get_latest_session_token" if operation == "session_token" else operation
        for path in paths:
            original = ROOT / "tests" / family / path.parent.name / path.name
            expected = ast.parse(original.read_text(encoding="utf-8"))
            actual = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(expected):
                if isinstance(node, ast.keyword) and node.arg == "_backend":
                    if isinstance(node.value, ast.Constant) and node.value.value == "rust":
                        node.value.value = "core-python"
            for tree in (expected, actual):
                if ast.get_docstring(tree) is not None:
                    tree.body = tree.body[1:]
            assert ast.dump(actual) == ast.dump(expected)
        return 0

    monkeypatch.setattr(runner.pytest, "main", inspect_baselines)
    if operation == "read_item":
        assert runner.run_copied_suite("core-python", []) == 0
    else:
        assert runner.main() == 0


def _methods(path):
    """Map every test method in a file to its parsed form, keyed by class and name.

    Parsing rather than importing means the comparison below does not need the
    test's dependencies or an account.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
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


def test_replacement_methods_match_originals_rust():
    """Every copied replace-container test is identical to the original it came from.

    The copies exist to run the already-shipped legacy assertions against the
    Rust path. Their value depends entirely on the assertions being unchanged:
    if a copy is quietly edited to suit the new engine, it stops being evidence
    that behavior was preserved and starts being evidence only that the new
    engine agrees with itself.

    The comparison excludes leading explanatory docstrings, formatting and
    comments, but not executable code. The count is pinned at eighteen so that a copy
    silently disappearing is a failure rather than a smaller, still-passing run.
    """
    count = 0
    for path in sorted(FAMILY.glob("*/test_*.py")):
        if "# Source:" not in path.read_text(encoding="utf-8"):
            continue
        suffix = "_async" if path.parent.name == "aio" else ""
        original = _methods(ROOT / "tests" / f"{path.stem}{suffix}.py")
        for key, method in _methods(path).items():
            source_key = (key[0], key[1].removesuffix("_rust"))
            method.name = source_key[1]
            assert ast.dump(method) == ast.dump(original[source_key]), (path, key)
            count += 1
    assert count == 18


def test_replacement_collection_keeps_both_surfaces_rust():
    """The copied tests are all actually collected, sync and async alike.

    Matching the source text is not enough; a copy that cannot be collected
    never runs and protects nothing. A real pytest collection is done in a
    separate process and its results must match the set found by parsing --
    exactly, in both directions, so neither a missing test nor an unexpected
    extra one passes unnoticed.

    The subprocess starts from a clean environment with parity capture switched
    off, so collection reflects the files themselves rather than whatever the
    current session happens to be set up for.
    """
    files = sorted(
        path for path in FAMILY.glob("*/test_*.py")
        if "# Source:" in path.read_text(encoding="utf-8")
    )
    expected = {
        f"{path.relative_to(ROOT).as_posix()}::{cls}::{method}"
        for path in files for cls, method in _methods(path)
    }
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "tests") + os.pathsep + env.get("PYTHONPATH", "")
    env.pop("COSMOS_PARITY_CAPTURE_OP", None)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--noconftest", "--import-mode=importlib",
         "--collect-only", "-q", *map(str, files)],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    collected = {line for line in result.stdout.splitlines() if "::test_" in line}
    assert collected == expected
