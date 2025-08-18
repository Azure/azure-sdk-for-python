import pytest
from azure.ai.evaluation._evaluators._path_efficiency import PathEfficiencyEvaluator


@pytest.mark.unittest
class TestPathEfficiencyEvaluator:
    def test_exact_match_scenario(self):
        """Test when agent steps exactly match ground truth."""
        evaluator = PathEfficiencyEvaluator()

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

        assert result["path_efficiency_precision_score"] == 1.0
        assert (
            result["path_efficiency_precision_threshold"]
            == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_precision_result"] == "pass"
        assert result["path_efficiency_recall_score"] == 1.0
        assert (
            result["path_efficiency_recall_threshold"]
            == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_recall_result"] == "pass"
        assert result["path_efficiency_f1_score"] == 1.0
        assert (
            result["path_efficiency_f1_threshold"] == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_f1_result"] == "pass"
        assert result["path_efficiency_exact_match_result"] == "pass"
        assert result["path_efficiency_in_order_match_result"] == "pass"
        assert result["path_efficiency_any_order_match_result"] == "pass"

    def test_in_order_match_with_extra_steps(self):
        """Test when agent has extra steps but maintains order."""
        evaluator = PathEfficiencyEvaluator()

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

        assert result["path_efficiency_precision_score"] == 0.75  # 3/4
        assert (
            result["path_efficiency_precision_threshold"]
            == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_precision_result"] == "pass"
        assert result["path_efficiency_recall_score"] == 1.0  # 3/3
        assert (
            result["path_efficiency_recall_threshold"]
            == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_recall_result"] == "pass"
        assert result["path_efficiency_f1_score"] == pytest.approx(0.857, rel=1e-2)
        assert (
            result["path_efficiency_f1_threshold"] == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_f1_result"] == "pass"
        assert result["path_efficiency_exact_match_result"] == "fail"
        assert result["path_efficiency_in_order_match_result"] == "pass"
        assert result["path_efficiency_any_order_match_result"] == "pass"

    def test_any_order_match(self):
        """Test when agent has all steps but in wrong order."""
        evaluator = PathEfficiencyEvaluator()

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

        assert result["path_efficiency_precision_score"] == 1.0
        assert (
            result["path_efficiency_precision_threshold"]
            == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_precision_result"] == "pass"
        assert result["path_efficiency_recall_score"] == 1.0
        assert (
            result["path_efficiency_recall_threshold"]
            == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_recall_result"] == "pass"
        assert result["path_efficiency_f1_score"] == 1.0
        assert (
            result["path_efficiency_f1_threshold"] == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_f1_result"] == "pass"
        assert result["path_efficiency_exact_match_result"] == "fail"
        assert result["path_efficiency_in_order_match_result"] == "fail"
        assert result["path_efficiency_any_order_match_result"] == "pass"

    def test_partial_match(self):
        """Test when agent misses some steps and has extra steps."""
        evaluator = PathEfficiencyEvaluator()

        response = [
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_1", "name": "search", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_2", "name": "wrong_step", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_3", "name": "report", "arguments": {}}],
            },
        ]
        ground_truth = ["search", "analyze", "report"]

        result = evaluator(response=response, ground_truth=ground_truth)

        assert result["path_efficiency_precision_score"] == pytest.approx(0.667, rel=1e-2)  # 2/3
        assert (
            result["path_efficiency_precision_threshold"]
            == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_precision_result"] == "pass"
        assert result["path_efficiency_recall_score"] == pytest.approx(0.667, rel=1e-2)  # 2/3
        assert (
            result["path_efficiency_recall_threshold"]
            == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_recall_result"] == "pass"
        assert result["path_efficiency_f1_score"] == pytest.approx(0.667, rel=1e-2)
        assert (
            result["path_efficiency_f1_threshold"] == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_f1_result"] == "pass"
        assert result["path_efficiency_exact_match_result"] == "fail"
        assert result["path_efficiency_in_order_match_result"] == "fail"
        assert result["path_efficiency_any_order_match_result"] == "fail"

    def test_no_matching_steps(self):
        """Test when agent has no matching steps."""
        evaluator = PathEfficiencyEvaluator()

        response = [
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_1", "name": "wrong1", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_2", "name": "wrong2", "arguments": {}}],
            },
        ]
        ground_truth = ["search", "analyze", "report"]

        result = evaluator(response=response, ground_truth=ground_truth)

        assert result["path_efficiency_precision_score"] == 0.0
        assert (
            result["path_efficiency_precision_threshold"]
            == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_precision_result"] == "fail"
        assert result["path_efficiency_recall_score"] == 0.0
        assert (
            result["path_efficiency_f1_threshold"] == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_recall_result"] == "fail"
        assert result["path_efficiency_recall_score"] == 0.0
        assert (
            result["path_efficiency_f1_threshold"] == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_f1_result"] == "fail"
        assert result["path_efficiency_exact_match_result"] == "fail"
        assert result["path_efficiency_in_order_match_result"] == "fail"
        assert result["path_efficiency_any_order_match_result"] == "fail"

    def test_empty_agent_steps(self):
        """Test when agent has no tool calls."""
        evaluator = PathEfficiencyEvaluator()

        response = []
        ground_truth = ["search", "analyze", "report"]

        result = evaluator(response=response, ground_truth=ground_truth)

        assert result["path_efficiency_precision_score"] == 0.0
        assert (
            result["path_efficiency_precision_threshold"]
            == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_precision_result"] == "fail"
        assert result["path_efficiency_recall_score"] == 0.0
        assert (
            result["path_efficiency_f1_threshold"] == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_recall_result"] == "fail"
        assert result["path_efficiency_f1_score"] == 0.0
        assert (
            result["path_efficiency_f1_threshold"] == PathEfficiencyEvaluator._DEFAULT_PATH_EFFICIENCY_SCORE_THRESHOLD
        )
        assert result["path_efficiency_f1_result"] == "fail"
        assert result["path_efficiency_exact_match_result"] == "fail"
        assert result["path_efficiency_in_order_match_result"] == "fail"
        assert result["path_efficiency_any_order_match_result"] == "fail"

    def test_call_method(self):
        """Test using the __call__ method."""
        evaluator = PathEfficiencyEvaluator(precision_threshold=0.8, recall_threshold=0.8, f1_score_threshold=0.8)

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

        assert result["path_efficiency_precision_score"] == 1.0
        assert result["path_efficiency_recall_score"] == 1.0
        assert result["path_efficiency_f1_score"] == 1.0
        assert result["path_efficiency_precision_result"] == "pass"
        assert result["path_efficiency_recall_result"] == "pass"
        assert result["path_efficiency_f1_result"] == "pass"
        assert result["path_efficiency_precision_threshold"] == 0.8
        assert result["path_efficiency_recall_threshold"] == 0.8
        assert result["path_efficiency_f1_threshold"] == 0.8
        assert result["path_efficiency_exact_match_result"] == "pass"
        assert result["path_efficiency_in_order_match_result"] == "pass"
        assert result["path_efficiency_any_order_match_result"] == "pass"

    def test_invalid_ground_truth(self):
        """Test with invalid ground truth steps."""
        evaluator = PathEfficiencyEvaluator()

        with pytest.raises(TypeError):
            evaluator(response=[], ground_truth="not_a_list")  # type: ignore

        with pytest.raises(ValueError):
            evaluator(response=[], ground_truth=[])
