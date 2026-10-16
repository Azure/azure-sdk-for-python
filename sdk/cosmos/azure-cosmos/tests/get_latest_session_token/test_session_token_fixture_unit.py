# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep copied assertions identical without running their account fixtures."""

import ast
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("surface,name", [
    ("sync", "test_session_token_helpers.py"),
    ("sync", "test_latest_session_token.py"),
    ("aio", "test_latest_session_token_async.py"),
])
def test_copied_method_bodies_match_originals(surface, name):
    original = ast.parse((ROOT / "tests" / name).read_text(encoding="utf-8-sig"))
    copied = ast.parse(
        (ROOT / "tests" / "get_latest_session_token" / surface / "legacy" / name).read_text(encoding="utf-8")
    )
    originals = {
        node.name: node for node in ast.walk(original)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    }
    methods = [
        node for node in ast.walk(copied)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    ]
    assert len(methods) == (5 if "helpers" in name else 2)
    for method in methods:
        assert ast.dump(ast.Module(body=method.body, type_ignores=[])) == ast.dump(
            ast.Module(body=originals[method.name].body, type_ignores=[])
        ), method.name
    assert not any(
        isinstance(node, ast.Attribute) and node.attr in ("trigger_split", "trigger_split_async")
        for node in ast.walk(copied)
    )
