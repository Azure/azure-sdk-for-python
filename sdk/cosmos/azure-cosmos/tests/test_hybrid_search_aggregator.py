# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Deterministic unit tests for client-side hybrid-search ranking."""

import asyncio
import copy
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from azure.cosmos import documents
from azure.cosmos.aio import CosmosClient  # noqa: F401 - initialize async execution contexts
from azure.cosmos._cosmos_client_connection import CosmosClientConnection
from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection as AsyncCosmosClientConnection
from azure.cosmos._cosmos_responses import CosmosAsyncItemPaged, CosmosItemPaged
from azure.cosmos._execution_context import execution_dispatcher
from azure.cosmos._execution_context.aio import execution_dispatcher as execution_dispatcher_async
from azure.cosmos._execution_context.hybrid_search_aggregator import (
    _compute_ranks,
    _compute_rrf_scores,
    _format_component_query,
    _rewrite_query_infos,
)
from azure.cosmos.http_constants import HttpHeaders, ResourceType, StatusCodes, SubStatusCodes
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos._query_iterable import QueryIterable
from azure.cosmos.aio._query_iterable_async import QueryIterable as AsyncQueryIterable
from azure.cosmos.partition_key import PartitionKey

pytestmark = pytest.mark.cosmosEmulator


@pytest.fixture(params=["sync", "async"])
def ranked_query_context(request, monkeypatch):
    is_async = request.param == "async"
    dispatcher = execution_dispatcher_async if is_async else execution_dispatcher
    mock_type = AsyncMock if is_async else Mock
    default_context = dispatcher._DefaultQueryExecutionContext
    monkeypatch.setattr(
        default_context,
        "_fetch_items_helper_with_retries",
        default_context._fetch_items_helper_no_retries,
    )
    ranges = [
        {"id": "0", "minInclusive": "", "maxExclusive": "80"},
        {"id": "1", "minInclusive": "80", "maxExclusive": "FF"},
    ]
    documents_in_insertion_order = [
        {"id": "couch", "pk": "cat", "text": "The cat is sleeping on the couch."},
        {"id": "fence", "pk": "cat", "text": "The cat jumped over the fence."},
    ]

    def create(query, options=None, component_count=1, skip=0, take=2):
        query_plan = {
            "queryInfo": {"distinctType": "None"},
            "queryRanges": [
                {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}
            ],
            "hybridSearchQueryInfo": {
                "requiresGlobalStatistics": True,
                "globalStatisticsQuery": "SELECT VALUE FullTextStatistics(c.text, 'fence') FROM c",
                "componentQueryInfos": [
                    {
                        "orderBy": ["Descending"],
                        "hasNonStreamingOrderBy": True,
                        "orderByExpressions": ["score"],
                        "rewrittenQuery": (
                            "SELECT * FROM c WHERE {documentdb-formattableorderbyquery-filter} "
                            "ORDER BY FullTextScore(c.text, 'fence', "
                            "{documentdb-formattablehybridsearchquery-totaldocumentcount}, "
                            "{documentdb-formattablehybridsearchquery-totalwordcount-0}, "
                            "{documentdb-formattablehybridsearchquery-hitcountsarray-0})"
                        ),
                    }
                    for _ in range(component_count)
                ],
                "skip": skip,
                "take": take,
            },
        }

        def query_feed(path, collection_id, rewritten_query, feed_options, range_id, **kwargs):
            text = rewritten_query["query"] if isinstance(rewritten_query, dict) else rewritten_query
            if text == query_plan["hybridSearchQueryInfo"]["globalStatisticsQuery"]:
                results = [{
                    "documentCount": 2,
                    "fullTextStatistics": [{"totalWordCount": 16, "hitCounts": [1]}],
                }]
            else:
                results = [
                    {
                        "_rid": item["id"],
                        "payload": {
                            "payload": item,
                            "componentScores": [score] * component_count,
                        },
                    }
                    for item, score in zip(reversed(documents_in_insertion_order), [2, 1])
                ]
            return copy.deepcopy(results), {}

        async def read_ranges(**kwargs):
            for item in ranges:
                yield item

        client = SimpleNamespace(
            connection_policy=documents.ConnectionPolicy(),
            last_response_headers={},
            _GetQueryPlanThroughGateway=mock_type(return_value=query_plan),
            _get_partition_key_definition=mock_type(return_value=PartitionKey(path="/pk")),
            _ReadPartitionKeyRanges=read_ranges if is_async else Mock(return_value=ranges),
            _routing_map_provider=SimpleNamespace(
                get_overlapping_ranges=mock_type(return_value=[ranges[0]])
            ),
            QueryFeed=mock_type(side_effect=query_feed),
        )
        # The direct service path succeeds, but ignores ORDER BY RANK.
        fetch = mock_type(return_value=(documents_in_insertion_order, {}))
        context = dispatcher._ProxyQueryExecutionContext(
            client,
            "dbs/db/colls/container",
            query,
            {"partitionKey": "cat", "maxItemCount": 1} if options is None else options,
            fetch,
            None,
            None,
            ResourceType.Document,
        )
        return context, client, fetch

    return is_async, create


async def _drain_context(context, is_async, by_page):
    results = []
    if by_page:
        while True:
            page = await context.fetch_next_block() if is_async else context.fetch_next_block()
            if not page:
                return results
            results.extend(page)
    if is_async:
        return [item async for item in context]
    return list(context)


