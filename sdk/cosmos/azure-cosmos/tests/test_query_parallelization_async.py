# The MIT License (MIT)
# Copyright (c) 2026 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Unit tests for async query parallelization (concurrent document producer execution).

These tests use mocks to validate concurrency behavior without requiring a live Cosmos DB account.
"""

import asyncio
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from azure.cosmos._execution_context.aio._concurrent_helpers import (
    _resolve_max_degree,
    _resolve_max_buffered,
    concurrent_peek_producers,
    concurrent_drain_producers,
)

# Lazy-import aggregators to avoid circular import issues when running tests in isolation.
# The circular chain is: base_execution_context -> aio.__init__ -> ContainerProxy ->
#   CosmosClientConnection -> execution_dispatcher -> aggregators -> base_execution_context
# We only import them inside test functions using importlib or when all modules are already loaded.

def _ensure_cosmos_aio_loaded():
    """Ensure the full azure.cosmos.aio import chain is loaded before importing internals."""
    import azure.cosmos.aio  # noqa: F401 - triggers the full module loading chain

def _import_multi_aggregator():
    """Lazily import _MultiExecutionContextAggregator."""
    _ensure_cosmos_aio_loaded()
    from azure.cosmos._execution_context.aio.multi_execution_aggregator import _MultiExecutionContextAggregator
    return _MultiExecutionContextAggregator

def _import_non_streaming_aggregator():
    """Lazily import _NonStreamingOrderByContextAggregator."""
    _ensure_cosmos_aio_loaded()
    from azure.cosmos._execution_context.aio.non_streaming_order_by_aggregator import (
        _NonStreamingOrderByContextAggregator
    )
    return _NonStreamingOrderByContextAggregator


# ---------------------------------------------------------------------------
# _resolve_max_degree tests
# ---------------------------------------------------------------------------

class TestResolveMaxDegree:
    """Tests for the _resolve_max_degree helper."""

    def test_none_returns_serial(self):
        assert _resolve_max_degree(None, 10) == 0

    def test_zero_returns_serial(self):
        assert _resolve_max_degree(0, 10) == 0

    def test_positive_returns_value(self):
        assert _resolve_max_degree(4, 10) == 4

    def test_positive_exceeding_partitions_returns_value(self):
        # The user explicitly asked for 100, we respect that
        assert _resolve_max_degree(100, 5) == 100

    def test_negative_one_auto(self):
        result = _resolve_max_degree(-1, 20)
        assert result > 0
        assert result <= 32  # cap

    def test_auto_respects_partition_count(self):
        # With 2 partitions, auto should return at most 2
        result = _resolve_max_degree(-1, 2)
        assert result <= 2

    def test_auto_caps_at_32(self):
        result = _resolve_max_degree(-1, 1000)
        assert result <= 32


# ---------------------------------------------------------------------------
# _resolve_max_buffered tests
# ---------------------------------------------------------------------------

class TestResolveMaxBuffered:
    """Tests for the _resolve_max_buffered helper."""

    def test_none_returns_zero(self):
        assert _resolve_max_buffered(None, 4) == 0

    def test_zero_returns_zero(self):
        assert _resolve_max_buffered(0, 4) == 0

    def test_positive_returns_value(self):
        assert _resolve_max_buffered(500, 4) == 500

    def test_negative_one_auto(self):
        result = _resolve_max_buffered(-1, 4)
        assert result == 400  # 4 * 100

    def test_auto_with_zero_concurrency(self):
        result = _resolve_max_buffered(-1, 0)
        assert result == 0

    def test_auto_minimum_100(self):
        result = _resolve_max_buffered(-1, 1)
        assert result >= 100


# ---------------------------------------------------------------------------
# concurrent_peek_producers tests
# ---------------------------------------------------------------------------

class TestConcurrentPeekProducers:
    """Tests for concurrent_peek_producers."""

    @pytest.mark.asyncio
    async def test_all_producers_peek_successfully(self):
        """All producers should be peeked and returned."""
        producers = []
        for i in range(5):
            p = MagicMock()
            p.peek = AsyncMock(return_value={"id": str(i)})
            producers.append(p)

        semaphore = asyncio.Semaphore(3)
        peeked, gone_errors = await concurrent_peek_producers(producers, semaphore)

        assert len(peeked) == 5
        assert len(gone_errors) == 0
        for p in producers:
            p.peek.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_empty_producers_skipped(self):
        """Producers that raise StopAsyncIteration should be skipped."""
        p1 = MagicMock()
        p1.peek = AsyncMock(return_value={"id": "1"})
        p2 = MagicMock()
        p2.peek = AsyncMock(side_effect=StopAsyncIteration)
        p3 = MagicMock()
        p3.peek = AsyncMock(return_value={"id": "3"})

        semaphore = asyncio.Semaphore(3)
        peeked, gone_errors = await concurrent_peek_producers([p1, p2, p3], semaphore)

        assert len(peeked) == 2
        assert len(gone_errors) == 0

    @pytest.mark.asyncio
    async def test_partition_gone_reported(self):
        """Partition-gone errors should be collected in gone_errors."""
        from azure.cosmos.exceptions import CosmosHttpResponseError

        p1 = MagicMock()
        p1.peek = AsyncMock(return_value={"id": "1"})

        gone_error = CosmosHttpResponseError(status_code=410, message="Gone")
        gone_error.sub_status_code = 1002  # PartitionKeyRangeGone

        p2 = MagicMock()
        p2.peek = AsyncMock(side_effect=gone_error)

        semaphore = asyncio.Semaphore(3)

        with patch("azure.cosmos.exceptions._partition_range_is_gone", return_value=True):
            peeked, gone_errors = await concurrent_peek_producers([p1, p2], semaphore)

        assert len(peeked) == 1
        assert len(gone_errors) == 1

    @pytest.mark.asyncio
    async def test_other_errors_raised(self):
        """Non-partition-gone errors should be raised immediately."""
        from azure.cosmos.exceptions import CosmosHttpResponseError

        p1 = MagicMock()
        p1.peek = AsyncMock(side_effect=CosmosHttpResponseError(status_code=500, message="Server Error"))

        semaphore = asyncio.Semaphore(3)

        with patch("azure.cosmos.exceptions._partition_range_is_gone", return_value=False):
            with pytest.raises(CosmosHttpResponseError):
                await concurrent_peek_producers([p1], semaphore)

    @pytest.mark.asyncio
    async def test_concurrency_bounded_by_semaphore(self):
        """Verify that concurrency does not exceed the semaphore limit."""
        max_concurrent = 0
        current_concurrent = 0
        lock = asyncio.Lock()

        async def tracked_peek():
            nonlocal max_concurrent, current_concurrent
            async with lock:
                current_concurrent += 1
                max_concurrent = max(max_concurrent, current_concurrent)
            await asyncio.sleep(0.01)  # simulate I/O
            async with lock:
                current_concurrent -= 1
            return {"id": "ok"}

        producers = []
        for _ in range(10):
            p = MagicMock()
            p.peek = tracked_peek
            producers.append(p)

        semaphore = asyncio.Semaphore(3)
        peeked, _ = await concurrent_peek_producers(producers, semaphore)

        assert len(peeked) == 10
        assert max_concurrent <= 3


# ---------------------------------------------------------------------------
# concurrent_drain_producers tests
# ---------------------------------------------------------------------------

class TestConcurrentDrainProducers:
    """Tests for concurrent_drain_producers."""

    @pytest.mark.asyncio
    async def test_drain_collects_all_results(self):
        """All items from all producers should be collected."""
        from collections import deque

        producers = []
        for i in range(3):
            p = MagicMock()
            p._cur_item = {"id": f"peek_{i}"}
            p.peek = AsyncMock(return_value=p._cur_item)
            # Simulate internal buffer with 2 items
            p._ex_context = MagicMock()
            p._ex_context._buffer = deque([{"id": f"buf_{i}_0"}, {"id": f"buf_{i}_1"}])
            p._ex_context.__anext__ = AsyncMock(side_effect=StopAsyncIteration)
            producers.append(p)

        semaphore = asyncio.Semaphore(2)
        results, gone_errors = await concurrent_drain_producers(producers, semaphore)

        assert len(gone_errors) == 0
        # Each producer: 1 peek + 2 buffer = 3 items, total = 9
        assert len(results) == 9


# ---------------------------------------------------------------------------
# MultiExecutionContextAggregator parallelization tests
# ---------------------------------------------------------------------------

class TestMultiExecutionAggregatorParallel:
    """Tests for parallel initialization in _MultiExecutionContextAggregator."""

    @pytest.mark.asyncio
    async def test_serial_mode_with_zero_parallelism(self):
        """With max_degree_of_parallelism=0, producers should be peeked sequentially."""
        _MultiExecutionContextAggregator = _import_multi_aggregator()

        # Create mock client and query info
        client = MagicMock()
        client._routing_map_provider = MagicMock()
        client._routing_map_provider.get_overlapping_ranges = AsyncMock(return_value=[
            {"id": "0", "minInclusive": "", "maxExclusive": "05C1"},
            {"id": "1", "minInclusive": "05C1", "maxExclusive": "FF"},
        ])

        query_ex_info = MagicMock()
        query_ex_info.get_order_by.return_value = None
        query_ex_info.get_rewritten_query.return_value = None
        query_ex_info.get_query_ranges.return_value = [{"min": "", "max": "FF", "isMinInclusive": True,
                                                         "isMaxInclusive": False}]

        options = {"maxDegreeOfParallelism": 0}

        aggregator = _MultiExecutionContextAggregator(
            client, "/dbs/db/colls/coll", "SELECT * FROM c", options,
            query_ex_info, None, None
        )

        # Patch _createTargetPartitionQueryExecutionContext to return mock producers
        mock_producers = []
        for i in range(2):
            mp = MagicMock()
            mp.peek = AsyncMock(return_value={"id": str(i)})
            target_range = {"id": str(i), "minInclusive": str(i), "maxExclusive": str(i + 1)}
            mp._partition_key_target_range = target_range
            mp.get_target_range = MagicMock(return_value=target_range)
            mock_producers.append(mp)

        with patch.object(aggregator, '_createTargetPartitionQueryExecutionContext',
                          side_effect=mock_producers):
            await aggregator._configure_partition_ranges()

        # Both producers should have been peeked
        for mp in mock_producers:
            mp.peek.assert_awaited_once()

        assert aggregator._orderByPQ.size() == 2

    @pytest.mark.asyncio
    async def test_parallel_mode_with_positive_parallelism(self):
        """With max_degree_of_parallelism>0, concurrent_peek_producers should be used."""
        _MultiExecutionContextAggregator = _import_multi_aggregator()

        client = MagicMock()
        client._routing_map_provider = MagicMock()
        client._routing_map_provider.get_overlapping_ranges = AsyncMock(return_value=[
            {"id": "0", "minInclusive": "", "maxExclusive": "05C1"},
            {"id": "1", "minInclusive": "05C1", "maxExclusive": "AA"},
            {"id": "2", "minInclusive": "AA", "maxExclusive": "FF"},
        ])

        query_ex_info = MagicMock()
        query_ex_info.get_order_by.return_value = None
        query_ex_info.get_rewritten_query.return_value = None
        query_ex_info.get_query_ranges.return_value = [{"min": "", "max": "FF", "isMinInclusive": True,
                                                         "isMaxInclusive": False}]

        options = {"maxDegreeOfParallelism": 2}

        aggregator = _MultiExecutionContextAggregator(
            client, "/dbs/db/colls/coll", "SELECT * FROM c", options,
            query_ex_info, None, None
        )

        mock_producers = []
        for i in range(3):
            mp = MagicMock()
            mp.peek = AsyncMock(return_value={"id": str(i)})
            target_range = {"id": str(i), "minInclusive": str(i), "maxExclusive": str(i + 1)}
            mp._partition_key_target_range = target_range
            mp.get_target_range = MagicMock(return_value=target_range)
            mock_producers.append(mp)

        with patch.object(aggregator, '_createTargetPartitionQueryExecutionContext',
                          side_effect=mock_producers):
            with patch(
                "azure.cosmos._execution_context.aio.multi_execution_aggregator.concurrent_peek_producers",
                new_callable=AsyncMock,
                return_value=(mock_producers, [])
            ) as mock_concurrent_peek:
                await aggregator._configure_partition_ranges()

                # Verify concurrent_peek_producers was called
                mock_concurrent_peek.assert_awaited_once()

        assert aggregator._orderByPQ.size() == 3


# ---------------------------------------------------------------------------
# NonStreamingOrderByContextAggregator parallelization tests
# ---------------------------------------------------------------------------

class TestNonStreamingOrderByParallel:
    """Tests for parallel drain in _NonStreamingOrderByContextAggregator."""

    @pytest.mark.asyncio
    async def test_serial_drain_with_zero_parallelism(self):
        """With max_degree_of_parallelism=0, drain should be sequential."""
        _NonStreamingOrderByContextAggregator = _import_non_streaming_aggregator()

        client = MagicMock()
        client._routing_map_provider = MagicMock()
        client._routing_map_provider.get_overlapping_ranges = AsyncMock(return_value=[
            {"id": "0", "minInclusive": "", "maxExclusive": "FF"},
        ])

        query_ex_info = MagicMock()
        query_ex_info.get_order_by.return_value = [{"item": "Ascending"}]
        query_ex_info.get_rewritten_query.return_value = None
        query_ex_info.get_query_ranges.return_value = [{"min": "", "max": "FF", "isMinInclusive": True,
                                                         "isMaxInclusive": False}]
        query_ex_info.get_top.return_value = 10
        query_ex_info.get_limit.return_value = 0
        query_ex_info.get_offset.return_value = 0

        options = {"maxDegreeOfParallelism": 0}

        aggregator = _NonStreamingOrderByContextAggregator(
            client, "/dbs/db/colls/coll", "SELECT * FROM c", options,
            query_ex_info, None, None
        )

        # Create a mock producer using a proper async iterator pattern
        items = [{"id": "a", "orderByItems": [{"item": 1}]},
                 {"id": "b", "orderByItems": [{"item": 2}]},
                 {"id": "c", "orderByItems": [{"item": 3}]}]

        class MockDocProducer:
            def __init__(self, items_list):
                self._items = list(items_list)
                self._index = 0
                self._cur_item = None
                self._partition_key_target_range = {"id": "0", "minInclusive": "", "maxExclusive": "FF"}

            def get_target_range(self):
                return self._partition_key_target_range

            async def peek(self):
                if self._cur_item is not None:
                    return self._cur_item
                if self._index < len(self._items):
                    self._cur_item = self._items[self._index]
                    return self._cur_item
                raise StopAsyncIteration

            async def __anext__(self):
                if self._cur_item is not None:
                    res = self._cur_item
                    self._cur_item = None
                    self._index += 1
                    return res
                if self._index < len(self._items):
                    res = self._items[self._index]
                    self._index += 1
                    return res
                raise StopAsyncIteration

        mp = MockDocProducer(items)

        with patch.object(aggregator, '_createTargetPartitionQueryExecutionContext', return_value=mp):
            await aggregator._configure_partition_ranges()

        assert aggregator._orderByPQ.size() == 3


# ---------------------------------------------------------------------------
# Options threading tests
# ---------------------------------------------------------------------------

class TestOptionsThreading:
    """Test that new kwargs properly flow through the options pipeline."""

    def test_base_build_options_includes_new_keys(self):
        """Verify build_options extracts max_degree_of_parallelism and max_buffered_item_count."""
        from azure.cosmos._base import build_options

        kwargs = {
            "max_degree_of_parallelism": 4,
            "max_buffered_item_count": 500,
        }
        options = build_options(kwargs)
        assert options["maxDegreeOfParallelism"] == 4
        assert options["maxBufferedItemCount"] == 500
        # kwargs should have been consumed
        assert "max_degree_of_parallelism" not in kwargs
        assert "max_buffered_item_count" not in kwargs

    def test_base_build_options_without_new_keys(self):
        """Verify build_options works fine without the new kwargs."""
        from azure.cosmos._base import build_options

        kwargs = {"max_item_count": 10}
        options = build_options(kwargs)
        assert "maxDegreeOfParallelism" not in options
        assert "maxBufferedItemCount" not in options
        assert options["maxItemCount"] == 10
