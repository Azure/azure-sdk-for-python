import pytest
from azure.ai.evaluation import (
    TaskNavigationEfficiencyEvaluator,
    TaskNavigationEfficiencyMatchingMode,
)


@pytest.mark.unittest
class TestTaskNavigationEfficiencyEvaluator:
    def test_exact_match_scenario(self):
        """Test when agent steps exactly match ground truth."""
        evaluator = TaskNavigationEfficiencyEvaluator(matching_mode=TaskNavigationEfficiencyMatchingMode.EXACT_MATCH)

        response = [
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_1", "name": "search", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_2", "name": "analyze", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_3", "name": "report", "arguments": {}}],
            },
        ]
        ground_truth = ["search", "analyze", "report"]

        result = evaluator(response=response, ground_truth=ground_truth)
        assert result["task_navigation_efficiency_result"] == "pass"
        assert "properties" in result
        assert result["properties"]["precision_score"] == 1.0
        assert result["properties"]["recall_score"] == 1.0
        assert result["properties"]["f1_score"] == 1.0

    def test_in_order_match_with_extra_steps(self):
        """Test when agent has extra steps but maintains order."""
        evaluator = TaskNavigationEfficiencyEvaluator(matching_mode=TaskNavigationEfficiencyMatchingMode.IN_ORDER_MATCH)

        response = [
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_1", "name": "search", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_2", "name": "extra_step", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_3", "name": "analyze", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_4", "name": "report", "arguments": {}}],
            },
        ]
        ground_truth = ["search", "analyze", "report"]

        result = evaluator(response=response, ground_truth=ground_truth)
        assert result["task_navigation_efficiency_result"] == "pass"
        assert result["properties"]["precision_score"] == 0.75  # 3/4
        assert result["properties"]["recall_score"] == 1.0  # 3/3
        assert result["properties"]["f1_score"] == pytest.approx(0.857, rel=1e-2)

    def test_any_order_match(self):
        """Test when agent has all steps but in wrong order."""
        evaluator = TaskNavigationEfficiencyEvaluator(
            matching_mode=TaskNavigationEfficiencyMatchingMode.ANY_ORDER_MATCH
        )

        response = [
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_1", "name": "report", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_2", "name": "search", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_3", "name": "analyze", "arguments": {}}],
            },
        ]
        ground_truth = ["search", "analyze", "report"]

        result = evaluator(response=response, ground_truth=ground_truth)
        assert result["task_navigation_efficiency_result"] == "pass"
        assert result["properties"]["precision_score"] == 1.0
        assert result["properties"]["recall_score"] == 1.0
        assert result["properties"]["f1_score"] == 1.0

    def test_exact_match_failure(self):
        """Test when exact match fails but other matches succeed."""
        exact_evaluator = TaskNavigationEfficiencyEvaluator(
            matching_mode=TaskNavigationEfficiencyMatchingMode.EXACT_MATCH
        )
        in_order_evaluator = TaskNavigationEfficiencyEvaluator(
            matching_mode=TaskNavigationEfficiencyMatchingMode.IN_ORDER_MATCH
        )

        response = [
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_1", "name": "search", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_2", "name": "extra_step", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_3", "name": "analyze", "arguments": {}}],
            },
        ]
        ground_truth = ["search", "analyze"]

        exact_result = exact_evaluator(response=response, ground_truth=ground_truth)
        assert exact_result["task_navigation_efficiency_result"] == "fail"

        in_order_result = in_order_evaluator(response=response, ground_truth=ground_truth)
        assert in_order_result["task_navigation_efficiency_result"] == "pass"

    def test_invalid_ground_truth(self):
        """Test with invalid ground truth steps."""
        evaluator = TaskNavigationEfficiencyEvaluator()

        with pytest.raises(TypeError):
            evaluator(response=[], ground_truth="not_a_list")  # type: ignore

        with pytest.raises(ValueError):
            evaluator(response=[], ground_truth=[])

    def test_tuple_format_with_parameters(self):
        """Test tuple format with exact parameter matching."""
        evaluator = TaskNavigationEfficiencyEvaluator(matching_mode=TaskNavigationEfficiencyMatchingMode.EXACT_MATCH)

        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_1",
                        "name": "search",
                        "arguments": {"query": "weather", "location": "NYC"},
                    }
                ],
            },
        ]

        # Ground truth with tuple format: (tool_names, parameters_dict)
        ground_truth = (
            ["search"],
            {"search": {"query": "weather", "location": "NYC"}},
        )

        result = evaluator(response=response, ground_truth=ground_truth)
        assert result["task_navigation_efficiency_result"] == "pass"
        assert result["properties"]["precision_score"] == 1.0
        assert result["properties"]["recall_score"] == 1.0
        assert result["properties"]["f1_score"] == 1.0

    def test_matching_mode_validation(self):
        """Test validation of matching_mode parameter."""
        # Test valid string mode
        evaluator1 = TaskNavigationEfficiencyEvaluator(matching_mode="exact_match")
        assert evaluator1.matching_mode == TaskNavigationEfficiencyMatchingMode.EXACT_MATCH

        # Test valid enum mode
        evaluator2 = TaskNavigationEfficiencyEvaluator(
            matching_mode=TaskNavigationEfficiencyMatchingMode.IN_ORDER_MATCH
        )
        assert evaluator2.matching_mode == TaskNavigationEfficiencyMatchingMode.IN_ORDER_MATCH

        # Test invalid string mode
        with pytest.raises(ValueError):
            TaskNavigationEfficiencyEvaluator(matching_mode="invalid_mode")

        # Test invalid type for mode
        with pytest.raises(Exception):  # EvaluationException
            TaskNavigationEfficiencyEvaluator(matching_mode=123)  # type: ignore
