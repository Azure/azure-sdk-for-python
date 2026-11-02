# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Deterministic unit tests for client-side hybrid-search ranking."""

import math
from fractions import Fraction

import pytest

import hybrid_search_data
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
def test_multi_type_vector_search_data_requires_every_rrf_component():
    data = hybrid_search_data.get_multi_type_vector_search_data()
    query_vector = data["parameters"][0]["value"]
    fields = [embedding["path"][1:] for embedding in data["vector_embedding_policy"]["vectorEmbeddings"]]
    component_ranks = {}
    for field in fields:
        ordered_items = sorted(data["items"], key=lambda item: math.dist(item[field], query_vector))
        component_ranks[field] = {item["id"]: rank for rank, item in enumerate(ordered_items, start=1)}

    def fused_ranking(selected_fields):
        scores = {
            item["id"]: sum(Fraction(1, 60 + component_ranks[field][item["id"]]) for field in selected_fields)
            for item in data["items"]
        }
        ordered_ids = sorted(scores, key=scores.get, reverse=True)
        assert all(scores[left] > scores[right] for left, right in zip(ordered_ids[:5], ordered_ids[1:6]))
        return ordered_ids[:5]

    assert fused_ranking(fields) == data["expected_ids"]
    for omitted_field in fields:
        assert fused_ranking([field for field in fields if field != omitted_field]) != data["expected_ids"], omitted_field
