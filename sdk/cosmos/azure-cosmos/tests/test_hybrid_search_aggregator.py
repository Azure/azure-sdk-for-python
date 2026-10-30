# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Deterministic unit tests for client-side hybrid-search ranking."""

import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from azure.cosmos.aio import CosmosClient  # noqa: F401 - needed to resolve circular imports
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._execution_context import hybrid_search_aggregator as sync_aggregator
from azure.cosmos._execution_context.aio import hybrid_search_aggregator as async_aggregator
from azure.cosmos._execution_context.hybrid_search_aggregator import (
    _compute_ranks,
    _compute_rrf_scores,
    _get_document_rid,
    _rank_results,
)

pytestmark = pytest.mark.cosmosEmulator


def _result(document_rid, scores, payload=None, prefix=b"\x01" * 8):
    rid = base64.b64encode(prefix + document_rid.to_bytes(8, "little")).decode("ascii").replace("/", "-")
    return {"_rid": rid, "payload": {"componentScores": scores, "payload": payload}}


@pytest.mark.parametrize(
    "competition, expected",
    [(False, [1, 2, 3, 4, 5]), (True, [1, 2, 2, 2, 5])],
)
def test_component_ranks_are_ordinal_or_competition_not_dense(competition, expected):
    scores = [[(score, index) for index, score in enumerate([10, 5, 5, 5, 0])]]
    assert _compute_ranks(scores, competition) == [expected]


