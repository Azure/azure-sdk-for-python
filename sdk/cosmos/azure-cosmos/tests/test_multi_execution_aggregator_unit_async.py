# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest

from azure.cosmos import exceptions
from azure.cosmos.aio import CosmosClient  # noqa: F401 - needed to resolve circular imports
from azure.cosmos._execution_context.aio.multi_execution_aggregator import _MultiExecutionContextAggregator
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes


class _DummyAsyncQueue:
    def __init__(self, producer):
        self._producer = producer
        self._size = 1

    def size(self):
        return self._size

    async def pop_async(self, comparator):
        self._size = 0
        return self._producer

    async def push_async(self, item, comparator):
        self._producer = item
        self._size += 1


class _AsyncSplitOnPeekProducer:
    def __init__(self, item):
        self.item = item
        self.next_calls = 0

    async def __anext__(self):
        self.next_calls += 1
        return self.item

    async def peek(self):
        error = exceptions.CosmosHttpResponseError(status_code=StatusCodes.GONE, message="split")
        error.sub_status = SubStatusCodes.PARTITION_KEY_RANGE_GONE
        raise error


class _ReplayAwareAsyncProducer:
    def __init__(self, name, target_range, items, split_on_peek=False):
        self.name = name
        self._target_range = target_range
        self._items = list(items)
        self._index = 0
        self._cur_item = None
        self._split_on_peek = split_on_peek
        self._split_raised = False
        self._next_calls = 0

    async def __anext__(self):
        self._next_calls += 1
        if self._cur_item is not None:
            result = self._cur_item
            self._cur_item = None
            return result
        if self._index >= len(self._items):
            raise StopAsyncIteration
        result = self._items[self._index]
        self._index += 1
        return result

    async def peek(self):
        if self._split_on_peek and self._next_calls > 0 and not self._split_raised:
            self._split_raised = True
            error = exceptions.CosmosHttpResponseError(status_code=StatusCodes.GONE, message="split")
            error.sub_status = SubStatusCodes.PARTITION_KEY_RANGE_GONE
            raise error
        if self._cur_item is None:
            if self._index >= len(self._items):
                raise StopAsyncIteration
            self._cur_item = self._items[self._index]
            self._index += 1
        return self._cur_item

    def get_target_range(self):
        return self._target_range


class _AsyncOrderComparator:
    async def compare(self, p1, p2):
        v1 = (await p1.peek())["order"]
        v2 = (await p2.peek())["order"]
        return (v1 > v2) - (v1 < v2)


class TestMultiExecutionAggregatorUnitAsync(unittest.IsolatedAsyncioTestCase):
    async def test_returns_fetched_item_when_peek_hits_partition_split_async(self):
        producer = _AsyncSplitOnPeekProducer({"id": "doc-1"})
        queue = _DummyAsyncQueue(producer)

        aggregator = object.__new__(_MultiExecutionContextAggregator)
        aggregator._orderByPQ = queue
        aggregator._document_producer_comparator = None

        repair_calls = {"count": 0}

        async def _repair(*args, **kwargs):
            repair_calls["count"] += 1

        aggregator._repair_document_producer = _repair

        result = await aggregator.__anext__()

        self.assertEqual(result["id"], "doc-1")
        self.assertEqual(producer.next_calls, 1)
        self.assertEqual(repair_calls["count"], 1)

    async def test_split_repair_preserves_unaffected_producers_async(self):
        unaffected = _ReplayAwareAsyncProducer(
            "unaffected",
            {"id": "0", "minInclusive": "10", "maxExclusive": "20"},
            [{"id": "A2", "order": 20}],
            split_on_peek=False,
        )
        split_producer = _ReplayAwareAsyncProducer(
            "split",
            {"id": "1", "minInclusive": "00", "maxExclusive": "10"},
            [{"id": "B1", "order": 10}],
            split_on_peek=True,
        )

        aggregator = object.__new__(_MultiExecutionContextAggregator)
        aggregator._orderByPQ = _MultiExecutionContextAggregator.PriorityQueue()
        aggregator._document_producer_comparator = _AsyncOrderComparator()
        await aggregator._orderByPQ.push_async(unaffected, aggregator._document_producer_comparator)
        await aggregator._orderByPQ.push_async(split_producer, aggregator._document_producer_comparator)
        aggregator._resource_link = "dbs/db/colls/c"
        aggregator._options = {}

        child1 = _ReplayAwareAsyncProducer(
            "child1",
            {"id": "1a", "minInclusive": "00", "maxExclusive": "05"},
            [{"id": "C1", "order": 11}],
        )
        child2 = _ReplayAwareAsyncProducer(
            "child2",
            {"id": "1b", "minInclusive": "05", "maxExclusive": "10"},
            [{"id": "C2", "order": 12}],
        )

        class _RoutingProvider:
            async def get_overlapping_ranges(self, resource_link, ranges, options):
                return [
                    {"id": "1a", "minInclusive": "00", "maxExclusive": "05"},
                    {"id": "1b", "minInclusive": "05", "maxExclusive": "10"},
                ]

        aggregator._client = type("_Client", (), {"_routing_map_provider": _RoutingProvider()})()
        aggregator._routing_provider = aggregator._client._routing_map_provider

        created = {"count": 0}

        def _create(range_dict):
            created["count"] += 1
            return child1 if range_dict["id"] == "1a" else child2

        aggregator._createTargetPartitionQueryExecutionContext = _create

        first = await aggregator.__anext__()

        self.assertEqual(first["id"], "B1")
        self.assertEqual(created["count"], 2)

        self.assertIn(unaffected, aggregator._orderByPQ._heap)
        self.assertEqual((await unaffected.peek())["id"], "A2")

        ids_in_heap = {p.name for p in aggregator._orderByPQ._heap}
        self.assertNotIn("split", ids_in_heap)
        self.assertIn("child1", ids_in_heap)
        self.assertIn("child2", ids_in_heap)

    async def test_rebuild_priority_queue_repairs_on_partition_gone_async(self):
        aggregator = object.__new__(_MultiExecutionContextAggregator)
        aggregator._orderByPQ = _MultiExecutionContextAggregator.PriorityQueue()
        aggregator._document_producer_comparator = _AsyncOrderComparator()
        aggregator._MAX_REBUILD_SPLIT_RETRIES = 3

        calls = {"count": 0, "context": None, "retry": None}

        async def _repair(failed_query_ex_context=None, split_retry_count=0):
            calls["count"] += 1
            calls["context"] = failed_query_ex_context
            calls["retry"] = split_retry_count

        aggregator._repair_document_producer = _repair

        producer = _AsyncSplitOnPeekProducer({"id": "doc-1"})
        await aggregator._rebuild_priority_queue([producer], split_retry_count=0)

        self.assertEqual(calls["count"], 1)
        self.assertIs(calls["context"], producer)
        self.assertEqual(calls["retry"], 1)


if __name__ == "__main__":
    unittest.main()
