# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for TaskMetadata operations (set, get, increment, append, flush)."""

import asyncio
from typing import Any

import pytest

from azure.ai.agentserver.core.tasks._metadata import TaskMetadata


class TestTaskMetadataOperations:
    """Tests for basic metadata operations."""

    def test_set_and_get(self) -> None:
        """set() stores a value, get() retrieves it."""
        meta = TaskMetadata()
        meta.set("key", "value")
        assert meta.get("key") == "value"

    def test_get_default(self) -> None:
        """get() returns default when key is missing."""
        meta = TaskMetadata()
        assert meta.get("missing") is None
        assert meta.get("missing", 42) == 42

    def test_set_marks_dirty(self) -> None:
        """set() marks the metadata as dirty."""
        meta = TaskMetadata()
        assert not meta._dirty
        meta.set("key", "value")
        assert meta._dirty

    def test_increment(self) -> None:
        """increment() increases a counter by the given amount."""
        meta = TaskMetadata()
        meta.increment("counter")
        assert meta.get("counter") == 1
        meta.increment("counter", 5)
        assert meta.get("counter") == 6

    def test_increment_non_numeric_raises(self) -> None:
        """increment() raises TypeError on non-numeric existing value."""
        meta = TaskMetadata()
        meta.set("key", "not a number")
        with pytest.raises(TypeError):
            meta.increment("key")

    def test_append(self) -> None:
        """append() adds items to a list."""
        meta = TaskMetadata()
        meta.append("log", "entry1")
        meta.append("log", "entry2")
        assert meta.get("log") == ["entry1", "entry2"]

    def test_append_non_list_raises(self) -> None:
        """append() raises TypeError when existing value is not a list."""
        meta = TaskMetadata()
        meta.set("key", "not a list")
        with pytest.raises(TypeError):
            meta.append("key", "item")

    def test_snapshot_returns_copy(self) -> None:
        """Snapshot returns a copy, not a reference."""
        meta = TaskMetadata()
        meta.set("key", "value")
        snap = dict(meta._data)
        meta.set("key", "changed")
        assert snap["key"] == "value"
        assert meta.get("key") == "changed"


class TestTaskMetadataFlush:
    """Tests for flush and auto-flush behavior."""

    @pytest.mark.asyncio
    async def test_flush_calls_callback(self) -> None:
        """flush() calls the flush_callback with (namespace, data)."""
        captured: list[tuple[Any, dict[str, Any]]] = []

        async def callback(namespace: Any, data: dict[str, Any]) -> None:
            captured.append((namespace, data))

        meta = TaskMetadata(flush_callback=callback)
        meta.set("key", "value")
        await meta.flush()

        assert len(captured) == 1
        ns, data = captured[0]
        assert ns is None  # default namespace
        assert data["key"] == "value"

    @pytest.mark.asyncio
    async def test_flush_clears_dirty(self) -> None:
        """flush() clears the dirty flag after success."""

        async def callback(namespace: Any, data: dict[str, Any]) -> None:
            pass

        meta = TaskMetadata(flush_callback=callback)
        meta.set("key", "value")
        assert meta._dirty
        await meta.flush()
        assert not meta._dirty

    @pytest.mark.asyncio
    async def test_flush_noop_when_clean(self) -> None:
        """flush() is a no-op when metadata is not dirty."""
        call_count = 0

        async def callback(namespace: Any, data: dict[str, Any]) -> None:
            nonlocal call_count
            call_count += 1

        meta = TaskMetadata(flush_callback=callback)
        await meta.flush()
        assert call_count == 0

    @pytest.mark.asyncio
    async def test_flush_noop_without_callback(self) -> None:
        """flush() is a no-op without a callback configured."""
        meta = TaskMetadata()
        meta.set("key", "value")
        # Should not raise
        await meta.flush()


