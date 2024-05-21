# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

"""Internal class for multi execution context aggregator implementation in the Azure Cosmos database service.
"""

from azure.cosmos._execution_context.aio.base_execution_context import _QueryExecutionContextBase
from azure.cosmos._execution_context.aio.multi_execution_aggregator import _MultiExecutionContextAggregator
from azure.cosmos._execution_context.aio import document_producer
from azure.cosmos._routing import routing_range
from azure.cosmos import exceptions

# pylint: disable=protected-access

class _NonStreamingOrderByContextAggregator(_QueryExecutionContextBase):
    """This class is a subclass of the query execution context base and serves for
    non-streaming order by queries. It is very similar to the existing MultiExecutionContextAggregator,
    but is needed since we're dealing with items and not document producers.

    This class builds upon the multi-execution aggregator, building a document producer per partition
    and draining their results entirely in order to create the result set relevant to the filters passed
    by the user.
    """

    def __init__(self, client, resource_link, query, options, partitioned_query_ex_info):
        super(_NonStreamingOrderByContextAggregator, self).__init__(client, options)

        # use the routing provider in the client
        self._routing_provider = client._routing_map_provider
        self._client = client
        self._resource_link = resource_link
        self._query = query
        self._partitioned_query_ex_info = partitioned_query_ex_info
        self._sort_orders = partitioned_query_ex_info.get_order_by()
        self._orderByPQ = _MultiExecutionContextAggregator.PriorityQueue()
        self._doc_producers = []
        self._document_producer_comparator = document_producer._NonStreamingOrderByComparator(self._sort_orders)


    async def __anext__(self):
        """Returns the next result

        :return: The next result.
        :rtype: dict
        :raises StopIteration: If no more result is left.
        """
        if self._orderByPQ.size() > 0:
            res = await self._orderByPQ.pop_async(self._document_producer_comparator)
            return res
        raise StopAsyncIteration

    async def fetch_next_block(self):

        raise NotImplementedError("You should use pipeline's fetch_next_block.")

    async def _repair_document_producer(self):
        """Repairs the document producer context by using the re-initialized routing map provider in the client,
        which loads in a refreshed partition key range cache to re-create the partition key ranges.
        After loading this new cache, the document producers get re-created with the new valid ranges.
        """
        # refresh the routing provider to get the newly initialized one post-refresh
        self._routing_provider = self._client._routing_map_provider
        # will be a list of (partition_min, partition_max) tuples
        targetPartitionRanges = await self._get_target_partition_key_range()

        targetPartitionQueryExecutionContextList = []
        for partitionTargetRange in targetPartitionRanges:
            # create and add the child execution context for the target range
            targetPartitionQueryExecutionContextList.append(
                self._createTargetPartitionQueryExecutionContext(partitionTargetRange)
            )
        self._doc_producers = []
        for targetQueryExContext in targetPartitionQueryExecutionContextList:
            try:
                await targetQueryExContext.peek()
                # if there are matching results in the target ex range add it to the priority queue
                self._doc_producers.append(targetQueryExContext)

            except StopAsyncIteration:
                continue

    def _createTargetPartitionQueryExecutionContext(self, partition_key_target_range):

        rewritten_query = self._partitioned_query_ex_info.get_rewritten_query()
        if rewritten_query:
            if isinstance(self._query, dict):
                # this is a parameterized query, collect all the parameters
                query = dict(self._query)
                query["query"] = rewritten_query
            else:
                query = rewritten_query
        else:
            query = self._query

        return document_producer._DocumentProducer(
            partition_key_target_range,
            self._client,
            self._resource_link,
            query,
            self._document_producer_comparator,
            self._options,
        )

    async def _get_target_partition_key_range(self):

        query_ranges = self._partitioned_query_ex_info.get_query_ranges()
        return await self._routing_provider.get_overlapping_ranges(
            self._resource_link, [routing_range.Range.ParseFromDict(range_as_dict) for range_as_dict in query_ranges]
        )

    async def _configure_partition_ranges(self):
        # will be a list of (partition_min, partition_max) tuples
        targetPartitionRanges = await self._get_target_partition_key_range()

        targetPartitionQueryExecutionContextList = []
        for partitionTargetRange in targetPartitionRanges:
            # create and add the child execution context for the target range
            targetPartitionQueryExecutionContextList.append(
                self._createTargetPartitionQueryExecutionContext(partitionTargetRange)
            )

        self._doc_producers = []
        for targetQueryExContext in targetPartitionQueryExecutionContextList:
            try:
                await targetQueryExContext.peek()
                self._doc_producers.append(targetQueryExContext)
            except exceptions.CosmosHttpResponseError as e:
                if exceptions._partition_range_is_gone(e):
                    # repairing document producer context on partition split
                    await self._repair_document_producer()
                else:
                    raise

            except StopAsyncIteration:
                continue

        pq_size = self._partitioned_query_ex_info.get_top() or\
                  self._partitioned_query_ex_info.get_limit() + self._partitioned_query_ex_info.get_offset()
        for doc_producer in self._doc_producers:
            while True:
                try:
                    result = await doc_producer.peek()
                    item_result = document_producer._NonStreamingItemResultProducer(result, self._sort_orders)
                    await self._orderByPQ.push_async(item_result, self._document_producer_comparator)
                    await doc_producer.__anext__()
                except StopAsyncIteration:
                    # this logic is necessary so that we only hold 2 * items_per_partition in memory at any time
                    if len(self._orderByPQ._heap) > pq_size:
                        new_heap = []
                        for i in range(pq_size):  # pylint: disable=unused-variable
                            new_heap.append(await self._orderByPQ.pop_async(self._document_producer_comparator))
                        del self._orderByPQ._heap
                        self._orderByPQ._heap = new_heap
                    break
