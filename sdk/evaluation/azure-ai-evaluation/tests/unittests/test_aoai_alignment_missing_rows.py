# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import List
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from azure.ai.evaluation._evaluate._evaluate_aoai import (
    OAIEvalRunCreationInfo,
    _get_single_run_results,
)


class MockOutputItem:
    def __init__(self, id: str, datasource_item_id: int, results: List[dict]):
        self.id = id
        self.datasource_item_id = datasource_item_id
        self.results = results


class MockOutputItemsList:
    def __init__(self, data, has_more=False):
        self.data = data
        self.has_more = has_more


@pytest.mark.unittest
def test_aoai_results_preserve_order_with_unordered_output_items(caplog):
    """AOAI output_items can arrive unordered; results should align to row ids (0..N-1)."""
    mock_client = Mock()
    expected_rows = 5
    run_info = OAIEvalRunCreationInfo(
        client=mock_client,
        eval_group_id="grp",
        eval_run_id="run",
        grader_name_map={"grader-1": "rel"},
        expected_rows=expected_rows,
    )

    # Completed run; pass_rate comes from per_testing_criteria_results
    mock_run_results = Mock()
    mock_run_results.status = "completed"
    mock_run_results.per_testing_criteria_results = [Mock(testing_criteria="grader-1", passed=4, failed=1)]

    # Unordered items: ids [3,0,4,1,2]; score equals its id for easy checks
    unordered_items = [
        MockOutputItem(id="i3", datasource_item_id=3, results=[{"name": "grader-1", "passed": True, "score": 3.0}]),
        MockOutputItem(id="i0", datasource_item_id=0, results=[{"name": "grader-1", "passed": True, "score": 0.0}]),
        MockOutputItem(id="i4", datasource_item_id=4, results=[{"name": "grader-1", "passed": False, "score": 4.0}]),
        MockOutputItem(id="i1", datasource_item_id=1, results=[{"name": "grader-1", "passed": True, "score": 1.0}]),
        MockOutputItem(id="i2", datasource_item_id=2, results=[{"name": "grader-1", "passed": True, "score": 2.0}]),
    ]
    mock_client.evals.runs.output_items.list.return_value = MockOutputItemsList(data=unordered_items, has_more=False)

    caplog.set_level(logging.WARNING, logger="azure.ai.evaluation._evaluate._evaluate_aoai")

    with patch(
        "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion",
        return_value=mock_run_results,
    ):
        df, metrics = _get_single_run_results(run_info)

    # Shape and index
    assert len(df) == expected_rows
    assert list(df.index) == list(range(expected_rows))

    score_col = "outputs.rel.score"
    assert score_col in df.columns

    # Each row i should have score == float(i), proving correct alignment after sort/reindex
    for i in range(expected_rows):
        assert df.loc[i, score_col] == float(i)

    # No missing-row padding in this test; the row_missing flag should not exist
    missing_flag_col = "outputs.rel.row_missing"
    assert missing_flag_col not in df.columns

    # Pass rate surfaced from per_testing_criteria_results
    assert metrics["rel.pass_rate"] == 4 / 5

    # No warning about padding missing rows in this scenario
    assert not any(
        "missing row(s) padded with NaN for alignment" in rec.message
        for rec in caplog.records
        if rec.levelno >= logging.WARNING
    )