@pytest.fixture(params=["legacy", "optimized"])
def hybrid_query_context(ranked_query_context, request):
    is_async, create = ranked_query_context

    def create_hybrid(component_pages, *, query=None, skip=0, take=10, cross_partition=False):
        context, client, fetch = create(
            query or "SELECT TOP 10 * FROM c ORDER BY RANK FullTextScore(c.text, 'fence')",
            options={"enableCrossPartitionQuery": True, "maxItemCount": 1} if cross_partition else None,
            component_count=len(component_pages),
            skip=skip,
            take=take,
        )
        plan = client._GetQueryPlanThroughGateway.return_value
        info = plan["hybridSearchQueryInfo"]
        for index, component in enumerate(info["componentQueryInfos"]):
            component["rewrittenQuery"] += f" /* component {index} */"
            if request.param == "optimized":
                for field in ("orderBy", "orderByExpressions", "hasNonStreamingOrderBy"):
                    component.pop(field)
        if cross_partition:
            client._routing_map_provider.get_overlapping_ranges.return_value.append(
                {"id": "1", "minInclusive": "80", "maxExclusive": "FF"}
            )
            error = CosmosHttpResponseError(status_code=StatusCodes.BAD_REQUEST, message="query plan required")
            error.sub_status = SubStatusCodes.CROSS_PARTITION_QUERY_NOT_SERVABLE
            fetch.side_effect = error

        original_feed = client.QueryFeed.side_effect
        client.component_requests = Mock()

        def query_feed(path, collection_id, query, options, range_id, **kwargs):
            text = query["query"] if isinstance(query, dict) else query
            if text == info["globalStatisticsQuery"]:
                return original_feed(path, collection_id, query, options, range_id, **kwargs)
            index = next(i for i in range(len(component_pages)) if text.endswith(f"/* component {i} */"))
            client.component_requests(index, range_id, options.get("continuation"))
            pages = component_pages[index].get(range_id, [])
            page_index = int(options.get("continuation") or 0)
            rows = copy.deepcopy(pages[page_index]) if pages else []
            if request.param == "legacy":
                rows = [
                    {"_rid": row["_rid"], "payload": {key: value for key, value in row.items() if key != "_rid"}}
                    for row in rows
                ]
            headers = {HttpHeaders.Continuation: str(page_index + 1)} if page_index + 1 < len(pages) else {}
            return rows, headers

        client.QueryFeed.side_effect = query_feed
        return context, client, info

    return is_async, create_hybrid


@pytest.mark.asyncio
@pytest.mark.parametrize("by_page", [False, True])
@pytest.mark.parametrize("parameterized", [False, True])
@pytest.mark.parametrize("component_count", [1, 2])
async def test_partition_scoped_rank_query_uses_plan_before_successful_direct_query(
    ranked_query_context, by_page, parameterized, component_count
):
    is_async, create = ranked_query_context
    expression = "FullTextScore(c.text, 'fence')"
    if component_count == 2:
        expression = f"RRF({expression}, VectorDistance(c.vector, [1, 0, 0]))"
    query = f"SELECT TOP 2 * FROM c ORDER BY RANK {expression}"
    parameters = [{"name": "@pk", "value": "cat"}]
    if parameterized:
        query = {"query": query.replace("FROM c", "FROM c WHERE c.pk = @pk"), "parameters": parameters}
    original_query = copy.deepcopy(query)
    options = {"partitionKey": "cat", "enableCrossPartitionQuery": False, "maxItemCount": 1}
    context, client, fetch = create(query, options, component_count)

    results = await _drain_context(context, is_async, by_page)

    assert [item["id"] for item in results] == ["fence", "couch"]
    assert all(item["pk"] == "cat" for item in results)
    fetch.assert_not_called()
    client._GetQueryPlanThroughGateway.assert_called_once_with(
        query, "dbs/db/colls/container", None, read_timeout=None
    )
    assert options == {"partitionKey": "cat", "enableCrossPartitionQuery": False, "maxItemCount": 1}
    component_calls = client.QueryFeed.call_args_list[2:]
    assert len(component_calls) == component_count
    for call in component_calls:
        assert call.args[3]["partitionKey"] == "cat"
        assert call.args[4] == "0"
        rewritten_query = call.args[2]
        if parameterized:
            assert rewritten_query["parameters"] == parameters
            rewritten_query = rewritten_query["query"]
        assert "{documentdb-" not in rewritten_query
        assert "'fence', 4, 32, [2]" in rewritten_query
    assert query == original_query


@pytest.mark.asyncio
@pytest.mark.parametrize("scope", ["Global", "Local"])
@pytest.mark.parametrize("partition_key", ["cat", "", 0, False, None])
async def test_rank_query_statistics_and_components_preserve_their_partition_scopes(
    ranked_query_context, scope, partition_key
):
    is_async, create = ranked_query_context
    query = "SELECT TOP 2 * FROM c ORDER BY RANK FullTextScore(c.text, 'fence')"
    context, client, _ = create(query, {"partitionKey": partition_key, "fullTextScoreScope": scope})

    await _drain_context(context, is_async, True)

    statistics_calls = client.QueryFeed.call_args_list[:-1]
    assert len(statistics_calls) == (2 if scope == "Global" else 1)
    for call in statistics_calls:
        if scope == "Global":
            assert "partitionKey" not in call.args[3]
        else:
            assert call.args[3]["partitionKey"] == partition_key
    assert client.QueryFeed.call_args_list[-1].args[3]["partitionKey"] == partition_key
    expected_range = PartitionKey(path="/pk")._get_epk_range_for_partition_key(partition_key)
    for call in client._routing_map_provider.get_overlapping_ranges.call_args_list:
        assert [query_range.to_dict() for query_range in call.args[1]] == [expected_range.to_dict()]


