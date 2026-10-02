# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Deterministic unit tests for client-side hybrid-search ranking."""

import asyncio
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from hybrid_search_helpers import assert_rrf_order, capture_rrf_scores, query_rrf_items, query_rrf_items_async
import hybrid_search_data
from azure.cosmos._execution_context import hybrid_search_aggregator
from azure.cosmos._execution_context.aio import hybrid_search_aggregator as hybrid_search_aggregator_async
from azure.cosmos._execution_context.hybrid_search_aggregator import (
    _compute_ranks,
    _compute_rrf_scores,
)


@pytest.mark.cosmosEmulator
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


@pytest.mark.cosmosEmulator
@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("distinct_scores", [False, True], ids=["tied", "distinct"])
@pytest.mark.parametrize("reverse_rids", [False, True], ids=["original-rids", "different-rids"])
@pytest.mark.parametrize("offset,limit", [(0, 10), (5, 10), (20, 10)])
def test_rrf_pipeline_ranking_and_offset(is_async, distinct_scores, reverse_rids, offset, limit):
    module = hybrid_search_aggregator_async if is_async else hybrid_search_aggregator
    indices = [61, 49, 51, 24, 54, 75, 77, 76, 80, 2, 22, 57, 85]
    text_scores = [9, 8, 8, 7, 7, 7, 6, 5, 4, 3, 2, 1, 0]
    if distinct_scores:
        text_scores[3:6] = [7.1, 7.3, 7.2]
    candidates = [
        {
            "_rid": f"{len(indices) - position if reverse_rids else position:02}",
            "payload": {"componentScores": [0, score], "payload": {"index": index}},
        }
        for position, (index, score) in enumerate(zip(indices, text_scores))
    ]
    query_info = {
        "requiresGlobalStatistics": False,
        "componentQueryInfos": [
            {"rewrittenQuery": "title-component", "orderBy": ["Descending"]},
            {"rewrittenQuery": "text-component", "orderBy": ["Descending"]},
        ],
        "skip": offset,
        "take": limit,
    }
    context = module._HybridSearchContextAggregator(
        SimpleNamespace(_routing_map_provider=None), "container", {}, None, query_info, None, None
    )
    target_ranges = AsyncMock(return_value=[{}]) if is_async else lambda **kwargs: [{}]
    drain_results = AsyncMock(return_value=(candidates, False)) if is_async else lambda _: (candidates, False)

    async def run_async():
        await context._run_hybrid_search()
        return [await context.__anext__() for _ in range(len(context._final_results))]

    with patch.object(context, "_get_target_partition_key_range", target_ranges), patch.object(
        module.document_producer, "_DocumentProducer"
    ) as producer, patch.object(module, "_drain_and_coalesce_results", drain_results), capture_rrf_scores() as scores:
        if is_async:
            producer.return_value.peek = AsyncMock()
            results = asyncio.run(run_async())
        else:
            context._run_hybrid_search()
            results = list(context)

    ranked_indices = [result["index"] for result in results]
    assert_rrf_order(ranked_indices, scores, offset=offset, limit=limit)
    # Pin the current private _rid tie handling with fixed inputs, not a service contract.
    expected_order = [61, 51, 49] if reverse_rids else [61, 49, 51]
    if distinct_scores:
        expected_order.extend([54, 75, 24])
    else:
        expected_order.extend([75, 54, 24] if reverse_rids else [24, 54, 75])
    expected_order.extend(indices[6:])
    assert ranked_indices == expected_order[offset : offset + limit]
    unique_scores = sorted(set(text_scores), reverse=True)
    assert scores == pytest.approx(
        {index: 1 / 61 + 1 / (60 + unique_scores.index(score) + 1) for index, score in zip(indices, text_scores)}
    )


@pytest.mark.cosmosEmulator
@pytest.mark.parametrize("weight", [0.1, 1, 10, -1])
def test_rrf_weighted_scores_with_tied_components(weight):
    ranks = [[1, 2, 2, 3], [3, 2, 2, 1]]
    results = [{"index": index} for index in range(4)]
    _compute_rrf_scores(ranks, [weight, weight], results)
    assert [result["Score"] for result in results] == pytest.approx(
        [
            weight / 61 + weight / 63,
            2 * weight / 62,
            2 * weight / 62,
            weight / 63 + weight / 61,
        ]
    )
    assert results[0]["Score"] == results[3]["Score"]
    assert results[1]["Score"] == results[2]["Score"]