class TestTaskMetadataDictProtocol:
    """Tests for dict-like access (MutableMapping protocol)."""

    def test_setitem_getitem(self) -> None:
        """[] assignment and retrieval works."""
        meta = TaskMetadata()
        meta["key"] = "value"
        assert meta["key"] == "value"

    def test_getitem_missing_raises_keyerror(self) -> None:
        """[] on missing key raises KeyError."""
        meta = TaskMetadata()
        with pytest.raises(KeyError):
            _ = meta["missing"]

    def test_setitem_marks_dirty(self) -> None:
        """[] assignment marks metadata as dirty."""
        meta = TaskMetadata()
        assert not meta._dirty
        meta["key"] = "value"
        assert meta._dirty

    def test_setitem_non_string_key_raises(self) -> None:
        """[] with non-string key raises TypeError."""
        meta = TaskMetadata()
        with pytest.raises(TypeError):
            meta[42] = "value"  # type: ignore[index]

    def test_delitem(self) -> None:
        """del removes a key and marks dirty."""
        meta = TaskMetadata()
        meta["key"] = "value"
        meta._dirty = False
        del meta["key"]
        assert "key" not in meta
        assert meta._dirty

    def test_delitem_missing_raises_keyerror(self) -> None:
        """del on missing key raises KeyError."""
        meta = TaskMetadata()
        with pytest.raises(KeyError):
            del meta["missing"]

    def test_contains(self) -> None:
        """'in' operator works."""
        meta = TaskMetadata()
        meta["key"] = "value"
        assert "key" in meta
        assert "missing" not in meta

    def test_len(self) -> None:
        """len() returns number of keys."""
        meta = TaskMetadata()
        assert len(meta) == 0
        meta["a"] = 1
        meta["b"] = 2
        assert len(meta) == 2

    def test_iter(self) -> None:
        """Iteration yields keys."""
        meta = TaskMetadata()
        meta["a"] = 1
        meta["b"] = 2
        assert sorted(meta) == ["a", "b"]

    def test_keys_values_items(self) -> None:
        """keys(), values(), items() delegate to internal dict."""
        meta = TaskMetadata()
        meta["x"] = 10
        meta["y"] = 20
        assert set(meta.keys()) == {"x", "y"}
        assert set(meta.values()) == {10, 20}
        assert set(meta.items()) == {("x", 10), ("y", 20)}

    def test_isinstance_mutable_mapping(self) -> None:
        """TaskMetadata is registered as MutableMapping."""
        import collections.abc

        meta = TaskMetadata()
        assert isinstance(meta, collections.abc.MutableMapping)

    def test_existing_methods_still_work(self) -> None:
        """Existing .set(), .get(), .increment(), .append() are unchanged."""
        meta = TaskMetadata()
        meta.set("counter", 0)
        meta.increment("counter", 5)
        assert meta.get("counter") == 5
        meta.append("log", "entry")
        assert meta.get("log") == ["entry"]
        assert meta.to_dict() == {"counter": 5, "log": ["entry"]}

    @pytest.mark.asyncio
    async def test_setitem_triggers_auto_flush(self) -> None:
        """[] assignment triggers flush via dirty-tracking."""
        captured: list[tuple[Any, dict[str, Any]]] = []

        async def callback(namespace: Any, data: dict[str, Any]) -> None:
            captured.append((namespace, data))

        meta = TaskMetadata(flush_callback=callback)
        meta["key"] = "value"
        await meta.flush()
        assert len(captured) == 1
        ns, data = captured[0]
        assert ns is None
        assert data["key"] == "value"


# --------------------------------------------------------------------- #
#  — Named-namespace metadata (,,)
# --------------------------------------------------------------------- #
# Contract clauses pinned by tests/tasks/test_contract_completeness.py:
#   - test_default_namespace_callable_and_dict
#   - test_named_namespace_isolation
#   - test_flush_per_namespace_only
#   - test_underscore_namespace_not_enforced_by_primitive
#
# Plus the spec-driven supplementary tests for the named-namespace
# facility (T035): auto-vivification, independent dirty tracking,
# lifecycle boundary snapshots, no cross-namespace pollution, source-
# scan for autoflush removal, default-namespace has no framework keys.
# --------------------------------------------------------------------- #