@pytest.mark.asyncio
async def test_rank_query_with_complete_hierarchical_partition_key(ranked_query_context):
    is_async, create = ranked_query_context
    partition_key = ["tenant", "cat"]
    definition = PartitionKey(path=["/tenant", "/pk"])
    context, client, fetch = create(
        "SELECT TOP 2 * FROM c ORDER BY RANK FullTextScore(c.text, 'fence')",
        {"partitionKey": partition_key},
    )
    client._get_partition_key_definition.return_value = definition

    assert [item["id"] for item in await _drain_context(context, is_async, True)] == ["fence", "couch"]
    expected_range = definition._get_epk_range_for_partition_key(partition_key)
    ranges = client._routing_map_provider.get_overlapping_ranges.call_args.args[1]
    assert [query_range.to_dict() for query_range in ranges] == [expected_range.to_dict()]
    assert client.QueryFeed.call_args.args[3]["partitionKey"] == partition_key
    fetch.assert_not_called()


@pytest.mark.asyncio
async def test_rank_query_cold_metadata_read_does_not_include_partition_key(ranked_query_context):
    is_async, create = ranked_query_context
    context, client, fetch = create(
        "SELECT TOP 2 * FROM c ORDER BY RANK FullTextScore(c.text, 'fence')",
        {"partitionKey": "cat", "excludedLocations": ["East US"]},
    )

    def read_partition_key_definition(resource_link, options):
        if "partitionKey" in options:
            raise CosmosHttpResponseError(
                status_code=StatusCodes.BAD_REQUEST,
                message="x-ms-documentdb-partitionkey header cannot be specified for this request",
            )
        assert options["excludedLocations"] == ["East US"]
        return PartitionKey(path="/pk")

    client._get_partition_key_definition.side_effect = read_partition_key_definition

    assert [item["id"] for item in await _drain_context(context, is_async, True)] == ["fence", "couch"]
    assert client.QueryFeed.call_args.args[3]["partitionKey"] == "cat"
    fetch.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("scope", ["Global", "Local"])
async def test_statistics_partition_split_repair_keeps_statistics_scope(ranked_query_context, scope):
    is_async, create = ranked_query_context
    context, client, _ = create(
        "SELECT TOP 2 * FROM c ORDER BY RANK FullTextScore(c.text, 'fence')",
        {"partitionKey": "cat", "fullTextScoreScope": scope},
    )
    query_feed = client.QueryFeed.side_effect
    split = False

    def split_once(path, collection_id, query, options, range_id, **kwargs):
        nonlocal split
        if not split and "FullTextStatistics" in query and range_id == ("1" if scope == "Global" else "0"):
            split = True
            error = CosmosHttpResponseError(status_code=StatusCodes.GONE, message="partition split")
            error.sub_status = SubStatusCodes.PARTITION_KEY_RANGE_GONE
            raise error
        return query_feed(path, collection_id, query, options, range_id, **kwargs)

    client.QueryFeed.side_effect = split_once

    assert [item["id"] for item in await _drain_context(context, is_async, True)] == ["fence", "couch"]
    assert split
    for call in client.QueryFeed.call_args_list[:-1]:
        if scope == "Global":
            assert "partitionKey" not in call.args[3]
        else:
            assert call.args[3]["partitionKey"] == "cat"
    assert client.QueryFeed.call_args.args[3]["partitionKey"] == "cat"


@pytest.mark.asyncio
async def test_rank_query_pager_resolves_partition_key_and_preserves_pages(ranked_query_context):
    is_async, create = ranked_query_context
    query = "SELECT TOP 2 * FROM c ORDER BY RANK FullTextScore(c.text, 'fence')"
    options = {"partitionKey": "cat", "maxItemCount": 1}
    context, client, fetch = create(query, options)

    async def partition_key():
        return "cat"

    if is_async:
        options["partitionKey"] = partition_key()
    pager_type = CosmosAsyncItemPaged if is_async else CosmosItemPaged
    pager = pager_type(
        client,
        query,
        options,
        fetch_function=fetch,
        collection_link=context._resource_link,
        page_iterator_class=AsyncQueryIterable if is_async else QueryIterable,
        resource_type=ResourceType.Document,
    )
    if is_async:
        pages = [[item async for item in page] async for page in pager.by_page()]
    else:
        pages = [list(page) for page in pager.by_page()]

    assert [[item["id"] for item in page] for page in pages] == [["fence"], ["couch"]]
    assert options["partitionKey"] == "cat"
    client._GetQueryPlanThroughGateway.assert_called_once()
    fetch.assert_not_called()


@pytest.mark.asyncio
async def test_partition_scoped_rank_query_applies_offset_once(ranked_query_context):
    is_async, create = ranked_query_context
    context, _, fetch = create(
        "SELECT * FROM c ORDER BY RANK FullTextScore(c.text, 'fence') OFFSET 1 LIMIT 1",
        skip=1,
        take=1,
    )

    assert [item["id"] for item in await _drain_context(context, is_async, True)] == ["couch"]
    fetch.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("by_page", [False, True])
