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
    concurrent_peek_producers,
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

    @pytest.mark.parametrize("bad_value", [-2, -5, -100])
    def test_invalid_negative_raises(self, bad_value):
        with pytest.raises(ValueError, match="max_concurrency"):
            _resolve_max_degree(bad_value, 10)


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
# MultiExecutionContextAggregator parallelization tests
# ---------------------------------------------------------------------------

class TestMultiExecutionAggregatorParallel:
    """Tests for parallel initialization in _MultiExecutionContextAggregator."""

    @pytest.mark.asyncio
    async def test_serial_mode_with_zero_parallelism(self):
        """With max_concurrency=0, producers should be peeked sequentially."""
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

        options = {"maxConcurrency": 0}

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
        """With max_concurrency>0, concurrent_peek_producers should be used."""
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

        options = {"maxConcurrency": 2}

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
        """With max_concurrency=0, drain should be sequential."""
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

        options = {"maxConcurrency": 0}

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

    # ------------------------------------------------------------------
    # Parallel drain path (_parallel_drain_producers) tests
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_parallel_drain_ordering_multiple_producers(self):
        """Items from multiple producers drained in parallel must be correctly
        ordered by the priority queue (ascending by orderByItems value)."""
        _NonStreamingOrderByContextAggregator = _import_non_streaming_aggregator()

        client = MagicMock()
        client._routing_map_provider = MagicMock()
        client._routing_map_provider.get_overlapping_ranges = AsyncMock(return_value=[
            {"id": "0", "minInclusive": "", "maxExclusive": "55"},
            {"id": "1", "minInclusive": "55", "maxExclusive": "AA"},
            {"id": "2", "minInclusive": "AA", "maxExclusive": "FF"},
        ])

        query_ex_info = MagicMock()
        query_ex_info.get_order_by.return_value = [{"item": "Ascending"}]
        query_ex_info.get_rewritten_query.return_value = None
        query_ex_info.get_query_ranges.return_value = [
            {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}
        ]
        # pq_size large enough so no trimming occurs
        query_ex_info.get_top.return_value = 100
        query_ex_info.get_limit.return_value = 0
        query_ex_info.get_offset.return_value = 0

        options = {"maxConcurrency": 2}  # triggers parallel path

        aggregator = _NonStreamingOrderByContextAggregator(
            client, "/dbs/db/colls/coll", "SELECT * FROM c ORDER BY c.val",
            options, query_ex_info, None, None
        )

        class MockDocProducer:
            def __init__(self, items_list, range_id):
                self._items = list(items_list)
                self._index = 0
                self._cur_item = None
                rng = {"id": str(range_id), "minInclusive": str(range_id), "maxExclusive": str(range_id + 1)}
                self._partition_key_target_range = rng

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

        # Three producers with interleaved sort values
        p0 = MockDocProducer([
            {"id": "a1", "orderByItems": [{"item": 1}]},
            {"id": "a5", "orderByItems": [{"item": 5}]},
            {"id": "a9", "orderByItems": [{"item": 9}]},
        ], range_id=0)
        p1 = MockDocProducer([
            {"id": "b2", "orderByItems": [{"item": 2}]},
            {"id": "b6", "orderByItems": [{"item": 6}]},
        ], range_id=1)
        p2 = MockDocProducer([
            {"id": "c3", "orderByItems": [{"item": 3}]},
            {"id": "c4", "orderByItems": [{"item": 4}]},
            {"id": "c7", "orderByItems": [{"item": 7}]},
            {"id": "c8", "orderByItems": [{"item": 8}]},
        ], range_id=2)

        producers_iter = iter([p0, p1, p2])
        with patch.object(
            aggregator, '_createTargetPartitionQueryExecutionContext',
            side_effect=lambda _range: next(producers_iter)
        ):
            await aggregator._configure_partition_ranges()

        # All 9 items should be in the PQ
        assert aggregator._orderByPQ.size() == 9

        # Pop all and verify ascending order
        popped_values = []
        while aggregator._orderByPQ.size() > 0:
            item = await aggregator._orderByPQ.pop_async(aggregator._document_producer_comparator)
            popped_values.append(item._item_result["orderByItems"][0]["item"])

        assert popped_values == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    @pytest.mark.asyncio
    async def test_parallel_drain_size_trimming(self):
        """When total drained items exceed pq_size, the priority queue must
        be trimmed to keep only the top pq_size items."""
        _NonStreamingOrderByContextAggregator = _import_non_streaming_aggregator()

        client = MagicMock()
        client._routing_map_provider = MagicMock()
        client._routing_map_provider.get_overlapping_ranges = AsyncMock(return_value=[
            {"id": "0", "minInclusive": "", "maxExclusive": "80"},
            {"id": "1", "minInclusive": "80", "maxExclusive": "FF"},
        ])

        query_ex_info = MagicMock()
        query_ex_info.get_order_by.return_value = [{"item": "Ascending"}]
        query_ex_info.get_rewritten_query.return_value = None
        query_ex_info.get_query_ranges.return_value = [
            {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}
        ]
        # pq_size = 3 (via get_top), but we'll have 6 items total
        query_ex_info.get_top.return_value = 3
        query_ex_info.get_limit.return_value = 0
        query_ex_info.get_offset.return_value = 0

        options = {"maxConcurrency": 2}

        aggregator = _NonStreamingOrderByContextAggregator(
            client, "/dbs/db/colls/coll", "SELECT TOP 3 * FROM c ORDER BY c.val",
            options, query_ex_info, None, None
        )

        class MockDocProducer:
            def __init__(self, items_list, range_id):
                self._items = list(items_list)
                self._index = 0
                self._cur_item = None
                rng = {"id": str(range_id), "minInclusive": str(range_id), "maxExclusive": str(range_id + 1)}
                self._partition_key_target_range = rng

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

        p0 = MockDocProducer([
            {"id": "a1", "orderByItems": [{"item": 1}]},
            {"id": "a3", "orderByItems": [{"item": 3}]},
            {"id": "a5", "orderByItems": [{"item": 5}]},
        ], range_id=0)
        p1 = MockDocProducer([
            {"id": "b2", "orderByItems": [{"item": 2}]},
            {"id": "b4", "orderByItems": [{"item": 4}]},
            {"id": "b6", "orderByItems": [{"item": 6}]},
        ], range_id=1)

        producers_iter = iter([p0, p1])
        with patch.object(
            aggregator, '_createTargetPartitionQueryExecutionContext',
            side_effect=lambda _range: next(producers_iter)
        ):
            await aggregator._configure_partition_ranges()

        # PQ should have been trimmed to pq_size = 3
        assert aggregator._orderByPQ.size() == 3

        # The top-3 ascending items should be 1, 2, 3
        popped_values = []
        while aggregator._orderByPQ.size() > 0:
            item = await aggregator._orderByPQ.pop_async(aggregator._document_producer_comparator)
            popped_values.append(item._item_result["orderByItems"][0]["item"])

        assert popped_values == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_parallel_drain_exception_cancels_remaining_tasks(self):
        """If one producer raises during parallel drain, the exception should
        propagate and remaining tasks should be cancelled."""
        _NonStreamingOrderByContextAggregator = _import_non_streaming_aggregator()

        client = MagicMock()
        client._routing_map_provider = MagicMock()
        client._routing_map_provider.get_overlapping_ranges = AsyncMock(return_value=[
            {"id": "0", "minInclusive": "", "maxExclusive": "80"},
            {"id": "1", "minInclusive": "80", "maxExclusive": "FF"},
        ])

        query_ex_info = MagicMock()
        query_ex_info.get_order_by.return_value = [{"item": "Ascending"}]
        query_ex_info.get_rewritten_query.return_value = None
        query_ex_info.get_query_ranges.return_value = [
            {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}
        ]
        query_ex_info.get_top.return_value = 10
        query_ex_info.get_limit.return_value = 0
        query_ex_info.get_offset.return_value = 0

        options = {"maxConcurrency": 2}

        aggregator = _NonStreamingOrderByContextAggregator(
            client, "/dbs/db/colls/coll", "SELECT * FROM c ORDER BY c.val",
            options, query_ex_info, None, None
        )

        class GoodProducer:
            """Producer that yields one item then stops."""
            def __init__(self):
                self._done = False
                self._cur_item = None
                self._partition_key_target_range = {"id": "0", "minInclusive": "0", "maxExclusive": "80"}

            def get_target_range(self):
                return self._partition_key_target_range

            async def peek(self):
                if self._done:
                    raise StopAsyncIteration
                self._cur_item = {"id": "ok", "orderByItems": [{"item": 1}]}
                return self._cur_item

            async def __anext__(self):
                if self._done:
                    raise StopAsyncIteration
                self._done = True
                return self._cur_item

        class FailingProducer:
            """Producer that succeeds on peek but raises RuntimeError during drain."""
            def __init__(self):
                self._peeked = False
                self._partition_key_target_range = {"id": "1", "minInclusive": "80", "maxExclusive": "FF"}

            def get_target_range(self):
                return self._partition_key_target_range

            async def peek(self):
                if not self._peeked:
                    self._peeked = True
                    return {"id": "fail", "orderByItems": [{"item": 2}]}
                raise RuntimeError("simulated drain failure")

            async def __anext__(self):
                raise RuntimeError("simulated drain failure")

        good = GoodProducer()
        bad = FailingProducer()

        producers_iter = iter([good, bad])
        with patch.object(
            aggregator, '_createTargetPartitionQueryExecutionContext',
            side_effect=lambda _range: next(producers_iter)
        ):
            with pytest.raises(RuntimeError, match="simulated drain failure"):
                await aggregator._configure_partition_ranges()

    @pytest.mark.asyncio
    async def test_parallel_drain_with_empty_producer(self):
        """One empty producer among several should not affect parallel drain
        of the remaining producers."""
        _NonStreamingOrderByContextAggregator = _import_non_streaming_aggregator()

        client = MagicMock()
        client._routing_map_provider = MagicMock()
        client._routing_map_provider.get_overlapping_ranges = AsyncMock(return_value=[
            {"id": "0", "minInclusive": "", "maxExclusive": "55"},
            {"id": "1", "minInclusive": "55", "maxExclusive": "AA"},
            {"id": "2", "minInclusive": "AA", "maxExclusive": "FF"},
        ])

        query_ex_info = MagicMock()
        query_ex_info.get_order_by.return_value = [{"item": "Ascending"}]
        query_ex_info.get_rewritten_query.return_value = None
        query_ex_info.get_query_ranges.return_value = [
            {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}
        ]
        query_ex_info.get_top.return_value = 50
        query_ex_info.get_limit.return_value = 0
        query_ex_info.get_offset.return_value = 0

        options = {"maxConcurrency": 3}

        aggregator = _NonStreamingOrderByContextAggregator(
            client, "/dbs/db/colls/coll", "SELECT * FROM c ORDER BY c.val",
            options, query_ex_info, None, None
        )

        class MockDocProducer:
            def __init__(self, items_list, range_id):
                self._items = list(items_list)
                self._index = 0
                self._cur_item = None
                rng = {"id": str(range_id), "minInclusive": str(range_id), "maxExclusive": str(range_id + 1)}
                self._partition_key_target_range = rng

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

        # p0 has items, p1 is empty (will be filtered during peek), p2 has items
        p0 = MockDocProducer([
            {"id": "a1", "orderByItems": [{"item": 1}]},
            {"id": "a3", "orderByItems": [{"item": 3}]},
        ], range_id=0)
        p1 = MockDocProducer([], range_id=1)  # empty
        p2 = MockDocProducer([
            {"id": "c2", "orderByItems": [{"item": 2}]},
            {"id": "c4", "orderByItems": [{"item": 4}]},
        ], range_id=2)

        producers_iter = iter([p0, p1, p2])
        with patch.object(
            aggregator, '_createTargetPartitionQueryExecutionContext',
            side_effect=lambda _range: next(producers_iter)
        ):
            await aggregator._configure_partition_ranges()

        # Only 4 items from producers p0 and p2 (p1 was empty and filtered out during peek)
        assert aggregator._orderByPQ.size() == 4

        popped_values = []
        while aggregator._orderByPQ.size() > 0:
            item = await aggregator._orderByPQ.pop_async(aggregator._document_producer_comparator)
            popped_values.append(item._item_result["orderByItems"][0]["item"])

        assert popped_values == [1, 2, 3, 4]


