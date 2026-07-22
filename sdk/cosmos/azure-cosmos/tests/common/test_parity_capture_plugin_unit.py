# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for parity-capture plugin registration safety."""
from __future__ import annotations

import importlib.util
import inspect
import pathlib
import sys
import unittest


_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_PLUGIN_PATH = _REPO_ROOT / "tests" / "common" / "parity_capture_plugin.py"


# Load the plugin straight from its file instead of importing it as a package, so
# these tests exercise the real plugin module without pytest having to register it.
def _load_plugin():
    mod_name = "_parity_capture_plugin_under_test"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, str(_PLUGIN_PATH))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


# These tests guard the parity-capture plugin -- the pytest add-on that records each
# SDK operation's request and response so the parity reporter can compare the
# core-python path against the rust path. The plugin is only used when auditing the
# migration and is off during normal test runs. Without these checks a newly migrated
# operation could be left out of the plugin's registry, or the plugin could turn a
# sync method into a coroutine or emit a false difference, and the audit would
# silently miss or misreport that operation.
class PluginRegistryTests(unittest.TestCase):
    """The plugin must stay reusable across migrated CRUD operations."""

    def setUp(self):
        self.plugin = _load_plugin()

    def test_registry_contains_migrated_crud_ops(self):
        """All migrated operations must be registered for sync + aio capture."""
        # Without this, a migrated operation (e.g. query_items) could be missing from
        # the registry and its calls would never be captured for the audit.
        registry = self.plugin._OP_REGISTRY  # noqa: SLF001
        for op in (
            "create_item",
            "delete_item",
            "read_item",
            "upsert_item",
            "replace_item",
            "patch_item",
            "query_items",
            "read_all_items",
            "read_feed_ranges",
            "feed_range_from_partition_key",
        ):
            self.assertIn(op, registry)
            self.assertIn("sync", registry[op])
            self.assertIn("aio", registry[op])
            self.assertTrue(callable(registry[op]["sync"]))
            self.assertTrue(callable(registry[op]["aio"]))

    def test_query_items_aio_patch_preserves_non_awaitable_signature(self):
        """The aio query_items target is sync-shaped and must stay non-coroutine after patching."""
        # The aio query_items entry point returns an async iterable but is not itself a
        # coroutine. Without this, the capture patch could wrap it as a coroutine and
        # break every async query_items caller under audit.
        module, class_name, method_name = self.plugin._aio_query_items_target()  # noqa: SLF001
        cls = getattr(module, class_name)
        original = getattr(cls, method_name)
        self.assertFalse(inspect.iscoroutinefunction(original))
        try:
            self.plugin._install_patches("query_items")  # noqa: SLF001
            patched = getattr(cls, method_name)
            self.assertFalse(inspect.iscoroutinefunction(patched))
        finally:
            self.plugin._revert_patches()  # noqa: SLF001

    def test_read_feed_ranges_aio_patch_preserves_non_awaitable_signature(self):
        """The aio read_feed_ranges target is sync-shaped and must stay non-coroutine after patching."""
        # Same guard for aio read_feed_ranges: the patch must not turn a non-coroutine
        # into a coroutine, or async read_feed_ranges would break under audit.
        module, class_name, method_name = self.plugin._aio_read_feed_ranges_target()  # noqa: SLF001
        cls = getattr(module, class_name)
        original = getattr(cls, method_name)
        self.assertFalse(inspect.iscoroutinefunction(original))
        try:
            self.plugin._install_patches("read_feed_ranges")  # noqa: SLF001
            patched = getattr(cls, method_name)
            self.assertFalse(inspect.iscoroutinefunction(patched))
        finally:
            self.plugin._revert_patches()  # noqa: SLF001

    def test_read_all_items_aio_patch_preserves_non_awaitable_signature(self):
        """The aio read_all_items target is sync-shaped and must stay non-coroutine after patching."""
        module, class_name, method_name = self.plugin._aio_read_all_items_target()  # noqa: SLF001
        cls = getattr(module, class_name)
        original = getattr(cls, method_name)
        self.assertFalse(inspect.iscoroutinefunction(original))
        try:
            self.plugin._install_patches("read_all_items")  # noqa: SLF001
            patched = getattr(cls, method_name)
            self.assertFalse(inspect.iscoroutinefunction(patched))
        finally:
            self.plugin._revert_patches()  # noqa: SLF001

    def test_repr_address_is_normalized_for_capture_payloads(self):
        """Address-bearing repr strings are normalized to avoid false diffs."""
        # An object's text form carries a process-local memory address ("at 0x...") that
        # changes every run. Without normalizing it, two identical results would look
        # different and the parity report would show a false diff.

        class _Dummy:
            def __repr__(self):
                return "<Dummy object at 0x1234ABCD>"

        normalized = self.plugin._coerce_json_safe(_Dummy())  # noqa: SLF001
        self.assertEqual(normalized, "<Dummy object>")

    def test_execution_evidence_uses_binding_counter_delta(self):
        """A Rust-selected client must prove that the binding counter moved."""
        original = self.plugin._rust_operation_count  # noqa: SLF001
        original_fallback = self.plugin._rust_fallback_count  # noqa: SLF001
        try:
            self.plugin._rust_operation_count = lambda: 12  # noqa: SLF001
            self.plugin._rust_fallback_count = lambda: 0  # noqa: SLF001
            evidence = self.plugin._execution_evidence(10, 0)  # noqa: SLF001
        finally:
            self.plugin._rust_operation_count = original  # noqa: SLF001
            self.plugin._rust_fallback_count = original_fallback  # noqa: SLF001
        self.assertEqual(evidence["executed_engine"], "rust")
        self.assertEqual(evidence["rust_operation_delta"], 2)

    def test_result_headers_prefer_public_aggregate(self):
        """List/read-many captures must use the result's aggregate headers."""

        class _Result:
            def get_response_headers(self):
                return {"x-ms-request-charge": "4.5"}

        class _Container:
            client_connection = type(
                "_Connection",
                (),
                {"last_response_headers": {"x-ms-request-charge": "1.0"}},
            )()

        headers = self.plugin._snapshot_result_headers(  # noqa: SLF001
            _Result(), _Container()
        )
        self.assertEqual(headers, {"x-ms-request-charge": "4.5"})

    def test_execution_evidence_rejects_attempt_then_fallback(self):
        """Entering Rust and then retrying in Python is not Rust execution parity."""
        original_count = self.plugin._rust_operation_count  # noqa: SLF001
        original_fallback = self.plugin._rust_fallback_count  # noqa: SLF001
        try:
            self.plugin._rust_operation_count = lambda: 12  # noqa: SLF001
            self.plugin._rust_fallback_count = lambda: 4  # noqa: SLF001
            evidence = self.plugin._execution_evidence(10, 3)  # noqa: SLF001
        finally:
            self.plugin._rust_operation_count = original_count  # noqa: SLF001
            self.plugin._rust_fallback_count = original_fallback  # noqa: SLF001
        self.assertEqual(evidence["executed_engine"], "core-python")
        self.assertEqual(evidence["rust_fallback_delta"], 1)


if __name__ == "__main__":
    unittest.main()