async def test_rank_query_plan_failure_does_not_fall_back_to_unranked_results(ranked_query_context, by_page):
    is_async, create = ranked_query_context
    context, client, fetch = create("SELECT TOP 2 * FROM c ORDER BY RANK FullTextScore(c.text, 'fence')")
    client._GetQueryPlanThroughGateway.side_effect = CosmosHttpResponseError(
        status_code=StatusCodes.BAD_REQUEST, message="query plan failed"
    )

    for _ in range(2):
        with pytest.raises(CosmosHttpResponseError, match="query plan failed"):
            await _drain_context(context, is_async, by_page)
    fetch.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    [
        "select top 2 * from c order\nby\trank FullTextScore(c.text, 'fence')",
        "SELECT TOP 2 * FROM c ORDER/* comment */BY -- comment\n RANK FullTextScore(c.text, 'fence')",
        r"""SELECT TOP 2 * FROM c WHERE c.note = 'it\'s -- text' ORDER BY RANK FullTextScore(c.text, 'fence')""",
    ],
)
async def test_rank_query_detection_accepts_sql_whitespace_and_comments(ranked_query_context, query):
    is_async, create = ranked_query_context
    context, client, fetch = create(query)

    assert [item["id"] for item in await _drain_context(context, is_async, True)] == ["fence", "couch"]
    client._GetQueryPlanThroughGateway.assert_called_once()
    fetch.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    [
        None,
        "SELECT * FROM c",
        "SELECT * FROM c ORDER BY c.id",
        "SELECT TOP 2 * FROM c ORDER BY VectorDistance(c.vector, [1, 0, 0])",
        "SELECT * FROM c WHERE FullTextContains(c.text, 'fence')",
        "SELECT * FROM c WHERE c.text = 'ORDER BY RANK FullTextScore'",
        'SELECT c["ORDER BY RANK"] FROM c',
        "SELECT * FROM c -- ORDER BY RANK FullTextScore(c.text, 'fence')",
        "SELECT * FROM c /* ORDER BY RANK FullTextScore(c.text, 'fence') */",
        {"query": "SELECT * FROM c WHERE c.text = @text", "parameters": [
            {"name": "@text", "value": "ORDER BY RANK FullTextScore"}
        ]},
    ],
)
async def test_non_ranking_queries_keep_default_execution(ranked_query_context, query):
    is_async, create = ranked_query_context
    context, client, fetch = create(query)

    assert [item["id"] for item in await _drain_context(context, is_async, True)] == ["couch", "fence"]
    fetch.assert_called_once()
    client._GetQueryPlanThroughGateway.assert_not_called()


@pytest.mark.asyncio
async def test_cross_partition_query_still_uses_error_driven_query_plan(ranked_query_context):
    is_async, create = ranked_query_context
    context, client, fetch = create(
        "SELECT TOP 2 * FROM c ORDER BY RANK FullTextScore(c.text, 'fence')",
        {"enableCrossPartitionQuery": True},
    )
    error = CosmosHttpResponseError(status_code=StatusCodes.BAD_REQUEST, message="query plan required")
    error.sub_status = SubStatusCodes.CROSS_PARTITION_QUERY_NOT_SERVABLE
    fetch.side_effect = error

    assert [item["id"] for item in await _drain_context(context, is_async, True)] == ["fence", "couch"]
    fetch.assert_called_once()
    client._GetQueryPlanThroughGateway.assert_called_once()


def test_mixed_component_rrf_scores_have_exact_expected_order():
    """Pin dense ranking, tied component scores, weighted RRF math, and the
    final descending order without depending on service-generated scores."""
    # Each tuple contains (component score, original result index). The first
    # component is already sorted from highest to lowest, while the second is
    # sorted from lowest to highest, as the query pipeline does before ranking.
    component_scores = [
        [(0.9, 0), (0.8, 1), (0.8, 2), (0.5, 3)],
        [(0.1, 2), (0.2, 0), (0.3, 3), (0.4, 1)],
    ]
    results = [{"id": item_id} for item_id in ("a", "b", "c", "d")]

    ranks = _compute_ranks(component_scores)
    _compute_rrf_scores(ranks, [1, 2], results)

    assert ranks == [
        [1, 2, 2, 3],
        [2, 4, 1, 3],
    ]
    expected_scores = {
        "a": 1 / 61 + 2 / 62,
        "b": 1 / 62 + 2 / 64,
        "c": 1 / 62 + 2 / 61,
        "d": 1 / 63 + 2 / 63,
    }
    for result in results:
        assert result["Score"] == pytest.approx(expected_scores[result["id"]])

    results.sort(key=lambda result: result["Score"], reverse=True)
    assert [result["id"] for result in results] == ["c", "a", "d", "b"]


@pytest.mark.asyncio
@pytest.mark.parametrize("component_count", [1, 2])
@pytest.mark.parametrize("select_value", [False, True])
async def test_hybrid_undefined_projections(hybrid_query_context, component_count, select_value):
    is_async, create = hybrid_query_context
    projection = {} if select_value else {"payload": {}}
    rows = [{"_rid": str(index), "componentScores": [], **projection} for index in range(3)]
    ranking = "FullTextScore(c.missing, 'needle')"
    if component_count == 2:
        ranking = f"RRF({ranking}, FullTextScore(c.otherMissing, 'needle'))"
    query = f"SELECT {'VALUE ' if select_value else ''}c.missing FROM c ORDER BY RANK {ranking} OFFSET 0 LIMIT 3"
    context, _, _ = create([{"0": [rows]} for _ in range(component_count)], query=query, take=3)

    assert await _drain_context(context, is_async, True) == ([] if select_value else [{}, {}, {}])


