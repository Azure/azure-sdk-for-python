# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Structural gate: public container methods never touch backend selection.

Architecture invariant under test: ``ContainerProxy`` (sync and async) must
not inspect ``_backend``, import or call a ``can_use_rust_backend_*`` gate,
import or call a ``try_*_with_rust_backend`` executor, or otherwise branch on
Rust-vs-legacy for the throughput (``get_throughput`` / ``replace_throughput``)
and feed-range (``read_feed_ranges`` / ``feed_range_from_partition_key`` /
``is_feed_range_subset``) operations. Those concerns now live behind the
``azure.cosmos._helpers.throughput_helper`` / ``azure.cosmos._helpers.feed_range_helper``
family coordinators, which ``container.py`` / ``aio/_container.py`` call
without knowing which engine served the request.

This is a static, source-level check (parses the two files as text/AST) so it
catches a regression the moment the forbidden pattern is reintroduced, without
needing a live connection, the compiled rust binding, or an emulator.
"""
from __future__ import annotations

import ast
import inspect
import pathlib
import unittest

from azure.cosmos import container as sync_container_module
from azure.cosmos.aio import _container as async_container_module

#: Substrings that must never appear in ``container.py`` / ``aio/_container.py``.
#: Each names a symptom of the anti-pattern the audit flagged: reading the raw
#: ``_backend`` attribute, naming a Rust routing gate/executor, or the bare
#: identifier a case-insensitive "Rust" match would catch in code (not prose).
#:
#: There are no offer ``try_*_with_rust_backend`` entries here because those
#: executors no longer exist: engine selection for the offer operations runs
#: through ``CosmosBackend.run_operation`` like every other operation, so there
#: is no second executor for a proxy to reach for.
_FORBIDDEN_SUBSTRINGS = (
    'getattr(self.client_connection, "_backend"',
    "getattr(self.client_connection, '_backend'",
    "can_use_rust_backend_for_read_offer",
    "can_use_rust_backend_for_replace_throughput",
    "can_use_rust_backend_for_read_feed_ranges",
    "can_use_rust_backend_for_feed_range_from_partition_key",
    "can_use_rust_backend_for_is_feed_range_subset",
    "try_read_feed_ranges_with_rust_backend",
    "try_feed_range_from_partition_key_with_rust_backend",
    "try_is_feed_range_subset_with_rust_backend",
)

#: The five public methods issue 1 covers, by name, per module.
_THROUGHPUT_AND_FEED_RANGE_METHODS = (
    "get_throughput",
    "replace_throughput",
    "read_feed_ranges",
    "feed_range_from_partition_key",
    "is_feed_range_subset",
)


def _read_source(module) -> str:
    """Read the source file for a loaded container module."""
    return pathlib.Path(inspect.getfile(module)).read_text(encoding="utf-8")


def _container_class(tree: ast.AST):
    """Return the ``ContainerProxy`` class from a parsed module."""
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "ContainerProxy":
            return node
    raise AssertionError("ContainerProxy class not found")


def _method_source(tree: ast.AST, source: str, method_name: str) -> str:
    """Return one public container method's source text."""
    class_node = _container_class(tree)
    for node in class_node.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name:
            lines = source.splitlines(keepends=True)
            start = node.lineno - 1
            end = getattr(node, "end_lineno", node.lineno)
            return "".join(lines[start:end])
    raise AssertionError("ContainerProxy.{} not found".format(method_name))


class _NoRustRoutingInContainerBase:
    """Shared checks parameterised by module; see the sync/async subclasses."""

    module = None  # set by subclass

    def _source(self) -> str:
        """Return the source of the container module the subclass points at."""
        return _read_source(self.module)

    def test_module_source_has_no_forbidden_backend_inspection_or_rust_naming(self):
        """Prove container modules contain no direct implementation checks."""
        source = self._source()
        hits = [needle for needle in _FORBIDDEN_SUBSTRINGS if needle in source]
        self.assertEqual(
            hits, [],
            "{} contains forbidden Rust-routing patterns: {}. Throughput and "
            "feed-range backend selection must live behind "
            "azure.cosmos._helpers.throughput_helper / "
            "azure.cosmos._helpers.feed_range_helper, not in the public "
            "container methods.".format(self.module.__name__, hits),
        )

    def test_throughput_and_feed_range_methods_do_not_reference_backend_attribute(self):
        """Each of the five public methods, read individually by source, never
        reads ``self.client_connection._backend`` (however spelled)."""
        source = self._source()
        tree = ast.parse(source, filename=inspect.getfile(self.module))
        violations = []
        for method_name in _THROUGHPUT_AND_FEED_RANGE_METHODS:
            method_source = _method_source(tree, source, method_name)
            if "_backend" in method_source:
                violations.append(method_name)
        self.assertEqual(
            violations, [],
            "{}: these methods still reference `_backend` directly: {}".format(
                self.module.__name__, violations
            ),
        )

    def test_throughput_and_feed_range_methods_do_not_name_rust(self):
        """Each of the five public methods, read individually by source, never
        mentions "rust" (case-insensitive) -- unlike a whole-file scan, this
        does not false-positive on unrelated architecture comments elsewhere
        in the module (e.g. on the item-operation methods, which legitimately
        route through ``ItemHelper`` / ``pick_backend``)."""
        source = self._source()
        tree = ast.parse(source, filename=inspect.getfile(self.module))
        violations = []
        for method_name in _THROUGHPUT_AND_FEED_RANGE_METHODS:
            method_source = _method_source(tree, source, method_name)
            if "rust" in method_source.lower():
                violations.append(method_name)
        self.assertEqual(
            violations, [],
            "{}: these methods still name Rust: {}".format(self.module.__name__, violations),
        )


class TestSyncContainerHasNoRustRouting(_NoRustRoutingInContainerBase, unittest.TestCase):
    """Apply source checks to the synchronous container API."""
    module = sync_container_module


class TestAsyncContainerHasNoRustRouting(_NoRustRoutingInContainerBase, unittest.TestCase):
    """Apply source checks to the asynchronous container API."""
    module = async_container_module


if __name__ == "__main__":
    unittest.main()
