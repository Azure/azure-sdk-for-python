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
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        (cls.name, method.name): method
        for cls in tree.body if isinstance(cls, ast.ClassDef)
        for method in cls.body
        if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
        and method.name.startswith("test_")
    }


def test_replacement_methods_match_originals():
    count = 0
    for path in sorted(FAMILY.glob("*/legacy/test_*.py")):
        suffix = "_async" if path.parent.parent.name == "aio" else ""
        original = _methods(ROOT / "tests" / f"{path.stem}{suffix}.py")
        for key, method in _methods(path).items():
            assert ast.dump(method) == ast.dump(original[key]), (path, key)
            count += 1
    assert count == 18


def test_replacement_collection_keeps_both_surfaces():
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