def test_mixed_component_rrf_scores_have_exact_expected_order():
    """Pin ordinal ranking, tied component scores, weighted RRF math, and the
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
        [1, 2, 3, 4],
        [2, 4, 1, 3],
    ]
    expected_scores = {
        "a": 1 / 61 + 2 / 62,
        "b": 1 / 62 + 2 / 64,
        "c": 1 / 63 + 2 / 61,
        "d": 1 / 64 + 2 / 63,
    }
    for result in results:
        assert result["Score"] == pytest.approx(expected_scores[result["id"]])

    results.sort(key=lambda result: result["Score"], reverse=True)
    assert [result["id"] for result in results] == ["c", "a", "b", "d"]


def test_document_rid_is_little_endian_document_portion_not_encoded_order():
    low = _result(255, [], prefix=b"\xff" * 8)["_rid"]
    high = _result(256, [], prefix=b"\x00" * 8)["_rid"]
    assert "-" in low
    assert _get_document_rid(low) == 255
    assert _get_document_rid(high) == 256
    assert _get_document_rid(_result(0x0FEDCBA987654321, [])["_rid"]) == 0x0FEDCBA987654321
    # The prefix is not part of the document number.
    assert _get_document_rid(_result(255, [])["_rid"]) == 255
    same_prefix_low = _result(255, [])["_rid"]
    same_prefix_high = _result(256, [])["_rid"]
    assert same_prefix_low > same_prefix_high
    with pytest.raises(ValueError, match="16-byte"):
        _get_document_rid(base64.b64encode(b"\x00" * 8).decode("ascii"))
    with pytest.raises(ValueError):
        _get_document_rid("not a resource ID")


@pytest.mark.parametrize("weights", [[1, 2], [1, -2]])
def test_component_ties_follow_query_plan_direction_and_preserve_weights(weights, monkeypatch):
    results = [_result(255, [5, 0.2]), _result(1, [10, 0.1]), _result(256, [5, 0.2])]
    info = {
        "componentQueryInfos": [{"orderBy": ["Descending"]}, {"orderBy": ["Ascending"]}],
        "componentWeights": weights,
    }
    decode = Mock(wraps=_get_document_rid)
    monkeypatch.setattr(sync_aggregator, "_get_document_rid", decode)
    _rank_results(results, info)
    expected = {
        1: weights[0] / 61 + weights[1] / 61,
        255: weights[0] / 63 + weights[1] / 62,
        256: weights[0] / 62 + weights[1] / 63,
    }
    assert decode.call_count == len(results)
    for result in results:
        assert result["Score"] == pytest.approx(expected[_get_document_rid(result["_rid"])])
    assert [_get_document_rid(result["_rid"]) for result in results] == (
        [1, 255, 256] if weights[1] > 0 else [256, 255, 1]
    )


@pytest.mark.parametrize("competition, expected", [(False, [256, 1, 255]), (True, [256, 255, 1])])
def test_final_rrf_ties_are_numeric_rid_descending(competition, expected):
    info = {"componentQueryInfos": [{}, {"orderBy": ["Ascending"]}]}
    for incoming in ([1, 255, 256], [256, 255, 1]):
        results = [_result(rid, [5, 5]) for rid in incoming]
        _rank_results(results, info, competition)
        assert [_get_document_rid(result["_rid"]) for result in results] == expected
        scores = {_get_document_rid(result["_rid"]): result["Score"] for result in results}
        assert scores[1] == scores[256]


@pytest.mark.parametrize("module", [sync_aggregator, async_aggregator], ids=["sync", "async"])
@pytest.mark.parametrize("competition", [False, True], ids=["ordinal", "competition"])
@pytest.mark.asyncio
async def test_query_snapshots_ranking_mode_and_preserves_dedup_payload_and_window(module, competition, monkeypatch):
    is_async = module is async_aggregator
    monkeypatch.setenv(Constants.HS_USE_COMPETITION_RANKING_CONFIG, "TrUe" if competition else "false")
    info = {
        "requiresGlobalStatistics": False,
        "componentQueryInfos": [
            {"orderBy": ["Descending"], "rewrittenQuery": "first"},
            {"orderBy": ["Ascending"], "rewrittenQuery": "second"},
        ],
        "skip": 1,
        "take": 1,
    }
    original = _result(1, [5, 5], {"id": "old"})
    replacement = _result(1, [5, 5], {"id": "new"})
    middle = _result(255, [5, 5], "projected scalar")
    high = _result(256, [5, 5], {"id": "high"})
    producers = []
    for rows in ([original, middle, high], [replacement, middle]):
        peek = AsyncMock(return_value=rows[0]) if is_async else Mock(return_value=rows[0])
        producers.append(SimpleNamespace(peek=peek, _ex_context=SimpleNamespace(_buffer=rows[1:])))
    monkeypatch.setattr(module.document_producer, "_DocumentProducer", Mock(side_effect=producers))
    client = SimpleNamespace(_routing_map_provider=None)
    context = module._HybridSearchContextAggregator(client, "colls/test", {}, None, info, None, None)
    context._get_target_partition_key_range = AsyncMock(return_value=[{}]) if is_async else Mock(return_value=[{}])
    # Changing the environment after query initialization must not change this query's mode.
    monkeypatch.setenv(Constants.HS_USE_COMPETITION_RANKING_CONFIG, "false" if competition else "true")
    assert context._use_competition_ranking is competition
    if is_async:
        await context._run_hybrid_search()
        actual = [item async for item in context]
    else:
        context._run_hybrid_search()
        actual = list(context)
    assert actual == (["projected scalar"] if competition else [{"id": "new"}])
    assert "Score" not in original
    assert "Score" in replacement
    assert replacement["_rid"] == original["_rid"]


@pytest.mark.parametrize("module", [sync_aggregator, async_aggregator], ids=["sync", "async"])
@pytest.mark.parametrize("second_scores", [[5, 0.2], []], ids=["empty-first", "all-empty"])
@pytest.mark.asyncio
async def test_query_uses_plan_component_count_for_empty_scores(module, second_scores, monkeypatch):
    is_async = module is async_aggregator
    info = {
        "requiresGlobalStatistics": False,
        "componentQueryInfos": [
            {"orderBy": ["Descending"], "rewrittenQuery": "first"},
            {"orderBy": ["Ascending"], "rewrittenQuery": "second"},
        ],
        "componentWeights": [1, 2],
        "skip": 0,
        "take": 2,
    }
    empty = _result(255, [], {"id": "empty"})
    second = _result(256, second_scores, {"id": "second"})
    producers = [
        SimpleNamespace(
            peek=AsyncMock(return_value=row) if is_async else Mock(return_value=row),
            _ex_context=SimpleNamespace(_buffer=[]),
        )
        for row in (empty, second)
    ]
    monkeypatch.setattr(module.document_producer, "_DocumentProducer", Mock(side_effect=producers))
    client = SimpleNamespace(_routing_map_provider=None)
    monkeypatch.delenv(Constants.HS_USE_COMPETITION_RANKING_CONFIG, raising=False)
    context = module._HybridSearchContextAggregator(client, "colls/test", {}, None, info, None, None)
    context._get_target_partition_key_range = AsyncMock(return_value=[{}]) if is_async else Mock(return_value=[{}])
    if is_async:
        await context._run_hybrid_search()
        actual = [item async for item in context]
    else:
        context._run_hybrid_search()
        actual = list(context)
    # The existing -999999 fallback sorts last descending and first ascending;
    # when all scores are empty, numeric RID ties give the same ordinal ranks.
    assert empty["Score"] == pytest.approx(1 / 62 + 2 / 61)
    assert second["Score"] == pytest.approx(1 / 61 + 2 / 62)
    assert actual == [{"id": "empty"}, {"id": "second"}]
    assert empty["payload"]["componentScores"] == []
    assert second["payload"]["componentScores"] == second_scores


@pytest.mark.parametrize("module", [sync_aggregator, async_aggregator], ids=["sync", "async"])
def test_ranking_mode_uses_environment_not_options(module, monkeypatch):
    client = SimpleNamespace(_routing_map_provider=None)
    monkeypatch.delenv(Constants.HS_USE_COMPETITION_RANKING_CONFIG, raising=False)
    options = {"hybridSearchUseCompetitionRanking": True}
    default = module._HybridSearchContextAggregator(client, "colls/test", options, None, {}, None, None)
    assert default._use_competition_ranking is False
    for value, expected in (("TrUe", True), ("false", False), ("1", False), ("", False)):
        monkeypatch.setenv(Constants.HS_USE_COMPETITION_RANKING_CONFIG, value)
        options = {"hybridSearchUseCompetitionRanking": not expected}
        context = module._HybridSearchContextAggregator(client, "colls/test", options, None, {}, None, None)
        assert context._use_competition_ranking is expected
        assert options == {"hybridSearchUseCompetitionRanking": not expected}
