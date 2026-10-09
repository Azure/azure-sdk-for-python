# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Deterministic unit tests for client-side hybrid-search ranking."""

import copy
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from azure.cosmos import documents
from azure.cosmos.aio import CosmosClient  # noqa: F401 - initialize async execution contexts
from azure.cosmos._cosmos_responses import CosmosAsyncItemPaged, CosmosItemPaged
from azure.cosmos._execution_context import execution_dispatcher
from azure.cosmos._execution_context.aio import execution_dispatcher as execution_dispatcher_async
from azure.cosmos._execution_context.hybrid_search_aggregator import (
    _compute_ranks,
    _compute_rrf_scores,
)
from azure.cosmos.http_constants import ResourceType, StatusCodes, SubStatusCodes
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
