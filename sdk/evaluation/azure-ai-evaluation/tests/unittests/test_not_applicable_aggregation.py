# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pandas as pd
import pytest
from azure.ai.evaluation._evaluate._evaluate import (
    _exclude_not_applicable_from_aggregation,
    _aggregate_metrics,
)


@pytest.mark.unittest
class TestNotApplicableAggregation:
    """Tests for not-applicable result exclusion from aggregation."""

    def test_exclude_not_applicable_comprehensive(self):
        """Test that not-applicable scores are excluded and mean is calculated correctly."""
        df = pd.DataFrame(
            {
                "tool_call_accuracy": [5.0, 3.0, 4.0, 3.0],
                "tool_call_accuracy_reason": [
                    "Good tool usage",
                    "Not applicable: No tool calls found",
                    "Partial success",
                    "Not applicable: Missing tool definitions",
                ],
                "tool_selection": [1, 1, 0, 1],
                "tool_selection_reason": [
                    "Not applicable: No tools",
                    "Good selection",
                    "Wrong tool",
                    "Good selection",
                ],
            }
        )

        result_df = _exclude_not_applicable_from_aggregation(df.copy())

        # tool_call_accuracy: rows 1 and 3 should be None
        assert result_df["tool_call_accuracy"].iloc[0] == 5.0
        assert pd.isna(result_df["tool_call_accuracy"].iloc[1])
        assert result_df["tool_call_accuracy"].iloc[2] == 4.0
        assert pd.isna(result_df["tool_call_accuracy"].iloc[3])
        # Mean: (5.0 + 4.0) / 2 = 4.5
        assert result_df["tool_call_accuracy"].mean() == 4.5

        # tool_selection: row 0 should be None
        assert pd.isna(result_df["tool_selection"].iloc[0])
        assert result_df["tool_selection"].iloc[1] == 1
        assert result_df["tool_selection"].iloc[2] == 0
        assert result_df["tool_selection"].iloc[3] == 1
        # Mean: (1 + 0 + 1) / 3 ≈ 0.67
        assert abs(result_df["tool_selection"].mean() - 2.0 / 3) < 0.0001


    def test_aggregate_metrics_with_not_applicable(self):
        """Test complete aggregation pipeline with not-applicable scores."""
        df = pd.DataFrame(
            {
                "outputs.eval1.score": [1.0, 2.0, 3.0, 4.0, 5.0],
                "outputs.eval1.score_reason": [
                    "Valid",
                    "Not applicable: Missing data",
                    "Valid",
                    "Not applicable: No context",
                    "Valid",
                ],
                "outputs.eval2.metric": [1.0, 2.0, 3.0, 4.0, 5.0],
                "outputs.eval2.metric_reason": ["Good", "Good", "Good", "Good", "Good"],
            }
        )

        result_metrics = _aggregate_metrics(df.copy(), evaluators={})

        # score: (1.0 + 3.0 + 5.0) / 3 = 3.0 (excluding not-applicable)
        assert "eval1.score" in result_metrics
        assert result_metrics["eval1.score"] == 3.0

        # metric: (1.0 + 2.0 + 3.0 + 4.0 + 5.0) / 5 = 3.0 (no exclusions)
        assert "eval2.metric" in result_metrics
        assert result_metrics["eval2.metric"] == 3.0

    def test_aggregate_metrics_all_not_applicable(self):
        """Test aggregation when all scores are not-applicable - metric should be omitted."""
        df = pd.DataFrame(
            {
                "outputs.eval1.score": [3.0, 3.0, 3.0],
                "outputs.eval1.score_reason": [
                    "Not applicable: No data",
                    "Not applicable: No data",
                    "Not applicable: No data",
                ],
            }
        )

        result_metrics = _aggregate_metrics(df.copy(), evaluators={})

        # When all values are not-applicable, metric should not appear in results
        assert "eval1.score" not in result_metrics
