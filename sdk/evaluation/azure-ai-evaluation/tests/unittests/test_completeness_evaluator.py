from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation import ResponseCompletenessEvaluator
from azure.ai.evaluation._exceptions import EvaluationException


async def completeness_response1_async_mock():
    return {
        "llm_output": '<S0>Let\'s think step by step: The ground truth states "The capital of Japan is Tokyo." The response is "The capital of Japan." The response does not specify what the capital is; it only repeats part of the question and omits the key information ("Tokyo"). Therefore, none of the necessary information from the ground truth is present in the response.</S0>\n<S1>The response is fully incomplete because it does not provide the answer ("Tokyo") at all.</S1>\n<S2>1</S2>',
        "input_token_count": 1354,
        "output_token_count": 108,
        "total_token_count": 1462,
        "finish_reason": "stop",
        "model_id": "gpt-4.1-2025-04-14",
        "sample_input": '[{"role": "user", "content": "{\\"response\\": \\"The capital of Japan\\", \\"ground_truth\\": \\"The capital of Japan is Tokyo.\\"}"}]',
        "sample_output": '[{"role": "assistant", "content": "<S0>Let\'s think step by step: The ground truth states \\"The capital of Japan is Tokyo.\\" The response is \\"The capital of Japan.\\" The response does not specify what the capital is; it only repeats part of the question and omits the key information (\\"Tokyo\\"). Therefore, none of the necessary information from the ground truth is present in the response.</S0>\\n<S1>The response is fully incomplete because it does not provide the answer (\\"Tokyo\\") at all.</S1>\\n<S2>1</S2>"}]',
    }


