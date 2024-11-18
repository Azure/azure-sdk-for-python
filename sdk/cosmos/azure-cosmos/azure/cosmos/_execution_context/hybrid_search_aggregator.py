# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

"""Internal class for multi execution context aggregator implementation in the Azure Cosmos database service.
"""

from azure.cosmos._execution_context.base_execution_context import _QueryExecutionContextBase
from azure.cosmos._execution_context import document_producer
from azure.cosmos._routing import routing_range
from azure.cosmos import exceptions

# pylint: disable=protected-access
RRF_CONSTANT = 60


class _Placeholders:
    total_document_count = "{documentdb-formattablehybridsearchquery-totaldocumentcount}"
    formattable_total_word_count = "{{documentdb-formattablehybridsearchquery-totalwordcount-{0}}}"
    formattable_hit_counts_array = "{{documentdb-formattablehybridsearchquery-hitcountsarray-{0}}}"
    formattable_order_by = "{documentdb-formattableorderbyquery-filter}"


def _retrieve_component_scores(drained_results):
    component_scores_list = []
    for _ in drained_results[0]['payload']['componentScores']:
        component_scores_list.append([])
    undefined_components = [-999999] * len(component_scores_list)
    for index, result in enumerate(drained_results):
        component_scores = result['payload']['componentScores']
        # Another small fix while backend changes are released to deal with empty component score scenarios
        if len(component_scores) == 0:
            component_scores = undefined_components
        for component_score_index, component_score in enumerate(component_scores):
            score_tuple = (component_score, index)
            component_scores_list[component_score_index].append(score_tuple)
    return component_scores_list


def _compute_rrf_scores(ranks, query_results):
    component_count = len(ranks)
    for index, result in enumerate(query_results):
        rrf_score = 0.0
        for component_index in range(component_count):
            rrf_score += 1.0 / (RRF_CONSTANT + ranks[component_index][index])
        # Add the score to the item to be returned
        result['Score'] = rrf_score


def _compute_ranks(component_scores):
    # initialize ranks as an N-D list with zeros
    ranks = [[0] * len(component_scores[0]) for _ in range(len(component_scores))]

    for component_index, scores in enumerate(component_scores):
        rank = 1  # ranks are 1-based
        for index, score_tuple in enumerate(scores):
            # Identical scores should have the same rank
            if index > 0 and score_tuple[0] < scores[index - 1][0]:
                rank += 1
            ranks[component_index][score_tuple[1]] = rank

    return ranks


def _coalesce_duplicate_rids(query_results):
    unique_rids = {d['_rid']: d for d in query_results}
    return list(unique_rids.values())


def _drain_and_coalesce_results(document_producers_to_drain):
    all_results = []
    is_singleton = True
    for dp in document_producers_to_drain:
        all_results.append(dp.peek())
        all_results.extend(dp._ex_context._buffer)
    if len(document_producers_to_drain) > 1:
        all_results = _coalesce_duplicate_rids(all_results)
        is_singleton = False
    return all_results, is_singleton


def _rewrite_query_infos(hybrid_search_query_info, global_statistics):
    rewritten_query_infos = []
    for query_info in hybrid_search_query_info['componentQueryInfos']:
        assert query_info['orderBy']
        assert query_info['hasNonStreamingOrderBy']
        rewritten_order_by_expressions = []
        for order_by_expression in query_info['orderByExpressions']:
            rewritten_order_by_expressions.append(
                _format_component_query_workaround(order_by_expression, global_statistics,
                                                   len(hybrid_search_query_info[
                                                           'componentQueryInfos'])))
        rewritten_query = _format_component_query_workaround(query_info['rewrittenQuery'],
                                                             global_statistics,
                                                             len(hybrid_search_query_info[
                                                                     'componentQueryInfos']))
        new_query_info = query_info.copy()
        new_query_info['orderByExpressions'] = rewritten_order_by_expressions
        new_query_info['rewrittenQuery'] = rewritten_query
        rewritten_query_infos.append(new_query_info)
    return rewritten_query_infos


def _format_component_query(format_string, global_statistics):
    format_string = format_string.replace(_Placeholders.formattable_order_by, "true")
    query = format_string.replace(_Placeholders.total_document_count,
                                  str(global_statistics['documentCount']))

    for i in range(len(global_statistics['fullTextStatistics'])):
        full_text_statistics = global_statistics['fullTextStatistics'][i]
        query = query.replace(_Placeholders.formattable_total_word_count.format(i),
                              str(full_text_statistics['totalWordCount']))
        hit_counts_array = f"[{','.join(map(str, full_text_statistics['hitCounts']))}]"
        query = query.replace(_Placeholders.formattable_hit_counts_array.format(i), hit_counts_array)

    return query


