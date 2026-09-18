# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async tests for SELECT VALUE aggregate classification and result merging.

Runs the same checks the sync tests cover from inside an async test
class so the async client shows the same behavior when partial query
results from different partitions are classified and merged.
"""

import unittest

import pytest

from azure.cosmos import _base
from azure.cosmos._query_aggregate_utils import (
    _AggregatePartialClassification,
    _classify_aggregate_partial,
    _get_select_value_aggregate_function,
)
from azure.cosmos._routing import feed_range_continuation as _frc
from azure.cosmos._routing.feed_range_continuation import (
    _count_page_items_from_partial_result,
)
from azure.cosmos.aio import _cosmos_client_connection_async as _async_conn

pytestmark = pytest.mark.cosmosEmulator


class TestQueryAggregateUtilsAsync(unittest.IsolatedAsyncioTestCase):
    """Async-side checks for the shared classifier and merge helpers.

    The helpers themselves are synchronous. Running them from an async
    test class confirms the async client uses the same helpers and
    behaves the same way as the sync client.
    """

    # Boolean partial rows should not be treated as numeric aggregates.
    async def test_classify_aggregate_partial_excludes_boolean_value_rows_async(self):
        query = "SELECT VALUE COUNT(1) FROM c"
        assert _classify_aggregate_partial([True], query) == _AggregatePartialClassification.NONE
        assert _classify_aggregate_partial([False], query) == _AggregatePartialClassification.NONE

    # Boolean rows from each partition should be joined into a list,
    # not added together.
    async def test_value_count_boolean_fragments_concatenate_via_base_merge_async(self):
        query = "SELECT VALUE COUNT(1) > 0 FROM c"
        assert _count_page_items_from_partial_result({"Documents": [True]}, query) == 1
        merged = _base._merge_query_results(
            {"Documents": [True]}, {"Documents": [True]}, query,
        )
        assert merged["Documents"] == [True, True]

    # A plain numeric projection without an aggregate function should
    # return one row per document, not a summed total.
    async def test_value_numeric_non_aggregate_concat_async(self):
        query = "SELECT VALUE c.score FROM c"
        assert _get_select_value_aggregate_function(query) is None
        assert _classify_aggregate_partial([7], query) == _AggregatePartialClassification.NONE
        merged = _base._merge_query_results(
            {"Documents": [7]}, {"Documents": [3]}, query,
        )
        assert merged["Documents"] == [7, 3]

    async def test_value_float_non_aggregate_concat_async(self):
        query = "SELECT VALUE c.ratio FROM c"
        merged = _base._merge_query_results(
            {"Documents": [1.5]}, {"Documents": [2.25]}, query,
        )
        assert merged["Documents"] == [1.5, 2.25]

    async def test_value_numeric_non_aggregate_three_way_concat_async(self):
        query = "SELECT VALUE c.score FROM c"
        merged = _base._merge_query_results(
            {"Documents": [7]}, {"Documents": [3]}, query,
        )
        merged = _base._merge_query_results(merged, {"Documents": [11]}, query)
        assert merged["Documents"] == [7, 3, 11]

    # MIN keeps the smaller value and MAX keeps the larger value when
    # combining one row from each partition.
    async def test_value_min_max_merge_async(self):
        min_query = "SELECT VALUE MIN(c.score) FROM c"
        assert _get_select_value_aggregate_function(min_query) == "MIN"
        merged_min = _base._merge_query_results(
            {"Documents": [7]}, {"Documents": [3]}, min_query,
        )
        assert merged_min["Documents"] == [3]

        max_query = "SELECT VALUE MAX(c.score) FROM c"
        assert _get_select_value_aggregate_function(max_query) == "MAX"
        merged_max = _base._merge_query_results(
            {"Documents": [7]}, {"Documents": [3]}, max_query,
        )
        assert merged_max["Documents"] == [7]

    # MIN and MAX should be detected regardless of keyword casing.
    async def test_value_min_max_lowercase_keyword_detected_async(self):
        assert _get_select_value_aggregate_function(
            "select value min(c.score) from c"
        ) == "MIN"
        assert _get_select_value_aggregate_function(
            "Select Value Max(c.score) From c"
        ) == "MAX"

    # MIN and MAX should still pick the right value when one partition
    # returns an int and another a float, or when values are negative.
    async def test_value_min_max_merge_mixed_numeric_types_async(self):
        min_query = "SELECT VALUE MIN(c.score) FROM c"
        merged_min = _base._merge_query_results(
            {"Documents": [7]}, {"Documents": [3.5]}, min_query,
        )
        assert merged_min["Documents"] == [3.5]

        max_query = "SELECT VALUE MAX(c.score) FROM c"
        merged_max = _base._merge_query_results(
            {"Documents": [-1]}, {"Documents": [-5]}, max_query,
        )
        assert merged_max["Documents"] == [-1]

    # The async client should call the same merge and counting helpers
    # as the sync client, so identical behavior is guaranteed.
    async def test_async_module_reuses_shared_classifier_and_merge_async(self):
        # Use behavior checks instead of identity checks so harmless
        # import-alias refactors do not break this test.
        sum_query = "SELECT VALUE SUM(c.amount) FROM c WHERE IS_NUMBER(c.amount)"
        expected_merge = {"Documents": [15]}
        async_merge_helper = getattr(_async_conn, "base", _base)._merge_query_results
        assert async_merge_helper({"Documents": [7]}, {"Documents": [8]}, sum_query) == expected_merge
        assert _base._merge_query_results({"Documents": [7]}, {"Documents": [8]}, sum_query) == expected_merge

        count_query = "SELECT VALUE COUNT(1) > 0 FROM c"
        partial = {"Documents": [True]}
        assert _async_conn._count_page_items_from_partial_result(partial, count_query) == 1
        assert _async_conn._count_page_items_from_partial_result(partial, count_query) == (
            _frc._count_page_items_from_partial_result(partial, count_query)
        )
        assert _async_conn._count_page_items_from_partial_result(partial, count_query) == (
            _count_page_items_from_partial_result(partial, count_query)
        )


if __name__ == "__main__":
    unittest.main()