async def completeness_response2_async_mock():
    return {
        "llm_output": '<S0>Let\'s think step by step: The ground truth contains a single statement: "The capital of Japan is Tokyo." The response exactly matches this statement without omitting or altering any information. There are no additional claims or missing details to consider. According to the definitions, a fully complete response should perfectly contain all necessary and relevant information from the ground truth.</S0>\n<S1>The response is a perfect match to the ground truth, with no missing or incorrect information.</S1>\n<S2>5</S2>',
        "input_token_count": 1356,
        "output_token_count": 107,
        "total_token_count": 1463,
        "finish_reason": "stop",
        "model_id": "gpt-4.1-2025-04-14",
        "sample_input": '[{"role": "user", "content": "{\\"response\\": \\"The capital of Japan is Tokyo.\\", \\"ground_truth\\": \\"The capital of Japan is Tokyo.\\"}"}]',
        "sample_output": '[{"role": "assistant", "content": "<S0>Let\'s think step by step: The ground truth contains a single statement: \\"The capital of Japan is Tokyo.\\" The response exactly matches this statement without omitting or altering any information. There are no additional claims or missing details to consider. According to the definitions, a fully complete response should perfectly contain all necessary and relevant information from the ground truth.</S0>\\n<S1>The response is a perfect match to the ground truth, with no missing or incorrect information.</S1>\\n<S2>5</S2>"}]',
    }


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestResponseCompletenessEvaluator:
    def test_initialization(self, mock_model_config):
        response_completeness_evaluator = ResponseCompletenessEvaluator(model_config=mock_model_config)
        # Test initialization of ResponseCompletenessEvaluator
        assert (
            response_completeness_evaluator.threshold == ResponseCompletenessEvaluator._DEFAULT_COMPLETENESS_THRESHOLD
        )
        assert response_completeness_evaluator._result_key == ResponseCompletenessEvaluator._RESULT_KEY
        assert response_completeness_evaluator._is_reasoning_model is False

    def test_initialization2(self, mock_model_config):
        response_completeness_evaluator = ResponseCompletenessEvaluator(
            model_config=mock_model_config, is_reasoning_model=True
        )
        # Test initialization of ResponseCompletenessEvaluator
        assert (
            response_completeness_evaluator.threshold == ResponseCompletenessEvaluator._DEFAULT_COMPLETENESS_THRESHOLD
        )
        assert response_completeness_evaluator._result_key == ResponseCompletenessEvaluator._RESULT_KEY
        assert response_completeness_evaluator._is_reasoning_model is True

    def test_evaluate_completeness_valid1(self, mock_model_config):
        response_completeness_evaluator = ResponseCompletenessEvaluator(model_config=mock_model_config)
        response_completeness_evaluator._flow = MagicMock(return_value=completeness_response1_async_mock())

        # Test evaluation with valid ground truth and response
        ground_truth = "The capital of Japan is Tokyo."
        response = "The capital of Japan"
        result = response_completeness_evaluator(ground_truth=ground_truth, response=response)

        key = ResponseCompletenessEvaluator._RESULT_KEY
        assert result is not None
        assert (
            key in result and f"{key}_result" in result and f"{key}_threshold" in result and f"{key}_reason" in result
        )
        assert result[key] == 1
        assert result[f"{key}_result"] == "fail"
        assert result[f"{key}_threshold"] == ResponseCompletenessEvaluator._DEFAULT_COMPLETENESS_THRESHOLD
        assert "The response is fully incomplete " in result[f"{key}_reason"]

    def test_evaluate_completeness_valid2(self, mock_model_config):
        response_completeness_evaluator = ResponseCompletenessEvaluator(model_config=mock_model_config)
        response_completeness_evaluator._flow = MagicMock(return_value=completeness_response2_async_mock())

        # Test evaluation with valid ground truth and response
        ground_truth = "The capital of Japan is Tokyo."
        response = "The capital of Japan is Tokyo."
        result = response_completeness_evaluator(ground_truth=ground_truth, response=response)

        key = ResponseCompletenessEvaluator._RESULT_KEY
        assert result is not None

        assert (
            key in result and f"{key}_result" in result and f"{key}_threshold" in result and f"{key}_reason" in result
        )
        assert result[key] == 5
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ResponseCompletenessEvaluator._DEFAULT_COMPLETENESS_THRESHOLD
        assert "The response is a perfect match " in result[f"{key}_reason"]

    def test_evaluate_completeness_valid3(self, mock_model_config):
        response_completeness_evaluator = ResponseCompletenessEvaluator(
            model_config=mock_model_config, is_reasoning_model=True
        )
        response_completeness_evaluator._flow = MagicMock(return_value=completeness_response2_async_mock())

        # Test evaluation with valid ground truth and response
        ground_truth = "The capital of Japan is Tokyo."
        response = "The capital of Japan is Tokyo."
        result = response_completeness_evaluator(ground_truth=ground_truth, response=response)

        key = ResponseCompletenessEvaluator._RESULT_KEY
        assert result is not None

        assert (
            key in result and f"{key}_result" in result and f"{key}_threshold" in result and f"{key}_reason" in result
        )
        assert result[key] == 5
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ResponseCompletenessEvaluator._DEFAULT_COMPLETENESS_THRESHOLD
        assert "The response is a perfect match " in result[f"{key}_reason"]

    def test_evaluate_completeness_missing_ground_truth(self, mock_model_config):
        response_completeness_evaluator = ResponseCompletenessEvaluator(model_config=mock_model_config)
        response_completeness_evaluator._flow = MagicMock(return_value=completeness_response1_async_mock())

        # Test evaluation with missing ground truth
        response = "The capital of China is Beijing."
        with pytest.raises(EvaluationException) as exc_info:
            response_completeness_evaluator(response=response)

        assert (
            "ResponseCompletenessEvaluator: Either 'conversation' or individual inputs must be provided."
            in exc_info.value.args[0]
        )

    def test_evaluate_completeness_missing_response(self, mock_model_config):
        response_completeness_evaluator = ResponseCompletenessEvaluator(model_config=mock_model_config)
        response_completeness_evaluator._flow = MagicMock(return_value=completeness_response1_async_mock())

        # Test evaluation with missing ground truth
        ground_truth = "The capital of China is Beijing."
        with pytest.raises(EvaluationException) as exc_info:
            response_completeness_evaluator(ground_truth=ground_truth)

        assert (
            "ResponseCompletenessEvaluator: Either 'conversation' or individual inputs must be provided."
            in exc_info.value.args[0]
        )