# ---------------------------------------------------------------------------
# Options threading tests
# ---------------------------------------------------------------------------

class TestOptionsThreading:
    """Test that new kwargs properly flow through the options pipeline."""

    def test_base_build_options_includes_new_keys(self):
        """Verify build_options extracts max_concurrency."""
        from azure.cosmos._base import build_options

        kwargs = {
            "max_concurrency": 4,
        }
        options = build_options(kwargs)
        assert options["maxConcurrency"] == 4
        # kwargs should have been consumed
        assert "max_concurrency" not in kwargs

    def test_base_build_options_without_new_keys(self):
        """Verify build_options works fine without the new kwargs."""
        from azure.cosmos._base import build_options

        kwargs = {"max_item_count": 10}
        options = build_options(kwargs)
        assert "maxConcurrency" not in options
        assert options["maxItemCount"] == 10


# ---------------------------------------------------------------------------
# Prefix partition key / feed range parallel fan-out tests
# ---------------------------------------------------------------------------

class TestPrefixQueryParallelFanOut:
    """Tests for the parallel fan-out pattern used in prefix partition key and
    feed range queries (the ``__QueryFeed`` path in the async connection)."""

    @pytest.mark.asyncio
    async def test_parallel_fan_out_merges_standard_results(self):
        """Parallel fan-out correctly merges non-aggregate results from multiple partitions."""
        from azure.cosmos._base import _merge_query_results

        # Simulate 3 partition results returned concurrently
        partition_results = [
            {"Documents": [{"id": "1"}, {"id": "2"}], "_count": 2},
            {"Documents": [{"id": "3"}, {"id": "4"}], "_count": 2},
            {"Documents": [{"id": "5"}], "_count": 1},
        ]

        # Merge sequentially (same as post-gather merge in __QueryFeed)
        merged: dict = {}
        for partial in partition_results:
            merged = _merge_query_results(merged, partial, "SELECT * FROM c")

        assert len(merged["Documents"]) == 5
        assert merged["_count"] == 5

    @pytest.mark.asyncio
    async def test_parallel_fan_out_merges_count_aggregate(self):
        """Parallel fan-out correctly merges COUNT aggregates from multiple partitions."""
        from azure.cosmos._base import _merge_query_results

        partition_results = [
            {"Documents": [{"_aggregate": {"$1": 10}}], "_count": 1},
            {"Documents": [{"_aggregate": {"$1": 20}}], "_count": 1},
            {"Documents": [{"_aggregate": {"$1": 30}}], "_count": 1},
        ]

        merged: dict = {}
        for partial in partition_results:
            merged = _merge_query_results(merged, partial, "SELECT COUNT(1) FROM c")

        assert merged["Documents"][0]["_aggregate"]["$1"] == 60

    @pytest.mark.asyncio
    async def test_parallel_fan_out_merges_min_aggregate(self):
        """Parallel fan-out correctly merges MIN aggregates from multiple partitions."""
        from azure.cosmos._base import _merge_query_results

        partition_results = [
            {"Documents": [{"_aggregate": {"min_val": 42}}], "_count": 1},
            {"Documents": [{"_aggregate": {"min_val": 7}}], "_count": 1},
            {"Documents": [{"_aggregate": {"min_val": 99}}], "_count": 1},
        ]

        merged: dict = {}
        for partial in partition_results:
            merged = _merge_query_results(merged, partial, "SELECT MIN(c.val) FROM c")

        assert merged["Documents"][0]["_aggregate"]["min_val"] == 7

    @pytest.mark.asyncio
    async def test_header_copies_are_independent(self):
        """Each concurrent task operates on its own header copy with no cross-task interference."""
        base_headers = {"Authorization": "token123", "x-ms-version": "2021-01-01"}

        captured_headers: list[dict] = []
        lock = asyncio.Lock()

        async def mock_post(headers):
            async with lock:
                captured_headers.append(dict(headers))
            await asyncio.sleep(0.01)
            return {"Documents": [], "_count": 0}, {}

        ranges = [
            {"id": "0", "minInclusive": "", "maxExclusive": "55"},
            {"id": "1", "minInclusive": "55", "maxExclusive": "AA"},
            {"id": "2", "minInclusive": "AA", "maxExclusive": "FF"},
        ]

        semaphore = asyncio.Semaphore(3)

        async def _query_range(range_info):
            task_headers = dict(base_headers)
            task_headers["x-ms-documentdb-partitionkeyrangeid"] = range_info["id"]
            async with semaphore:
                return await mock_post(task_headers)

        tasks = [asyncio.create_task(_query_range(r)) for r in ranges]
        await asyncio.gather(*tasks)

        # Verify each task got independent headers with different range IDs
        range_ids = sorted(h["x-ms-documentdb-partitionkeyrangeid"] for h in captured_headers)
        assert range_ids == ["0", "1", "2"]
        # Original headers should be unchanged
        assert "x-ms-documentdb-partitionkeyrangeid" not in base_headers

    @pytest.mark.asyncio
    async def test_task_cancellation_on_failure(self):
        """If one concurrent task fails, remaining tasks are properly cancelled."""
        started = asyncio.Event()

        async def mock_post_success():
            started.set()
            await asyncio.sleep(5.0)  # Long-running, should be cancelled
            return {"Documents": [], "_count": 0}, {}

        async def mock_post_fail():
            await started.wait()  # Wait until at least one other task starts
            raise RuntimeError("Simulated partition failure")

        semaphore = asyncio.Semaphore(3)

        async def _run(coroutine_fn):
            async with semaphore:
                return await coroutine_fn()

        tasks = [
            asyncio.create_task(_run(mock_post_success)),
            asyncio.create_task(_run(mock_post_fail)),
            asyncio.create_task(_run(mock_post_success)),
        ]

        with pytest.raises(RuntimeError, match="Simulated partition failure"):
            try:
                await asyncio.gather(*tasks)
            except Exception:
                for t in tasks:
                    if not t.done():
                        t.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                raise

    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self):
        """Semaphore properly limits the number of concurrent in-flight HTTP calls."""
        max_concurrent = 0
        current_concurrent = 0
        lock = asyncio.Lock()

        async def mock_post(range_id):
            nonlocal max_concurrent, current_concurrent
            async with lock:
                current_concurrent += 1
                max_concurrent = max(max_concurrent, current_concurrent)
            await asyncio.sleep(0.05)
            async with lock:
                current_concurrent -= 1
            return {"Documents": [{"id": range_id}], "_count": 1}, {}

        # 5 ranges but concurrency limit of 2
        ranges = [str(i) for i in range(5)]
        semaphore = asyncio.Semaphore(2)

        async def _query_range(range_id):
            async with semaphore:
                return await mock_post(range_id)

        tasks = [asyncio.create_task(_query_range(r)) for r in ranges]
        results = await asyncio.gather(*tasks)

        assert max_concurrent <= 2
        assert len(results) == 5

    def test_resolve_max_degree_controls_fan_out_decision(self):
        """_resolve_max_degree determines serial vs parallel for prefix query fan-out."""
        # Serial: None and 0 both yield 0 (serial)
        assert _resolve_max_degree(None, 5) == 0
        assert _resolve_max_degree(0, 5) == 0
        # Parallel: positive value or auto (-1) yield > 0
        assert _resolve_max_degree(3, 5) == 3
        assert _resolve_max_degree(-1, 5) > 0
        # Single range: auto still returns a value but at most 1
        assert _resolve_max_degree(-1, 1) <= 1