@pytest.mark.asyncio
@pytest.mark.parametrize("component_count", [1, 2])
async def test_hybrid_scalar_and_object_projections(hybrid_query_context, component_count):
    is_async, create = hybrid_query_context
    payloads = [None, 42, 0, False, "", "string", [10, 20], {}, {"payload": "user", "componentScores": [-100]}]
    rows = [{"_rid": "0", "componentScores": [10] * component_count}]
    rows.extend(
        {"_rid": str(index + 1), "componentScores": [9 - index] * component_count, "payload": payload}
        for index, payload in enumerate(payloads)
    )
    context, client, _ = create(
        [{"0": [rows]} for _ in range(component_count)],
        query="SELECT VALUE c.value FROM c ORDER BY RANK FullTextScore(c.text, 'needle') OFFSET 0 LIMIT 10",
    )
    pager_type = CosmosAsyncItemPaged if is_async else CosmosItemPaged
    fetch = AsyncMock() if is_async else Mock()
    pager = pager_type(
        client,
        context._query,
        context._options,
        fetch_function=fetch,
        collection_link=context._resource_link,
        page_iterator_class=AsyncQueryIterable if is_async else QueryIterable,
        resource_type=ResourceType.Document,
    )
    results = [item async for item in pager] if is_async else list(pager)

    assert results == payloads
    assert [type(value) for value in results[:6]] == [type(value) for value in payloads[:6]]
    fetch.assert_not_called()


@pytest.mark.asyncio
async def test_hybrid_singleton_drains_all_backend_pages_before_offset_limit(hybrid_query_context):
    is_async, create = hybrid_query_context
    rows = [{"_rid": value, "componentScores": [4 - index], "payload": value} for index, value in enumerate("abcd")]
    context, client, _ = create([{"0": [[], [rows[0]], [], [rows[1]], [rows[2]], [rows[3]]]}], skip=1, take=2)

    assert await _drain_context(context, is_async, True) == ["b", "c"]
    assert [call.args[2] for call in client.component_requests.call_args_list] == [None, "1", "2", "3", "4", "5"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "weights, expected",
    [(None, ["c", "a", "b", "d"]), ([1, 2], ["c", "d", "b", "a"]), ([1, -2], ["a", "b", "d", "c"])],
)
@pytest.mark.parametrize("cross_partition", [False, True])
async def test_hybrid_multicomponent_pages_are_coalesced_and_ranked(
    hybrid_query_context, weights, expected, cross_partition
):
    is_async, create = hybrid_query_context
    a, b, c, d = [
        {"_rid": value, "componentScores": scores, "payload": value}
        for value, scores in zip("abcd", [[4, 1], [3, 2], [2, 4], [1, 3]])
    ]
    pages = (
        [{"0": [[a], [b]], "1": [[c], [d]]}, {"0": [[b], [a]], "1": [[c], [d]]}]
        if cross_partition
        else [{"0": [[a, b], [c, d]]}, {"0": [[c, d], [b, a]]}]
    )
    context, client, info = create(
        pages,
        query="SELECT TOP 4 * FROM c ORDER BY RANK RRF(VectorDistance(c.vector, [1, 0]), FullTextScore(c.text, 'fence'))",
        cross_partition=cross_partition,
        take=4,
    )
    info["componentWeights"] = weights

    assert await _drain_context(context, is_async, True) == expected
    component_calls = client.QueryFeed.call_args_list[2:]
    assert len(component_calls) == (8 if cross_partition else 4)


@pytest.mark.asyncio
async def test_hybrid_multiple_components_with_only_one_nonempty_producer(hybrid_query_context):
    is_async, create = hybrid_query_context
    rows = [
        {"_rid": value, "componentScores": scores, "payload": value}
        for value, scores in zip("abc", [[3, 1], [2, 2], [1, 3]])
    ]
    context, _, info = create([{"0": [rows]}, {"0": [[]]}])
    info["componentWeights"] = [1, 10]

    assert await _drain_context(context, is_async, True) == ["c", "b", "a"]


@pytest.mark.asyncio
async def test_hybrid_vector_components_preserve_parameters_and_sort_direction(hybrid_query_context):
    is_async, create = hybrid_query_context
    parameters = [{"name": "@vector", "value": [1, 0]}]
    query = {
        "query": "SELECT TOP 3 * FROM c ORDER BY RANK "
        "RRF(VectorDistance(c.vector, @vector), VectorDistance(c.image, @vector), [2, 1])",
        "parameters": parameters,
    }
    rows = [
        {"_rid": value, "componentScores": scores, "payload": value}
        for value, scores in zip("abc", [[0.1, 3], [0.2, 1], [0.3, 2]])
    ]
    context, client, info = create([{"0": [rows]}, {"0": [list(reversed(rows))]}], query=query)
    info["requiresGlobalStatistics"] = False
    info["componentWeights"] = [2, 1]
    for index, component in enumerate(info["componentQueryInfos"]):
        component["rewrittenQuery"] = (
            f"SELECT VALUE c.value FROM c ORDER BY VectorDistance(c.vector, @vector) /* component {index} */"
        )
    if info["componentQueryInfos"][0].get("orderBy"):
        for component in info["componentQueryInfos"]:
            component["orderBy"] = ["Ascending"]
    else:
        for row in rows:
            row["componentScores"] = [-score for score in row["componentScores"]]
    original_query = copy.deepcopy(query)

    assert await _drain_context(context, is_async, True) == ["a", "b", "c"]
    assert query == original_query
    for call in client.QueryFeed.call_args_list:
        assert call.args[2]["parameters"] == parameters


