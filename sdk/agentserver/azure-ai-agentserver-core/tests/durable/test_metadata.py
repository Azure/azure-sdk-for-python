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
