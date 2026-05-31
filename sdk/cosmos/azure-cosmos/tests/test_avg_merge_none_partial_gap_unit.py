# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Unit tests for the cross-partition SELECT VALUE AVG(...) merge guard.

Calls ``_merge_query_results`` directly with fake backend partials, so
the tests are deterministic and need no live Cosmos account.

Any cross-partition AVG must raise ``ValueError``, regardless of whether
the per-partition partial is numeric, ``[None]``, empty, or missing the
``Documents`` key.
"""

import pytest

from azure.cosmos import _base
from azure.cosmos._query_aggregate_utils import (
    _AggregatePartialClassification,
    _classify_aggregate_partial,
    _get_select_value_aggregate_function,
)
from azure.cosmos._routing.feed_range_continuation import (
    _count_page_items_from_partial_result,
)


AVG_QUERY = 'SELECT VALUE AVG(c["value"]) FROM c'

# Inner message raised by _merge_query_results.
INNER_AVG_MERGE_ERROR_SUBSTRING = (
    "VALUE AVG aggregate merge across partitions is not supported client-side."
)

# Outer message produced by _raise_query_merge_value_error.
USER_FACING_WRAPPER_SUBSTRING = "Unsupported query shape for range-scoped pagination"


# ---------------------------------------------------------------------------
# Classifier behavior. Numeric singletons classify as VALUE for AVG;
# `[None]` does not.
# ---------------------------------------------------------------------------


class TestClassifierTypeGateRootCause:

    def test_numeric_singleton_classifies_as_value_for_avg_query(self):
        assert _classify_aggregate_partial([100], AVG_QUERY) == _AggregatePartialClassification.VALUE
        assert _classify_aggregate_partial([1.5], AVG_QUERY) == _AggregatePartialClassification.VALUE

    def test_none_singleton_classifies_as_none_for_avg_query(self):
        # `[None]` fails the `isinstance(row, (int, float))` type gate.
        assert _classify_aggregate_partial([None], AVG_QUERY) == _AggregatePartialClassification.NONE

    def test_aggregate_function_is_detected_for_avg_query(self):
        assert _get_select_value_aggregate_function(AVG_QUERY) == "AVG"

    def test_aggregate_function_detection_is_case_insensitive(self):
        # _get_select_value_aggregate_function uppercases the query
        # before extracting the aggregate name, so the guard in
        # _base._merge_query_results (`== "AVG"`) fires regardless of
        # what case the caller wrote the SQL in.
        assert _get_select_value_aggregate_function('SELECT VALUE avg(c["value"]) FROM c') == "AVG"
        assert _get_select_value_aggregate_function('SELECT VALUE Avg(c["value"]) FROM c') == "AVG"
        assert _get_select_value_aggregate_function('select value avg(c["value"]) from c') == "AVG"
        assert _get_select_value_aggregate_function('SeLeCt VaLuE aVg(c["value"]) FrOm c') == "AVG"

    def test_avg_merge_guard_fires_for_lowercase_avg_query(self):
        # End-to-end check that the guard in _base._merge_query_results
        # also fires for a lowercase AVG query, not just the upper-case
        # form used by the rest of the suite.
        lowercase_avg_query = 'select value avg(c["value"]) from c'
        with pytest.raises(ValueError) as excinfo:
            _base._merge_query_results(
                {"Documents": [100]}, {"Documents": [200]}, lowercase_avg_query,
            )
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

    def test_page_item_count_for_none_partial_treats_it_as_logical_row(self):
        # `[None]` counts as 1 row; a numeric AVG partial counts as 0
        # (it is a merge fragment, not a row).
        assert _count_page_items_from_partial_result({"Documents": [None]}, AVG_QUERY) == 1
        assert _count_page_items_from_partial_result({"Documents": [100]}, AVG_QUERY) == 0


# ---------------------------------------------------------------------------
# Contract: every cross-partition AVG merge must raise.
# ---------------------------------------------------------------------------


class TestAvgMergeNonePartialGap:

    def test_merge_numeric_then_none_raises(self):
        # A=[100], B=[None].
        with pytest.raises(ValueError) as excinfo:
            _base._merge_query_results(
                {"Documents": [100]}, {"Documents": [None]}, AVG_QUERY,
            )
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

    def test_merge_none_then_numeric_raises(self):
        # A=[None], B=[100].
        with pytest.raises(ValueError) as excinfo:
            _base._merge_query_results(
                {"Documents": [None]}, {"Documents": [100]}, AVG_QUERY,
            )
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

    def test_merge_none_then_none_raises(self):
        # Both partitions return [None].
        with pytest.raises(ValueError) as excinfo:
            _base._merge_query_results(
                {"Documents": [None]}, {"Documents": [None]}, AVG_QUERY,
            )
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

    def test_merge_three_way_with_middle_none_raises(self):
        # Any second AVG partial must raise (numeric or [None]). The
        # merge never reaches a third partition for AVG.
        with pytest.raises(ValueError) as excinfo:
            _base._merge_query_results(
                {"Documents": [100]}, {"Documents": [200]}, AVG_QUERY,
            )
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo_none:
            _base._merge_query_results(
                {"Documents": [100]}, {"Documents": [None]}, AVG_QUERY,
            )
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo_none.value)


class TestAvgMergeEmptyPartialGap:
    """Empty ``Documents`` partials must not bypass the AVG guard.

    The Cosmos backend returns ``Documents: []`` for an AVG over a
    partition whose argument is null, missing, or filtered-out on
    every row. Before the fix, the ``if not partial_docs: return
    results`` short-circuit ran before the AVG guard, so empty
    partials silently returned the prior single-partition answer
    as if it were the merged answer.

    These tests pin the post-fix contract: cross-partition AVG raises
    for numeric, ``[None]``, empty, and missing-key partials alike.
    """

    def test_merge_numeric_then_empty_raises(self):
        # A=[100], B=[]. Used to return {"Documents": [100]} silently.
        with pytest.raises(ValueError) as excinfo:
            _base._merge_query_results(
                {"Documents": [100]}, {"Documents": []}, AVG_QUERY,
            )
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

    def test_merge_none_then_empty_raises(self):
        # A=[None], B=[].
        with pytest.raises(ValueError) as excinfo:
            _base._merge_query_results(
                {"Documents": [None]}, {"Documents": []}, AVG_QUERY,
            )
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

    def test_merge_numeric_then_missing_documents_key_raises(self):
        # B has no "Documents" key at all. .get("Documents") returns
        # None (falsy), so this used to fall through the same short-
        # circuit.
        with pytest.raises(ValueError) as excinfo:
            _base._merge_query_results(
                {"Documents": [100]}, {}, AVG_QUERY,
            )
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

    def test_merge_empty_then_numeric_raises(self):
        # A=[], B=[100]. `{"Documents": []}` is a non-empty dict, so
        # the `if not results:` guard does not short-circuit and the
        # AVG guard fires when B arrives.
        with pytest.raises(ValueError) as excinfo:
            _base._merge_query_results(
                {"Documents": []}, {"Documents": [100]}, AVG_QUERY,
            )
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

    def test_merge_empty_then_none_raises(self):
        # A=[], B=[None].
        with pytest.raises(ValueError) as excinfo:
            _base._merge_query_results(
                {"Documents": []}, {"Documents": [None]}, AVG_QUERY,
            )
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

    def test_merge_empty_then_empty_raises(self):
        # Both partitions returned []. Two empty partials still mean
        # the merge ran twice (cross-partition), so the guard fires.
        with pytest.raises(ValueError) as excinfo:
            _base._merge_query_results(
                {"Documents": []}, {"Documents": []}, AVG_QUERY,
            )
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

    def test_merge_three_way_numeric_empty_numeric_raises_on_first_merge(self):
        # 3-way fan-in with an empty middle partial still raises on the
        # first merge call; the third partition is never reached.
        with pytest.raises(ValueError) as excinfo:
            merged = _base._merge_query_results(
                {"Documents": [100]}, {"Documents": []}, AVG_QUERY,
            )
            _base._merge_query_results(merged, {"Documents": [200]}, AVG_QUERY)
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

    def test_merge_three_way_empty_empty_numeric_raises_on_first_merge(self):
        # 3-way fan-in starting with two empty partials then a numeric
        # one. Pins the empty-on-LHS path on the inner merge call.
        with pytest.raises(ValueError) as excinfo:
            merged = _base._merge_query_results(
                {"Documents": []}, {"Documents": []}, AVG_QUERY,
            )
            _base._merge_query_results(merged, {"Documents": [100]}, AVG_QUERY)
        assert INNER_AVG_MERGE_ERROR_SUBSTRING in str(excinfo.value)

    @pytest.mark.parametrize(
        "results,partial",
        [
            ({"Documents": [100]}, {"Documents": []}),
            ({"Documents": [None]}, {"Documents": []}),
            ({"Documents": [100]}, {}),
            ({"Documents": []}, {"Documents": [100]}),
            ({"Documents": []}, {"Documents": [None]}),
            ({"Documents": []}, {"Documents": []}),
        ],
        ids=[
            "numeric_then_empty",
            "none_then_empty",
            "numeric_then_missing_documents_key",
            "empty_then_numeric",
            "empty_then_none",
            "empty_then_empty",
        ],
    )
    def test_empty_partial_merge_error_is_rephrased_for_customer(self, results, partial):
        # The inner ValueError must round-trip through the wrapper to
        # the outer user-facing message, with the inner error chained
        # as __cause__.
        try:
            _base._merge_query_results(results, partial, AVG_QUERY)
        except ValueError as inner:
            with pytest.raises(ValueError) as outer:
                _base._raise_query_merge_value_error(inner)
            outer_message = str(outer.value)
            assert USER_FACING_WRAPPER_SUBSTRING in outer_message
            assert "SELECT VALUE AVG" in outer_message
            assert outer.value.__cause__ is inner
        else:
            pytest.fail(
                "Expected ValueError from _merge_query_results for "
                "({!r}, {!r}); merge returned silently — empty-partial "
                "short-circuit is bypassing the AVG guard.".format(results, partial)
            )


class TestNonAvgEmptyPartialUnchanged:
    """The hoisted AVG guard must not change behavior for non-AVG queries.

    COUNT, SUM, MIN, MAX, plain VALUE, and standard queries must still
    handle empty partials normally.
    """

    def test_count_with_empty_partial_returns_results_unchanged(self):
        merged = _base._merge_query_results(
            {"Documents": [7]}, {"Documents": []}, "SELECT VALUE COUNT(1) FROM c",
        )
        assert merged == {"Documents": [7]}

    def test_sum_with_empty_partial_returns_results_unchanged(self):
        merged = _base._merge_query_results(
            {"Documents": [42]}, {"Documents": []}, 'SELECT VALUE SUM(c["x"]) FROM c',
        )
        assert merged == {"Documents": [42]}

    def test_min_with_empty_partial_returns_results_unchanged(self):
        merged = _base._merge_query_results(
            {"Documents": [3]}, {"Documents": []}, "SELECT VALUE MIN(c.score) FROM c",
        )
        assert merged == {"Documents": [3]}

    def test_max_with_empty_partial_returns_results_unchanged(self):
        merged = _base._merge_query_results(
            {"Documents": [11]}, {"Documents": []}, "SELECT VALUE MAX(c.score) FROM c",
        )
        assert merged == {"Documents": [11]}

    def test_non_aggregate_value_with_empty_partial_returns_results_unchanged(self):
        merged = _base._merge_query_results(
            {"Documents": [1, 2, 3]}, {"Documents": []}, "SELECT VALUE c.x FROM c",
        )
        assert merged == {"Documents": [1, 2, 3]}

    def test_standard_query_with_empty_partial_returns_results_unchanged(self):
        merged = _base._merge_query_results(
            {"Documents": [{"id": "a"}]}, {"Documents": []}, "SELECT * FROM c",
        )
        assert merged == {"Documents": [{"id": "a"}]}

    def test_count_with_empty_then_numeric_returns_partial_result(self):
        # When `results` is {} (initial seed), the `if not results:`
        # short-circuit returns `partial_result` directly and never
        # reaches the AVG guard.
        merged = _base._merge_query_results(
            {}, {"Documents": [7]}, "SELECT VALUE COUNT(1) FROM c",
        )
        assert merged == {"Documents": [7]}

    def test_count_with_empty_documents_lhs_then_numeric_appends(self):
        # `results = {"Documents": []}` is a non-empty dict, so the
        # merge falls through to the normal non-AVG path. Must not
        # raise; exact merged shape is implementation-defined.
        merged = _base._merge_query_results(
            {"Documents": []}, {"Documents": [7]}, "SELECT VALUE COUNT(1) FROM c",
        )
        assert merged.get("Documents") == [7]

    def test_standard_query_with_empty_lhs_and_empty_partial_returns_empty(self):
        # Empty on both sides for non-AVG is a no-op, not a raise.
        merged = _base._merge_query_results(
            {"Documents": []}, {"Documents": []}, "SELECT * FROM c",
        )
        assert merged == {"Documents": []}


class TestAvgMergeNonePartialUserFacingWrapper:
    """Wrapper roundtrip: inner ValueError must surface as the outer
    user-facing message with the original error chained as __cause__."""

    @pytest.mark.parametrize(
        "results,partial",
        [
            ({"Documents": [100]}, {"Documents": [None]}),
            ({"Documents": [None]}, {"Documents": [100]}),
            ({"Documents": [None]}, {"Documents": [None]}),
        ],
        ids=["numeric_then_none", "none_then_numeric", "none_then_none"],
    )
    def test_none_partial_merge_error_is_rephrased_for_customer(self, results, partial):
        try:
            _base._merge_query_results(results, partial, AVG_QUERY)
        except ValueError as inner:
            with pytest.raises(ValueError) as outer:
                _base._raise_query_merge_value_error(inner)
            outer_message = str(outer.value)
            assert USER_FACING_WRAPPER_SUBSTRING in outer_message
            assert "SELECT VALUE AVG" in outer_message
            assert outer.value.__cause__ is inner
        else:
            pytest.fail(
                "Expected ValueError from _merge_query_results for "
                "({!r}, {!r}); merge returned silently.".format(results, partial)
            )