@pytest.mark.asyncio
async def test_hybrid_undefined_projection_keeps_its_rank_before_limit(hybrid_query_context):
    is_async, create = hybrid_query_context
    rows = [
        {"_rid": "a", "componentScores": [3, 3]},
        {"_rid": "b", "componentScores": [2, 2], "payload": None},
        {"_rid": "c", "componentScores": [1, 1], "payload": 42},
    ]
    context, _, _ = create([{"0": [rows]}, {"0": [rows]}], take=2)

    assert await _drain_context(context, is_async, True) == [None]


@pytest.mark.asyncio
@pytest.mark.parametrize("empty_scores", [False, True])
async def test_hybrid_empty_results_and_undefined_component_scores(hybrid_query_context, empty_scores):
    is_async, create = hybrid_query_context
    rows = (
        [
            {"_rid": "a", "componentScores": [], "payload": {}},
            {"_rid": "b", "componentScores": [1, 2], "payload": "hit"},
        ]
        if empty_scores
        else []
    )
    context, _, _ = create([{"0": [rows]}, {"0": [rows]}])

    assert await _drain_context(context, is_async, True) == (["hit", {}] if empty_scores else [])


@pytest.mark.asyncio
async def test_hybrid_inconsistent_component_scores_fail_explicitly(hybrid_query_context):
    is_async, create = hybrid_query_context
    rows = [{"_rid": "a", "componentScores": [1], "payload": "a"}]
    context, _, _ = create([{"0": [rows]}, {"0": [rows]}])

    with pytest.raises(ValueError, match="invalid number of component scores"):
        await _drain_context(context, is_async, True)


@pytest.mark.asyncio
async def test_hybrid_malformed_envelope_is_not_an_undefined_projection(hybrid_query_context):
    is_async, create = hybrid_query_context
    context, _, _ = create([{"0": [[{"_rid": "a", "payload": {}}]]}])

    with pytest.raises(ValueError, match="missing component scores"):
        await _drain_context(context, is_async, True)


@pytest.mark.asyncio
async def test_hybrid_later_page_error_is_not_a_partial_success(hybrid_query_context):
    is_async, create = hybrid_query_context
    row = {"_rid": "a", "componentScores": [1], "payload": "a"}
    context, client, _ = create([{"0": [[row], []]}])
    original_feed = client.QueryFeed.side_effect

    def fail_second_page(path, collection_id, query, options, range_id, **kwargs):
        if options.get("continuation"):
            raise CosmosHttpResponseError(status_code=StatusCodes.BAD_REQUEST, message="component page failed")
        return original_feed(path, collection_id, query, options, range_id, **kwargs)

    client.QueryFeed.side_effect = fail_second_page
    with pytest.raises(CosmosHttpResponseError, match="component page failed"):
        await _drain_context(context, is_async, True)


def _score_expression(index):
    return (
        f"FullTextScore(c.text{index}, @term, "
        "{documentdb-formattablehybridsearchquery-totaldocumentcount}, "
        f"{{documentdb-formattablehybridsearchquery-totalwordcount-{index}}}, "
        f"{{documentdb-formattablehybridsearchquery-hitcountsarray-{index}}})"
    )


@pytest.mark.parametrize("parameters", [[], [{"name": "@term", "value": "needle"}]])
def test_hybrid_statistics_rewrite_preserves_query_dictionary(parameters):
    statistics = {
        "documentCount": 100,
        "fullTextStatistics": [
            {"totalWordCount": 200, "hitCounts": [3, 4]},
            {"totalWordCount": 500, "hitCounts": [7, 8]},
        ],
    }
    query = {
        "query": f"SELECT VALUE {_score_expression(1)} FROM c WHERE {{documentdb-formattableorderbyquery-filter}}",
        "parameters": parameters,
    }
    original = copy.deepcopy(query)

    assert _format_component_query(query, statistics) == {
        "query": "SELECT VALUE FullTextScore(c.text1, @term, 100, 500, [7,8]) FROM c WHERE true",
        "parameters": parameters,
    }
    assert query == original


@pytest.mark.parametrize("order_by", ["absent", None, []])
def test_hybrid_rewrite_accepts_optional_ordering_metadata(order_by):
    component = {"rewrittenQuery": f"SELECT VALUE {_score_expression(0)} FROM c"}
    if order_by != "absent":
        component.update(orderBy=order_by, orderByExpressions=None, hasNonStreamingOrderBy=False)
    plan = {"componentQueryInfos": [component]}
    original = copy.deepcopy(plan)
    statistics = {"documentCount": 2, "fullTextStatistics": [{"totalWordCount": 16, "hitCounts": [1]}]}

    rewritten = _rewrite_query_infos(plan, statistics)

    assert rewritten[0]["rewrittenQuery"] == "SELECT VALUE FullTextScore(c.text0, @term, 2, 16, [1]) FROM c"
    assert plan == original
    assert rewritten[0].get("orderByExpressions") is None


