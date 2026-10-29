import pytest
from azure.ai.evaluation import QAEvaluator
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestQAEvaluator:
    def test_is_reasoning_model_passed_to_sub_evaluators(self, mock_model_config):
        """Test that is_reasoning_model is passed to all LLM-based sub-evaluators"""
        qa_evaluator = QAEvaluator(model_config=mock_model_config, is_reasoning_model=True)

        # Verify that all LLM-based sub-evaluators have is_reasoning_model=True
        for evaluator in qa_evaluator._evaluators:
            # F1ScoreEvaluator doesn't use LLM, so it doesn't have _is_reasoning_model
            if hasattr(evaluator, "_is_reasoning_model"):
                assert (
                    evaluator._is_reasoning_model is True
                ), f"{type(evaluator).__name__} did not receive is_reasoning_model=True"

    def test_is_reasoning_model_defaults_to_false(self, mock_model_config):
        """Test that is_reasoning_model defaults to False for sub-evaluators"""
        qa_evaluator = QAEvaluator(model_config=mock_model_config)

        # Verify that all LLM-based sub-evaluators have is_reasoning_model=False
        for evaluator in qa_evaluator._evaluators:
            if hasattr(evaluator, "_is_reasoning_model"):
                assert (
                    evaluator._is_reasoning_model is False
                ), f"{type(evaluator).__name__} did not default to is_reasoning_model=False"

    def test_invalid_threshold_type_error_metadata(self, mock_model_config):
        """Test that an invalid threshold type raises EvaluationException with correct metadata."""
        with pytest.raises(EvaluationException) as exc_info:
            QAEvaluator(model_config=mock_model_config, groundedness_threshold="not-a-number")  # type: ignore

        exc = exc_info.value
        assert exc.blame == ErrorBlame.USER_ERROR
        assert exc.category == ErrorCategory.INVALID_VALUE
        assert exc.target == ErrorTarget.QA_EVALUATOR
