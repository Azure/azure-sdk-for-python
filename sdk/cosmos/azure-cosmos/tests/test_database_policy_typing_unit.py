# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Checks that the container policy keywords of the sync and async DatabaseProxy are typed the same way."""

import ast
import inspect
import unittest

import pytest

from azure.cosmos import database as sync_database
from azure.cosmos.aio import _database as async_database

METHODS = ("create_container", "create_container_if_not_exists", "replace_container")
POLICY_KEYWORDS = ("indexing_policy", "unique_key_policy", "conflict_resolution_policy")


def _definitions(module, method_name):
    """Yield every definition of a DatabaseProxy method, overloads included."""
    tree = ast.parse(inspect.getsource(module))
    proxy = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "DatabaseProxy")
    for node in proxy.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name:
            yield node


def _annotations(module, method_name):
    """Return {keyword: {annotation, ...}} for the policy keywords of a method."""
    found = {}
    for node in _definitions(module, method_name):
        # The sync client accepts some of these positionally, so look at both kinds of arguments.
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.arg in POLICY_KEYWORDS and arg.annotation is not None:
                found.setdefault(arg.arg, set()).add(ast.unparse(arg.annotation))
    return found


def _documented_types(module, method_name):
    """Return {keyword: {type, ...}} from ':param <type> <name>:' / ':keyword <type> <name>:' docstring lines."""
    found = {}
    for node in _definitions(module, method_name):
        for line in (ast.get_docstring(node) or "").splitlines():
            parts = line.strip().split(":")
            if len(parts) < 3 or not parts[1].startswith(("param ", "keyword ")):
                continue
            documented_type, _, name = parts[1].split(" ", 1)[1].rpartition(" ")
            if name in POLICY_KEYWORDS:
                found.setdefault(name, set()).add(documented_type)
    return found


@pytest.mark.cosmosEmulator
class TestDatabasePolicyTyping(unittest.TestCase):

    def test_async_policy_annotations_match_sync(self):
        for method_name in METHODS:
            sync_annotations = _annotations(sync_database, method_name)
            async_annotations = _annotations(async_database, method_name)
            self.assertTrue(async_annotations, f"no policy keywords found on async {method_name}")
            for keyword, annotation in async_annotations.items():
                self.assertEqual(
                    sync_annotations[keyword],
                    annotation,
                    f"async DatabaseProxy.{method_name}({keyword}=...) is typed differently from the sync client",
                )

    def test_async_policy_docstring_types_match_sync(self):
        for method_name in METHODS:
            sync_types = _documented_types(sync_database, method_name)
            async_types = _documented_types(async_database, method_name)
            self.assertTrue(async_types, f"no documented policy keywords found on async {method_name}")
            for keyword, documented in async_types.items():
                self.assertEqual(
                    sync_types[keyword],
                    documented,
                    f"async DatabaseProxy.{method_name} documents {keyword} differently from the sync client",
                )


if __name__ == "__main__":
    unittest.main()