@pytest.mark.asyncio
@pytest.mark.parametrize("component_count", [1, 2, 4])
async def test_hybrid_scores_in_projections_and_filters_use_statistics_indexes(hybrid_query_context, component_count):
    is_async, create = hybrid_query_context
    parameters = [{"name": "@term", "value": "needle"}, {"name": "@vector", "value": [1, 0]}]
    ranking = "FullTextScore(c.text0, @term)"
    if component_count == 2:
        ranking = f"RRF(VectorDistance(c.vector, @vector), {ranking}, [1, 2])"
    elif component_count == 4:
        ranking = (
            f"RRF(VectorDistance(c.vector, @vector), {ranking}, "
            "VectorDistance(c.image, @vector), FullTextScore(c.text2, @term), [1, 2, 1, 2])"
        )
    query = {
        "query": "SELECT TOP 2 FullTextScore(c.text2, @term) AS score FROM c "
        "WHERE FullTextScore(c.text1, @term) > 0 "
        f"ORDER BY RANK {ranking}",
        "parameters": parameters,
    }
    row = {"_rid": "a", "componentScores": [1] * component_count, "payload": {"score": 2.5}}
    context, client, info = create([{"0": [[row]]} for _ in range(component_count)], query=query)
    for index, component in enumerate(info["componentQueryInfos"]):
        component["rewrittenQuery"] = (
            f"SELECT {_score_expression(2)} AS score FROM c WHERE {_score_expression(1)} > 0 "
            f"AND {{documentdb-formattableorderbyquery-filter}} "
            f"ORDER BY VectorDistance(c.vector, @vector) /* component {index} */"
        )
        if component.get("orderBy"):
            component["orderByExpressions"] = [_score_expression(1)]
    original_query = copy.deepcopy(query)
    original_feed = client.QueryFeed.side_effect
    statistics = {
        "documentCount": 10,
        "fullTextStatistics": [
            {"totalWordCount": 100, "hitCounts": [1, 2]},
            {"totalWordCount": 200, "hitCounts": [3, 4]},
            {"totalWordCount": 300, "hitCounts": [5, 6]},
        ],
    }

    def query_feed(path, collection_id, query, options, range_id, **kwargs):
        if query["query"] == info["globalStatisticsQuery"]:
            assert query["parameters"] == parameters
            return [copy.deepcopy(statistics)], {}
        index = next(i for i in range(component_count) if query["query"].endswith(f"/* component {i} */"))
        assert query == {
            "query": "SELECT FullTextScore(c.text2, @term, 20, 600, [10,12]) AS score FROM c "
            "WHERE FullTextScore(c.text1, @term, 20, 400, [6,8]) > 0 AND true "
            f"ORDER BY VectorDistance(c.vector, @vector) /* component {index} */",
            "parameters": parameters,
        }
        return original_feed(path, collection_id, query, options, range_id, **kwargs)

    client.QueryFeed.side_effect = query_feed

    assert await _drain_context(context, is_async, True) == [{"score": 2.5}]
    assert query == original_query
    aggregated_statistics = copy.deepcopy(statistics)
    aggregated_statistics["documentCount"] *= 2
    for entry in aggregated_statistics["fullTextStatistics"]:
        entry["totalWordCount"] *= 2
        entry["hitCounts"] = [value * 2 for value in entry["hitCounts"]]
    rewritten = _rewrite_query_infos(info, aggregated_statistics, parameters)
    for component in rewritten:
        if component.get("orderBy"):
            assert component["orderByExpressions"] == ["FullTextScore(c.text1, @term, 20, 400, [6,8])"]


@pytest.mark.asyncio
async def test_hybrid_gateway_negotiation_executes_compatible_response_formats(hybrid_query_context):
    is_async, create = hybrid_query_context
    row = {"_rid": "a", "componentScores": [1, 2], "payload": 42}
    context, client, _ = create([{"0": [[row]]}, {"0": [[row]]}])
    plan = client._GetQueryPlanThroughGateway.return_value
    connection_type = AsyncCosmosClientConnection if is_async else CosmosClientConnection
    request = AsyncMock(return_value=plan) if is_async else Mock(return_value=(plan, {}))
    client._CosmosClientConnection__QueryFeed = request
    client._GetQueryPlanThroughGateway = connection_type._GetQueryPlanThroughGateway.__get__(client)

    assert await _drain_context(context, is_async, True) == [42]
    features = request.call_args.args[6]["supportedQueryFeatures"].split(",")
    assert {"HybridSearch", "WeightedRankFusion", "HybridSearchSkipOrderByRewrite"} <= set(features)


@pytest.mark.asyncio
@pytest.mark.parametrize("take, message", [(None, "without TOP or LIMIT"), (50001, "more items than the max")])
async def test_hybrid_query_plan_keeps_top_limit_safety(hybrid_query_context, take, message, monkeypatch):
    is_async, create = hybrid_query_context
    monkeypatch.setenv("AZURE_COSMOS_HYBRID_SEARCH_MAX_ITEMS", "1000")
    context, client, _ = create([{"0": [[]]}], take=take)

    with pytest.raises(ValueError, match=message):
        await _drain_context(context, is_async, True)
    client.QueryFeed.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("ranked_query_context", ["async"], indirect=True)