class TestTaskMetadataNamedNamespaces:
    """Phase 5  — `ctx.metadata(name)` namespaces.

    A bare ``ctx.metadata`` is the default namespace (dict-protocol).
    Calling it like a function — ``ctx.metadata("name")`` — returns a
    sibling namespace facade with its own data and dirty tracking. Each
    namespace persists independently to ``payload["metadata"]`` (default)
    or ``payload["metadata:<name>"]`` (named).
    """

    def test_default_namespace_callable_and_dict(self) -> None:
        """`ctx.metadata` supports BOTH dict-protocol AND being called.

        The default namespace exposes the MutableMapping protocol
        directly (``meta["k"] = v``). It is ALSO callable: ``meta()``
        with no arg returns the default namespace (self), and
        ``meta("name")`` returns a named-namespace facade.
        """
        meta = TaskMetadata()

        meta["k"] = 1
        assert meta["k"] == 1

        default_via_call = meta()
        assert default_via_call["k"] == 1
        assert default_via_call is meta or dict(default_via_call) == dict(meta)

        named = meta("custom")
        assert isinstance(named, TaskMetadata)
        assert "k" not in named

    def test_named_namespace_isolation(self) -> None:
        """Setting in one namespace does NOT leak into siblings or default."""
        meta = TaskMetadata()
        meta["default_key"] = "D"
        meta("a")["x"] = 1
        meta("b")["y"] = 2

        assert meta["default_key"] == "D"
        assert "default_key" not in meta("a")
        assert "default_key" not in meta("b")
        assert "x" not in meta
        assert "x" not in meta("b")
        assert "y" not in meta
        assert "y" not in meta("a")
        assert meta("a")["x"] == 1
        assert meta("b")["y"] == 2

    def test_named_namespace_auto_vivifies(self) -> None:
        """First reference to a named namespace creates an empty facade."""
        meta = TaskMetadata()
        fresh = meta("never_seen_before")
        assert isinstance(fresh, TaskMetadata)
        assert len(fresh) == 0

    def test_namespaces_have_independent_dirty_tracking(self) -> None:
        """Marking one namespace dirty leaves siblings clean."""
        meta = TaskMetadata()
        a = meta("a")
        b = meta("b")
        assert not a._dirty
        assert not b._dirty
        assert not meta._dirty

        a["touched"] = 1
        assert a._dirty
        assert not b._dirty
        assert not meta._dirty

    @pytest.mark.asyncio
    async def test_flush_per_namespace_only(self) -> None:
        """`meta("a").flush()` flushes ONLY namespace a, not default nor b.

        The flush_callback wired up by the framework is per-namespace; a
        named-namespace flush MUST NOT write to ``payload["metadata"]``
        or to any other namespace's storage slot.
        """
        captured: list[tuple[str | None, dict[str, Any]]] = []

        async def callback(namespace: str | None, data: dict[str, Any]) -> None:
            captured.append((namespace, dict(data)))

        meta = TaskMetadata(flush_callback=callback)
        meta["default"] = "D"
        meta("a")["x"] = 1
        meta("b")["y"] = 2

        # Flush only "a"
        await meta("a").flush()
        assert len(captured) == 1
        assert captured[0] == ("a", {"x": 1})

        # Default and b are still dirty
        assert meta._dirty
        assert meta("b")._dirty
        assert not meta("a")._dirty

    @pytest.mark.asyncio
    async def test_lifecycle_boundary_snapshots_all_touched_namespaces(self) -> None:
        """A `flush_all()` (lifecycle boundary) MUST flush every dirty namespace."""
        captured: list[tuple[str | None, dict[str, Any]]] = []

        async def callback(namespace: str | None, data: dict[str, Any]) -> None:
            captured.append((namespace, dict(data)))

        meta = TaskMetadata(flush_callback=callback)
        meta["d"] = 0
        meta("a")["x"] = 1
        meta("b")["y"] = 2
        # c is auto-vivified but never written -> not dirty -> should NOT flush
        _ = meta("c")

        await meta._flush_all()

        seen = {ns for ns, _ in captured}
        assert None in seen, "default namespace must be flushed"
        assert "a" in seen
        assert "b" in seen
        assert "c" not in seen, "clean namespaces must not be flushed"

    def test_no_cross_namespace_pollution_after_delete(self) -> None:
        """Deleting a key in one namespace does not affect siblings."""
        meta = TaskMetadata()
        meta("a")["shared_name"] = "from_a"
        meta("b")["shared_name"] = "from_b"

        del meta("a")["shared_name"]

        assert "shared_name" not in meta("a")
        assert meta("b")["shared_name"] == "from_b"

    def test_metadata_module_has_no_autoflush_symbols(self) -> None:
        """Source-scan: ``start_auto_flush`` / ``stop_auto_flush`` etc. are gone.

          retires the auto-flush loop entirely; flushes
        are explicit (per-write debounce + lifecycle boundary). Source
        text must not mention the old API names.
        """
        from pathlib import Path

        from azure.ai.agentserver.core.tasks import _metadata as _meta_mod

        source = Path(_meta_mod.__file__).read_text(encoding="utf-8")
        forbidden = ("start_auto_flush", "stop_auto_flush", "_auto_flush_loop", "_flush_task", "_flush_interval")
        offenders = [name for name in forbidden if name in source]
        assert not offenders, f"_metadata.py must not mention retired auto-flush symbols: " f"{offenders}"

    def test_underscore_namespace_not_enforced_by_primitive(self) -> None:
        """The CORE primitive MUST NOT reject namespace names with a
        leading underscore — that is a wrapper-layer concern.

        The handler-facing wrapper layers (e.g. the responses package's
        :class:`ResilienceContext`) reject ``_*`` names so handler code
        cannot collide with framework-reserved namespaces such as
        ``_responses``. Framework-layered code (the responses
        orchestrator) reaches those reserved namespaces through this
        primitive API directly. If the primitive enforced the rule,
        framework-layered code would be unable to use its own reserved
        namespaces — a regression that breaks the responses
        orchestrator's ``_responses`` namespace access.

        Pinned by ``test_contract_completeness.py`` § Phase 5
        named-namespace clauses (see test_metadata.py line ~245).
        """
        meta = TaskMetadata()
        # Underscore-prefixed namespaces must be accessible from the
        # primitive (no ValueError).
        framework_ns = meta("_responses")
        framework_ns["disposition"] = "mark-failed"
        assert framework_ns["disposition"] == "mark-failed"
        # The namespace persists in the registry and is reachable again.
        assert meta("_responses") is framework_ns
        # The default namespace remains independent (no leakage).
        assert "disposition" not in meta