@pytest.mark.cosmosEmulator
@pytest.mark.parametrize("indices", [[75, 77, 85], [54, 77, 85], [24, 77, 85]])
def test_rrf_assertion_accepts_only_boundary_ties(indices):
    scores = {61: 0.9, 49: 0.8, 51: 0.8, 24: 0.7, 54: 0.7, 75: 0.7, 77: 0.6, 85: 0.5}
    assert_rrf_order(indices, scores, offset=5, limit=10)


@pytest.mark.cosmosEmulator
@pytest.mark.parametrize("indices", [[61, 49], [61, 51]])
def test_rrf_assertion_accepts_top_boundary_ties(indices):
    assert_rrf_order(indices, {61: 0.9, 49: 0.8, 51: 0.8, 24: 0.7}, limit=2)


@pytest.mark.cosmosEmulator
@pytest.mark.parametrize(
    "indices",
    [
        [49, 77, 85],  # Wrong offset: a higher-scoring document was not skipped.
        [75, 85, 77],  # Unequal scores returned out of order.
        [75, 77, 77],  # Duplicate result.
        [75, 77],  # Missing result.
        [75, 77, 85, 24],  # Extra result.
        [75, 77, 999],  # Unknown document.
    ],
)
def test_rrf_assertion_rejects_invalid_results(indices):
    scores = {61: 0.9, 49: 0.8, 51: 0.8, 24: 0.7, 54: 0.7, 75: 0.7, 77: 0.6, 85: 0.5}
    with pytest.raises(AssertionError):
        assert_rrf_order(indices, scores, offset=5, limit=10)


@pytest.mark.cosmosEmulator
def test_rrf_assertion_rejects_missing_score_capture():
    with pytest.raises(AssertionError, match="did not execute"):
        assert_rrf_order([], {})


@pytest.mark.cosmosEmulator
@pytest.mark.parametrize("indices,limit", [([24, 54, 75], 3), ([24], 1)])
def test_rrf_assertion_rejects_ties_including_limit_boundary(indices, limit):
    with pytest.raises(AssertionError, match="tied RRF scores"):
        assert_rrf_order(indices, {24: 0.7, 54: 0.7, 75: 0.7}, limit=limit, require_unique_scores=True)


@pytest.mark.cosmosEmulator
def test_hybrid_fixture_has_distinct_frequencies_at_fixed_lengths():
    original = hybrid_search_data.get_full_text_items()["items"]
    items = hybrid_search_data.get_hybrid_search_items()["items"]
    modified = []
    for original_item, item in zip(original, items):
        assert {key: value for key, value in item.items() if key != "text"} == {
            key: value for key, value in original_item.items() if key != "text"
        }
        if item["text"] != original_item["text"]:
            modified.append(item)
            assert len(item["text"].split()) == 100
            assert ("John" in item["text"].split()) == (item["index"] in (2, 57, 85))
    assert len(items) == len(original) == 100
    assert {item["index"] for item in modified} == {61, 49, 51, 24, 54, 75, 77, 76, 80, 2, 22, 57, 85}
    assert sorted(item["text"].count("United States") for item in modified) == list(range(1, 14))


@pytest.mark.cosmosEmulator
@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
def test_rrf_query_helper_preserves_projection_and_options(is_async):
    module = hybrid_search_aggregator_async if is_async else hybrid_search_aggregator
    original_compute = module._compute_rrf_scores
    candidates = [{"payload": {"payload": {"Index": index}}} for index in [24, 54, 75]]
    options = {"partition_key": "1", "max_item_count": 2}

    def query_items(query, **kwargs):
        assert query == "hybrid-query"
        assert kwargs == options
        results = deepcopy(candidates)
        module._compute_rrf_scores([[1, 1, 1], [1, 1, 1]], [1, 1], results)
        return [result["payload"]["payload"] for result in results][1:]

    async def query_items_async(query, **kwargs):
        for result in query_items(query, **kwargs):
            yield result

    if is_async:
        container = SimpleNamespace(query_items=query_items_async)
        results, scores = asyncio.run(
            query_rrf_items_async(
                container, "hybrid-query", offset=1, index_field="Index", require_unique_scores=False, **options
            )
        )
    else:
        container = SimpleNamespace(query_items=query_items)
        results, scores = query_rrf_items(
            container, "hybrid-query", offset=1, index_field="Index", require_unique_scores=False, **options
        )
    assert results == [{"Index": 54}, {"Index": 75}]
    assert scores == pytest.approx({24: 2 / 61, 54: 2 / 61, 75: 2 / 61})
    assert module._compute_rrf_scores is original_compute
