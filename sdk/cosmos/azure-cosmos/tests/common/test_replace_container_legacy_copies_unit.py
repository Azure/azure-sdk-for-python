# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Protect unchanged replacement assertions and distinct sync/aio collection."""

import ast
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
FAMILY = ROOT / "tests" / "replace_container"


def _methods(path):
    """Map every test method in a file to its parsed form, keyed by class and name.

    Parsing rather than importing means the comparison below does not need the
    test's dependencies or an account.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        (cls.name, method.name): method
        for cls in tree.body if isinstance(cls, ast.ClassDef)
        for method in cls.body
        if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
        and method.name.startswith("test_")
    }


def test_replacement_methods_match_originals():
    """Every copied replace-container test is identical to the original it came from.

    The copies exist to run the already-shipped legacy assertions against the
    Rust path. Their value depends entirely on the assertions being unchanged:
    if a copy is quietly edited to suit the new engine, it stops being evidence
    that behavior was preserved and starts being evidence only that the new
    engine agrees with itself.

    The comparison is made on the parsed form, so formatting and comments may
    differ but the code may not. The count is pinned at eighteen so that a copy
    silently disappearing is a failure rather than a smaller, still-passing run.
    """
    count = 0
    for path in sorted(FAMILY.glob("*/legacy/test_*.py")):
        suffix = "_async" if path.parent.parent.name == "aio" else ""
        original = _methods(ROOT / "tests" / f"{path.stem}{suffix}.py")
        for key, method in _methods(path).items():
            assert ast.dump(method) == ast.dump(original[key]), (path, key)
            count += 1
    assert count == 18


def test_replacement_collection_keeps_both_surfaces():
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
    files = sorted(FAMILY.glob("*/legacy/test_*.py"))
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