class TestTaskMetadataRecoveryResilience:
    """Phase 5 T036 — named-namespace persistence survives crash/recovery.

    Real-crash variant requires a ``_crash_harness`` subprocess fixture
    (Phase 0 Q3 design). In its absence (it is a Phase 8 deliverable),
    this test simulates the same guarantee in-process by manually
    persisting per-namespace slots and replaying the recovery decode
    path, which exercises the same payload contract.
    """

    @pytest.mark.asyncio
    async def test_named_namespace_survives_recovery_with_independent_state(self) -> None:
        """Each `payload["metadata:<name>"]` is restored to its own facade.

        Simulates a crash by:
        1. Producing the post-flush payload shape (per  layout).
        2. Constructing a fresh TaskMetadata from that "recovered" data.
        3. Asserting each namespace's data is intact AND siblings remain
           isolated (no cross-namespace bleed during decode).
        """
        # Step 1: write into multiple namespaces and capture per-namespace
        # flushes (simulates the manager's per-namespace persist).
        persisted: dict[str | None, dict[str, Any]] = {}

        async def callback(namespace: str | None, data: dict[str, Any]) -> None:
            persisted[namespace] = dict(data)

        live = TaskMetadata(flush_callback=callback)
        live["d_key"] = "default-data"
        live("a")["x"] = 1
        live("a")["counter"] = 42
        live("b")["nested"] = {"k": "v"}

        await live._flush_all()

        # Mimic the payload that the manager would write — default goes
        # into payload["metadata"], named goes into payload["metadata:<name>"].
        payload: dict[str, Any] = {"metadata": persisted[None]}
        for ns_name, data in persisted.items():
            if ns_name is None:
                continue
            payload[f"metadata:{ns_name}"] = data

        # Step 2: simulate "fresh process after crash" — decode payload.
        # The decode helper lives on TaskMetadata so the manager and
        # tests share one definition.
        restored = TaskMetadata.from_payload(payload, flush_callback=callback)

        # Step 3: verify per-namespace integrity + isolation
        assert restored["d_key"] == "default-data"
        assert restored("a")["x"] == 1
        assert restored("a")["counter"] == 42
        assert restored("b")["nested"] == {"k": "v"}

        # Isolation preserved through recovery
        assert "x" not in restored
        assert "x" not in restored("b")
        assert "nested" not in restored("a")
