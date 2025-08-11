# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from unittest.mock import Mock, patch
from typing import List
import pandas as pd

from azure.ai.evaluation._evaluate._evaluate_aoai import _get_single_run_results, OAIEvalRunCreationInfo


class MockOutputItem:
    def __init__(self, id: str, datasource_item_id: int, results: List[dict]):
        self.id = id
        self.datasource_item_id = datasource_item_id
        self.results = results


class MockOutputItemsList:
    def __init__(self, data, has_more=False):
        self.data = data
        self.has_more = has_more


def test_alignment_with_missing_rows(monkeypatch):
    """Ensure missing rows are padded with NaN and not cause row shifts."""
    mock_client = Mock()
    # expected 5 rows, but one (id=2) will be missing
    run_info = OAIEvalRunCreationInfo(
        client=mock_client,
        eval_group_id="grp",
        eval_run_id="run",
        grader_name_map={"grader-1": "rel"},
        expected_rows=5,
    )

    # Mock concluded run results
    mock_run_results = Mock()
    mock_run_results.status = "completed"
    # passed=3 failed=1 -> pass rate 0.75
    mock_run_results.per_testing_criteria_results = [Mock(testing_criteria="grader-1", passed=3, failed=1)]

    # Return rows 0,1,3,4; omit 2
    mock_items = [
        MockOutputItem(id="i0", datasource_item_id=0, results=[{"name": "grader-1", "passed": True, "score": 0.9}]),
        MockOutputItem(id="i1", datasource_item_id=1, results=[{"name": "grader-1", "passed": False, "score": 0.1}]),
        MockOutputItem(id="i3", datasource_item_id=3, results=[{"name": "grader-1", "passed": True, "score": 0.8}]),
        MockOutputItem(id="i4", datasource_item_id=4, results=[{"name": "grader-1", "passed": True, "score": 0.95}]),
    ]

    mock_client.evals.runs.output_items.list.return_value = MockOutputItemsList(data=mock_items, has_more=False)

    with patch(
        "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion", return_value=mock_run_results
    ):
        df, metrics = _get_single_run_results(run_info)

    # Expect 5 rows, with row 2 all NaN except for row_missing flag
    assert len(df) == 5
    # score column exists
    score_col = "outputs.rel.score"
    assert score_col in df.columns

    # Row 2 should be NaN for the score
    assert pd.isna(df.loc[2, score_col])

    # Row alignment: original row 3 score should remain at index 3, not shifted to 2
    assert df.loc[3, score_col] == 0.8

    # Row missing flag set only for the missing row
    missing_flag_col = "outputs.rel.row_missing"
    assert missing_flag_col in df.columns
    assert df.loc[2, missing_flag_col] is True
    assert df[missing_flag_col].sum() == 1

    # Pass rate computed
    assert metrics["rel.pass_rate"] == 0.75