def _format_component_query_workaround(format_string, global_statistics, component_count):
    # TODO: remove this method once the fix is live and switch back to one above
    format_string = format_string.replace(_Placeholders.formattable_order_by, "true")
    query = format_string.replace(_Placeholders.total_document_count,
                                  str(global_statistics['documentCount']))
    statistics_index = 0
    for component_index in range(component_count):
        total_word_count_placeholder = _Placeholders.formattable_total_word_count.format(component_index)
        hit_counts_array_placeholder = _Placeholders.formattable_hit_counts_array.format(component_index)

        if total_word_count_placeholder not in query:
            continue

        full_text_statistics = global_statistics['fullTextStatistics'][statistics_index]
        query = query.replace(total_word_count_placeholder, str(full_text_statistics['totalWordCount']))

        hit_counts_array = f"[{','.join(map(str, full_text_statistics['hitCounts']))}]"
        query = query.replace(hit_counts_array_placeholder, hit_counts_array)

        statistics_index += 1

    return query


class _HybridSearchContextAggregator(_QueryExecutionContextBase):
    """This class is a subclass of the query execution context base and serves for
    full text search and hybrid search queries. It is very similar to the existing MultiExecutionContextAggregator,
    but is needed since we have a lot more additional client-side logic to take care of.

    This class builds upon the multi-execution aggregator, building a document producer per partition
    and draining their results entirely in order to create the result set relevant to the filters passed
    by the user.
    """

    def __init__(self, client, resource_link, options,
                 partitioned_query_execution_info, hybrid_search_query_info):
        super(_HybridSearchContextAggregator, self).__init__(client, options)

        # use the routing provider in the client
        self._routing_provider = client._routing_map_provider
        self._client = client
        self._resource_link = resource_link
        self._partitioned_query_ex_info = partitioned_query_execution_info
        self._hybrid_search_query_info = hybrid_search_query_info
        self._final_results = []
        self._aggregated_global_statistics = None
        self._document_producer_comparator = None

    def _run_hybrid_search(self):
        # Check if we need to run global statistics queries, and if so do for every partition in the container
        if self._hybrid_search_query_info['requiresGlobalStatistics']:
            target_partition_key_ranges = self._get_target_partition_key_range(target_all_ranges=True)
            global_statistics_doc_producers = []
            global_statistics_query = self._hybrid_search_query_info['globalStatisticsQuery']
            partitioned_query_execution_context_list = []
            for partition_key_target_range in target_partition_key_ranges:
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
                        global_statistics_doc_producers = self._repair_document_producer(global_statistics_query,
                                                                                         target_all_ranges=True)
                    else:
                        raise
                except StopIteration:
                    continue

            # Aggregate all partitioned global statistics
            self._aggregate_global_statistics(global_statistics_doc_producers)

        # re-write the component queries if needed
        if self._aggregated_global_statistics:
            rewritten_query_infos = _rewrite_query_infos(self._hybrid_search_query_info,
                                                         self._aggregated_global_statistics)
        else:
            rewritten_query_infos = self._hybrid_search_query_info['componentQueryInfos']

        component_query_execution_list = []
        # for each of the query infos, run the component queries for the target partitions
        target_partition_key_ranges = self._get_target_partition_key_range(target_all_ranges=False)
        for rewritten_query in rewritten_query_infos:
            for pk_range in target_partition_key_ranges:
                component_query_execution_list.append(
                    document_producer._DocumentProducer(
                        pk_range,
                        self._client,
                        self._resource_link,
                        rewritten_query['rewrittenQuery'],
                        self._document_producer_comparator,
                        self._options,
                    )
                )
        # verify all document producers have items/ no splits
        component_query_results = []
        for target_query_ex_context in component_query_execution_list:
            try:
                target_query_ex_context.peek()
                component_query_results.append(target_query_ex_context)
            except exceptions.CosmosHttpResponseError as e:
                if exceptions._partition_range_is_gone(e):
                    component_query_results = []
                    # repairing document producer context on partition split
                    for rewritten_query in rewritten_query_infos:
                        component_query_results.extend(self._repair_document_producer(
                            rewritten_query['rewrittenQuery']))
                else:
                    raise
            except StopIteration:
                continue

        # Drain all the results and coalesce on rid
        drained_results, is_singleton = _drain_and_coalesce_results(component_query_results)
        # If we only have one component query, we format the response and return with no further work
        if is_singleton:
            self._format_final_results(drained_results)
            return

        # Sort drained results by _rid
        drained_results.sort(key=lambda x: x['_rid'])

        # Compose component scores matrix, where each tuple is (score, index)
        component_scores = _retrieve_component_scores(drained_results)

        # Sort by scores in descending order
        for score_tuples in component_scores:
            score_tuples.sort(key=lambda x: x[0], reverse=True)

        # Compute the ranks
        ranks = _compute_ranks(component_scores)

        # Compute the RRF scores and add them to output
        _compute_rrf_scores(ranks, drained_results)

        # Finally, sort on the RRF scores to build the final result to return
        drained_results.sort(key=lambda x: x['Score'], reverse=True)
        self._format_final_results(drained_results)

    def _format_final_results(self, results):
        skip = self._hybrid_search_query_info['skip'] or 0
        take = self._hybrid_search_query_info['take']
        self._final_results = results[skip:skip + take]
        self._final_results.reverse()
        self._final_results = [item["payload"]["payload"] for item in self._final_results]

    def _rewrite_query_infos(self):
        rewritten_query_infos = []
        for query_info in self._hybrid_search_query_info['componentQueryInfos']:
            assert query_info['orderBy']
            assert query_info['hasNonStreamingOrderBy']
            rewritten_order_by_expressions = []
            for order_by_expression in query_info['orderByExpressions']:
                rewritten_order_by_expressions.append(
                    _format_component_query_workaround(order_by_expression, self._aggregated_global_statistics,
                                                       len(self._hybrid_search_query_info[
                                                               'componentQueryInfos'])))

            rewritten_query = _format_component_query_workaround(query_info['rewrittenQuery'],
                                                                 self._aggregated_global_statistics,
                                                                 len(self._hybrid_search_query_info[
                                                                         'componentQueryInfos']))
            new_query_info = query_info.copy()
            new_query_info['orderByExpressions'] = rewritten_order_by_expressions
            new_query_info['rewrittenQuery'] = rewritten_query
            rewritten_query_infos.append(new_query_info)
        return rewritten_query_infos

    def _aggregate_global_statistics(self, global_statistics_doc_producers):
        self._aggregated_global_statistics = {"documentCount": 0,
                                              "fullTextStatistics": None}
        for dp in global_statistics_doc_producers:
            self._aggregated_global_statistics["documentCount"] += dp._cur_item['documentCount']
            if self._aggregated_global_statistics["fullTextStatistics"] is None:
                self._aggregated_global_statistics["fullTextStatistics"] = dp._cur_item['fullTextStatistics']
            else:
                all_text_statistics = self._aggregated_global_statistics["fullTextStatistics"]
                curr_text_statistics = dp._cur_item['fullTextStatistics']
                assert len(all_text_statistics) == len(curr_text_statistics)
                for i, all_stats in enumerate(all_text_statistics):
                    curr_stats = curr_text_statistics[i]
                    assert len(all_stats['hitCounts']) == len(curr_stats['hitCounts'])
                    all_stats['totalWordCount'] += curr_stats['totalWordCount']
                    for j in range(len(all_stats['hitCounts'])):
                        all_stats['hitCounts'][j] += curr_stats['hitCounts'][j]

    def __next__(self):
        """Returns the next item result.

        :return: The next result.
        :rtype: dict
        :raises StopIteration: If no more results are left.
        """
        if len(self._final_results) > 0:
            res = self._final_results.pop()
            return res
        raise StopIteration

    def fetch_next_block(self):
        raise NotImplementedError("You should use pipeline's fetch_next_block.")

    def _repair_document_producer(self, query, target_all_ranges=False):
        # refresh the routing provider to get the newly initialized one post-refresh
        self._routing_provider = self._client._routing_map_provider
        # will be a list of (partition_min, partition_max) tuples
        target_partition_ranges = self._get_target_partition_key_range(target_all_ranges)

        partitioned_query_execution_context_list = []
        for partition_key_target_range in target_partition_ranges:
            # create and add the child execution context for the target range
            partitioned_query_execution_context_list.append(
                document_producer._DocumentProducer(
                    partition_key_target_range,
                    self._client,
                    self._resource_link,
                    query,
                    self._document_producer_comparator,
                    self._options,
                )
            )

        doc_producers = []
        for target_query_ex_context in partitioned_query_execution_context_list:
            try:
                target_query_ex_context.peek()
                doc_producers.append(target_query_ex_context)
            except StopIteration:
                continue
        return doc_producers

    def _get_target_partition_key_range(self, target_all_ranges):
        if target_all_ranges:
            return list(self._client._ReadPartitionKeyRanges(collection_link=self._resource_link))
        query_ranges = self._partitioned_query_ex_info.get_query_ranges()
        return self._routing_provider.get_overlapping_ranges(
            self._resource_link, [routing_range.Range.ParseFromDict(range_as_dict) for range_as_dict in query_ranges]
        )