async def test_hybrid_statistics_split_does_not_count_replaced_producers_twice(hybrid_query_context):
    is_async, create = hybrid_query_context
    row = {"_rid": "a", "componentScores": [1], "payload": "a"}
    context, client, info = create([{"2": [[row]]}])
    original_feed = client.QueryFeed.side_effect
    original_ranges = [
        {"id": "0", "minInclusive": "", "maxExclusive": "80"},
        {"id": "1", "minInclusive": "80", "maxExclusive": "FF"},
    ]
    children = [
        {"id": "2", "minInclusive": "", "maxExclusive": "40"},
        {"id": "3", "minInclusive": "40", "maxExclusive": "80"},
    ]
    split = False
    statistics_ranges = []

    async def read_ranges(**kwargs):
        for item in children + [original_ranges[1]] if split else original_ranges:
            yield item

    def query_feed(path, collection_id, query, options, range_id, **kwargs):
        nonlocal split
        if query == info["globalStatisticsQuery"]:
            statistics_ranges.append(range_id)
            if range_id == "0":
                split = True
                client._routing_map_provider.get_overlapping_ranges.return_value = [children[0]]
                error = CosmosHttpResponseError(status_code=StatusCodes.GONE, message="statistics split")
                error.sub_status = SubStatusCodes.PARTITION_KEY_RANGE_GONE
                raise error
            return [{"documentCount": 1, "fullTextStatistics": [{"totalWordCount": 8, "hitCounts": [1]}]}], {}
        assert "'fence', 3, 24, [3]" in query
        return original_feed(path, collection_id, query, options, range_id, **kwargs)

    client._ReadPartitionKeyRanges = read_ranges
    client.QueryFeed.side_effect = query_feed

    assert await _drain_context(context, is_async, True) == ["a"]
    assert statistics_ranges == ["0", "2", "3", "1"]


@pytest.mark.asyncio
@pytest.mark.parametrize("ranked_query_context", ["async"], indirect=True)
async def test_hybrid_component_split_drains_replacement_pages_once(hybrid_query_context):
    is_async, create = hybrid_query_context
    a, b, c, d = [
        {"_rid": value, "componentScores": [4 - index, 4 - index], "payload": value}
        for index, value in enumerate("abcd")
    ]
    pages = [
        {"2": [[a], [b]], "3": [[], [c]], "1": [[d]]},
        {"2": [[b], [a]], "3": [[c]], "1": [[], [d]]},
    ]
    context, client, info = create(pages, cross_partition=True, skip=1, take=2)
    original_feed = client.QueryFeed.side_effect
    metadata = {
        "containerRID": "container-rid",
        "correlatedActivityId": "query-id",
        "sessionToken": "0:1",
        "excludedLocations": ["West US"],
    }
    context._options.update(metadata)
    context._response_hook = Mock()
    context._raw_response_hook = Mock()
    split = False

    def query_feed(path, collection_id, query, options, range_id, **kwargs):
        nonlocal split
        for key, value in metadata.items():
            assert options[key] == value
        assert kwargs["response_hook"] is context._response_hook
        assert kwargs["raw_response_hook"] is context._raw_response_hook
        if query != info["globalStatisticsQuery"] and range_id == "0":
            assert not split, "Retired producer fetched again after split repair"
            split = True
            client._routing_map_provider.get_overlapping_ranges.return_value = [
                {"id": "2", "minInclusive": "", "maxExclusive": "40"},
                {"id": "3", "minInclusive": "40", "maxExclusive": "80"},
                {"id": "1", "minInclusive": "80", "maxExclusive": "FF"},
            ]
            error = CosmosHttpResponseError(status_code=StatusCodes.GONE, message="component split")
            error.sub_status = SubStatusCodes.PARTITION_KEY_RANGE_GONE
            raise error
        return original_feed(path, collection_id, query, options, range_id, **kwargs)

    client.QueryFeed.side_effect = query_feed

    assert await _drain_context(context, is_async, True) == ["b", "c"]
    assert split
    requests = [call.args for call in client.component_requests.call_args_list]
    expected_requests = [
        (component_index, range_id, str(page_index) if page_index else None)
        for component_index, ranges in enumerate(pages)
        for range_id, backend_pages in ranges.items()
        for page_index in range(len(backend_pages))
    ]
    assert len(requests) == len(expected_requests)
    assert set(requests) == set(expected_requests)


@pytest.mark.asyncio
@pytest.mark.parametrize("ranked_query_context", ["async"], indirect=True)
@pytest.mark.parametrize("stage", ["statistics", "component"])
@pytest.mark.parametrize("failure", ["error", "cancel"])
async def test_hybrid_async_fetch_failure_finishes_active_work(hybrid_query_context, stage, failure):
    is_async, create = hybrid_query_context
    row = {"_rid": "a", "componentScores": [1, 1], "payload": "a"}
    context, client, info = create([{"0": [[row]]}, {"0": [[row]]}])
    original_feed = client.QueryFeed.side_effect
    started = asyncio.Event()
    release = asyncio.Event()
    active = 0

    async def query_feed(path, collection_id, query, options, range_id, **kwargs):
        nonlocal active
        is_statistics = query == info["globalStatisticsQuery"]
        if is_statistics == (stage == "statistics"):
            active += 1
            started.set()
            try:
                await release.wait()
                raise CosmosHttpResponseError(status_code=StatusCodes.BAD_REQUEST, message="fetch failed")
            finally:
                active -= 1
        return original_feed(path, collection_id, query, options, range_id, **kwargs)

    client.QueryFeed.side_effect = query_feed
    consumer = asyncio.create_task(_drain_context(context, is_async, True))
    try:
        await asyncio.wait_for(started.wait(), timeout=5)
        if failure == "cancel":
            consumer.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(consumer, timeout=5)
        else:
            release.set()
            with pytest.raises(CosmosHttpResponseError, match="fetch failed"):
                await asyncio.wait_for(consumer, timeout=5)
        assert active == 0
        if stage == "statistics":
            client.component_requests.assert_not_called()
    finally:
        if not consumer.done():
            consumer.cancel()
        await asyncio.gather(consumer, return_exceptions=True)
