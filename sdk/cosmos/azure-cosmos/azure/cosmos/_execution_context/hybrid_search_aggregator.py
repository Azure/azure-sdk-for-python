# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

"""Internal class for multi execution context aggregator implementation in the Azure Cosmos database service.
"""

from azure.cosmos._execution_context.base_execution_context import _QueryExecutionContextBase
from azure.cosmos._execution_context.multi_execution_aggregator import _MultiExecutionContextAggregator
from azure.cosmos._execution_context import document_producer
from azure.cosmos._routing import routing_range
from azure.cosmos import exceptions


# pylint: disable=protected-access

class _Placeholders:
    total_document_count = "{documentdb-formattablehybridsearchquery-totaldocumentcount}"
    formattable_total_word_count = "{{documentdb-formattablehybridsearchquery-totalwordcount-{0}}}"
    formattable_hit_counts_array = "{{documentdb-formattablehybridsearchquery-hitcountsarray-{0}}}"


class _HybridSearchContextAggregator(_QueryExecutionContextBase):
    """This class is a subclass of the query execution context base and serves for
    non-streaming order by queries. It is very similar to the existing MultiExecutionContextAggregator,
    but is needed since we're dealing with items and not document producers.

    This class builds upon the multi-execution aggregator, building a document producer per partition
    and draining their results entirely in order to create the result set relevant to the filters passed
    by the user.
    """

    def __init__(self, client, resource_link, query, options, partitioned_query_ex_info, hybrid_search_query_info,
                 all_pk_ranges):
        super(_HybridSearchContextAggregator, self).__init__(client, options)

        # use the routing provider in the client
        self._routing_provider = client._routing_map_provider
        self._client = client
        self._resource_link = resource_link
        self._original_query = query
        self._partitioned_query_ex_info = partitioned_query_ex_info
        self._sort_orders = partitioned_query_ex_info.get_order_by()
        self._orderByPQ = _MultiExecutionContextAggregator.PriorityQueue()
        self.hybrid_search_query_info = hybrid_search_query_info
        self.skip = hybrid_search_query_info['skip']
        self.take = hybrid_search_query_info['take']
        self.all_pk_ranges = all_pk_ranges
        self.original_query = query
        self.aggregated_global_statistics = None

        # will be a list of (partition_min, partition_max) tuples
        targetPartitionRanges = self._get_target_partition_key_range()

        self._document_producer_comparator = document_producer._PartitionKeyRangeDocumentProducerComparator()

        # Step 1: Check if we need to run global statistics queries, and if so do for every partition in the container
        self.ranges_to_statistics = []
        if hybrid_search_query_info['requiresGlobalStatistics']:
            global_statistics_doc_producers = []
            global_statistics_query = hybrid_search_query_info['globalStatisticsQuery']
            partitioned_query_execution_context_list = []
            for partition_key_target_range in all_pk_ranges:
                # create a document producer for each partition key range
                partitioned_query_execution_context_list.append(
                    document_producer._DocumentProducer(
                        partition_key_target_range,
                        self._client,
                        self._resource_link,
                        global_statistics_query,
                        self._document_producer_comparator,
                        self._options,
                    )
                )

            # verify all document producers have items/ no splits
            for target_query_ex_context in partitioned_query_execution_context_list:
                try:
                    target_query_ex_context.peek()
                    global_statistics_doc_producers.append(target_query_ex_context)
                except exceptions.CosmosHttpResponseError as e:
                    if exceptions._partition_range_is_gone(e):
                        # repairing document producer context on partition split
                        self._repair_document_producer()
                    else:
                        raise
                except StopIteration:
                    continue

            # Aggregate all partitioned global statistics
            self._aggregate_global_statistics(global_statistics_doc_producers)
            for doc_prod in global_statistics_doc_producers:
                self.ranges_to_statistics.append([doc_prod._cur_item, doc_prod._partition_key_target_range, doc_prod._options])

            print(3)
        # Step 2: re-write the component queries if needed
        component_query_infos = self.hybrid_search_query_info['componentQueryInfos']
        if self.aggregated_global_statistics:
            rewritten_query_infos = []
            for query_info in component_query_infos:
                assert query_info['orderBy']
                assert query_info['hasNonStreamingOrderBy']
                rewritten_order_by_expressions = []
                for order_by_expression in query_info['orderByExpressions']:
                    rewritten_order_by_expression = self._format_component_query(order_by_expression)
                    rewritten_order_by_expressions.append(rewritten_order_by_expression)

                rewritten_query = self._format_component_query(query_info['rewrittenQuery'])
                new_query_info = query_info.copy()
                new_query_info['orderByExpressions'] = rewritten_order_by_expressions
                new_query_info['rewrittenQuery'] = rewritten_query
                rewritten_query_infos.append(new_query_info)
            print("minute 19ish in the video")

    def _format_component_query(self, format_string):
        query = format_string.replace(_Placeholders.total_document_count, str(self.aggregated_global_statistics['documentCount']))

        for i in range(len(self.aggregated_global_statistics['fullTextStatistics'])):
            full_text_statistics = self.aggregated_global_statistics['fullTextStatistics'][i]
            query = query.replace(_Placeholders.formattable_total_word_count.format(i), full_text_statistics['totalWordCount'])
            hit_counts_array = f"[{','.join(map(str, full_text_statistics['hitCounts']))}]"
            query = query.replace(_Placeholders.formattable_hit_counts_array.format(i), hit_counts_array)

        return query

    def _aggregate_global_statistics(self, global_statistics_doc_producers):
        self.aggregated_global_statistics = {"documentCount": 0,
                                             "fullTextStatistics": None}
        for document_producer in global_statistics_doc_producers:
            self.aggregated_global_statistics["documentCount"] += document_producer._cur_item['documentCount']
            if self.aggregated_global_statistics["fullTextStatistics"] is None:
                self.aggregated_global_statistics["fullTextStatistics"] = document_producer._cur_item['fullTextStatistics']
            else:
                all_text_statistics = self.aggregated_global_statistics["fullTextStatistics"]
                curr_text_statistics = document_producer._cur_item['fullTextStatistics']
                assert len(all_text_statistics) == len(curr_text_statistics)
                for i in range(len(all_text_statistics)):
                    assert len(all_text_statistics[i]['hitCounts']) == len(curr_text_statistics[i]['hitCounts'])
                    all_text_statistics[i]['totalWordCount'] += curr_text_statistics[i]['totalWordCount']
                    for j in range(len(all_text_statistics[i]['hitCounts'])):
                        all_text_statistics[i]['hitCounts'][j] += curr_text_statistics[i]['hitCounts'][j]

            print(2)

        print(3)

    def __next__(self):
        """Returns the next item result.

        :return: The next result.
        :rtype: dict
        :raises StopIteration: If no more results are left.
        """
        if self._orderByPQ.size() > 0:
            res = self._orderByPQ.pop()
            return res
        raise StopIteration

    def fetch_next_block(self):
        raise NotImplementedError("You should use pipeline's fetch_next_block.")

    def _repair_document_producer(self):
        """Repairs the document producer context by using the re-initialized routing map provider in the client,
        which loads in a refreshed partition key range cache to re-create the partition key ranges.
        After loading this new cache, the document producers get re-created with the new valid ranges.
        """
        # refresh the routing provider to get the newly initialized one post-refresh
        self._routing_provider = self._client._routing_map_provider
        # will be a list of (partition_min, partition_max) tuples
        targetPartitionRanges = self._get_target_partition_key_range()

        partitioned_query_execution_context_list = []
        for partitionTargetRange in targetPartitionRanges:
            # create and add the child execution context for the target range
            partitioned_query_execution_context_list.append(
                self._create_global_statistics_partitioned_execution_context(partitionTargetRange)
            )

        self._doc_producers = []
        for target_query_ex_context in partitioned_query_execution_context_list:
            try:
                target_query_ex_context.peek()
                # if there are matching results in the target ex range add it to the priority queue
                self._doc_producers.append(target_query_ex_context)

            except StopIteration:
                continue

    def _create_global_statistics_partitioned_execution_context(self, partition_key_target_range):

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

    def _create_partitioned_global_statistics_query(self, partition_key_target_range):

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

    def _get_target_partition_key_range(self):
        query_ranges = self._partitioned_query_ex_info.get_query_ranges()
        return self._routing_provider.get_overlapping_ranges(
            self._resource_link, [routing_range.Range.ParseFromDict(range_as_dict) for range_as_dict in query_ranges]
        )
