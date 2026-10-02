# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Score-order assertions and a no-ties guard for live RRF fixtures."""

from contextlib import contextmanager
from collections import Counter
from unittest.mock import patch

from azure.cosmos import ContainerProxy
from azure.cosmos.aio import ContainerProxy as AsyncContainerProxy
from azure.cosmos._execution_context import hybrid_search_aggregator
from azure.cosmos._execution_context.aio import hybrid_search_aggregator as hybrid_search_aggregator_async


@contextmanager
def capture_rrf_scores(index_field="index"):
    scores = {}
    compute_scores = hybrid_search_aggregator._compute_rrf_scores

    def capture(ranks, weights, results):
        compute_scores(ranks, weights, results)
        for result in results:
            scores[result["payload"]["payload"][index_field]] = result["Score"]

    # Scores are internal and cannot be projected by the query. Keep the real
    # calculation, capturing candidates before TOP/OFFSET/LIMIT is applied.
    with patch.object(hybrid_search_aggregator, "_compute_rrf_scores", capture), patch.object(
        hybrid_search_aggregator_async, "_compute_rrf_scores", capture
    ):
        yield scores


def assert_rrf_order(indices, scores, *, offset=0, limit=10, require_unique_scores=False):
    assert scores, "The query did not execute client-side RRF scoring."
    assert len(indices) == min(limit, max(0, len(scores) - offset))
    assert len(indices) == len(set(indices)), "RRF results contain duplicate documents."
    assert set(indices) <= scores.keys(), "RRF results contain an unknown document."
    expected_scores = sorted(scores.values(), reverse=True)[offset : offset + limit]
    assert [scores[index] for index in indices] == expected_scores
    if require_unique_scores:
        counts = Counter(scores.values())
        assert all(counts[scores[index]] == 1 for index in indices), "The fixture produced tied RRF scores."


def query_rrf_items(
    container: ContainerProxy, query, *, offset=0, limit=10, index_field="index", require_unique_scores=True, **kwargs
):
    with capture_rrf_scores(index_field) as scores:
        results = list(container.query_items(query, **kwargs))
    assert_rrf_order(
        [result[index_field] for result in results],
        scores,
        offset=offset,
        limit=limit,
        require_unique_scores=require_unique_scores,
    )
    return results, scores


async def query_rrf_items_async(
    container: AsyncContainerProxy,
    query,
    *,
    offset=0,
    limit=10,
    index_field="index",
    require_unique_scores=True,
    **kwargs
):
    with capture_rrf_scores(index_field) as scores:
        results = [result async for result in container.query_items(query, **kwargs)]
    assert_rrf_order(
        [result[index_field] for result in results],
        scores,
        offset=offset,
        limit=limit,
        require_unique_scores=require_unique_scores,
    )
    return results, scores
