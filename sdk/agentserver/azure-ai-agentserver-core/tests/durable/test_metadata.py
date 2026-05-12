# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for TaskMetadata operations (set, get, increment, append, flush)."""

import asyncio
from typing import Any

import pytest

from azure.ai.agentserver.core.durable._metadata import TaskMetadata


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
        """flush() calls the flush_callback with current data."""
        captured: list[dict[str, Any]] = []

        async def callback(data: dict[str, Any]) -> None:
            captured.append(data)

        meta = TaskMetadata(flush_callback=callback)
        meta.set("key", "value")
        await meta.flush()

        assert len(captured) == 1
        assert captured[0]["key"] == "value"

    @pytest.mark.asyncio
    async def test_flush_clears_dirty(self) -> None:
        """flush() clears the dirty flag after success."""

        async def callback(data: dict[str, Any]) -> None:
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

        async def callback(data: dict[str, Any]) -> None:
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

    @pytest.mark.asyncio
    async def test_stop_auto_flush_final_flush(self) -> None:
        """stop_auto_flush() does a final flush before stopping."""
        captured: list[dict[str, Any]] = []

        async def callback(data: dict[str, Any]) -> None:
            captured.append(data)

        meta = TaskMetadata(flush_callback=callback, flush_interval=100)
        meta.start_auto_flush()
        meta.set("key", "value")
        await meta.stop_auto_flush()

        assert len(captured) == 1
        assert captured[0]["key"] == "value"


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
        captured: list[dict[str, Any]] = []

        async def callback(data: dict[str, Any]) -> None:
            captured.append(data)

        meta = TaskMetadata(flush_callback=callback)
        meta["key"] = "value"
        await meta.flush()
        assert len(captured) == 1
        assert captured[0]["key"] == "value"
