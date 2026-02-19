from unittest.mock import MagicMock, patch

import pytest
from azure.ai.evaluation import GroundednessEvaluator


async def groundedness_response_async_mock():
    return {
        "llm_output": "<S0>Let's analyze: The response states that Paris is the capital of France, and the context confirms this.</S0>\n<S1>The response is fully grounded in the provided context.</S1>\n<S2>5</S2>",
        "input_token_count": 1354,
        "output_token_count": 108,
        "total_token_count": 1462,
        "finish_reason": "stop",
        "model_id": "gpt-4.1-2025-04-14",
        "sample_input": '[{"role": "user", "content": "..."}]',
        "sample_output": '[{"role": "assistant", "content": "..."}]',
    }


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestGroundednessEvaluator:
    def test_initialization_default_is_reasoning_model(self, mock_model_config):
        """Test that is_reasoning_model defaults to False"""
        groundedness_evaluator = GroundednessEvaluator(model_config=mock_model_config)
        assert groundedness_evaluator._is_reasoning_model is False

    def test_initialization_with_is_reasoning_model_true(self, mock_model_config):
        """Test that is_reasoning_model=True is stored correctly"""
        groundedness_evaluator = GroundednessEvaluator(model_config=mock_model_config, is_reasoning_model=True)
        assert groundedness_evaluator._is_reasoning_model is True

    def test_initialization_stores_credential(self, mock_model_config):
        """Test that credential is stored for use in _ensure_query_prompty_loaded"""
        mock_credential = MagicMock()
        groundedness_evaluator = GroundednessEvaluator(model_config=mock_model_config, credential=mock_credential)
        assert groundedness_evaluator._credential is mock_credential

    def test_initialization_stores_credential_none(self, mock_model_config):
        """Test that credential defaults to None"""
        groundedness_evaluator = GroundednessEvaluator(model_config=mock_model_config)
        assert groundedness_evaluator._credential is None

    def test_query_mode_preserves_is_reasoning_model(self, mock_model_config):
        """Test that is_reasoning_model is passed when switching to query prompty"""
        groundedness_evaluator = GroundednessEvaluator(model_config=mock_model_config, is_reasoning_model=True)
        groundedness_evaluator._flow = MagicMock(return_value=groundedness_response_async_mock())

        # Mock AsyncPrompty.load to verify is_reasoning_model is passed
        with patch("azure.ai.evaluation._evaluators._groundedness._groundedness.AsyncPrompty.load") as mock_load:
            mock_load.return_value = MagicMock(return_value=groundedness_response_async_mock())

            # Trigger _ensure_query_prompty_loaded by calling with query
            groundedness_evaluator._ensure_query_prompty_loaded()

            # Verify AsyncPrompty.load was called with is_reasoning_model=True
            mock_load.assert_called_once()
            call_kwargs = mock_load.call_args[1]
            assert call_kwargs.get("is_reasoning_model") is True

    def test_query_mode_preserves_credential(self, mock_model_config):
        """Test that credential is passed when switching to query prompty"""
        mock_credential = MagicMock()
        groundedness_evaluator = GroundednessEvaluator(model_config=mock_model_config, credential=mock_credential)
        groundedness_evaluator._flow = MagicMock(return_value=groundedness_response_async_mock())

        # Mock AsyncPrompty.load to verify token_credential is passed
        with patch("azure.ai.evaluation._evaluators._groundedness._groundedness.AsyncPrompty.load") as mock_load:
            mock_load.return_value = MagicMock(return_value=groundedness_response_async_mock())

            # Trigger _ensure_query_prompty_loaded by calling with query
            groundedness_evaluator._ensure_query_prompty_loaded()

            # Verify AsyncPrompty.load was called with token_credential
            mock_load.assert_called_once()
            call_kwargs = mock_load.call_args[1]
            assert call_kwargs.get("token_credential") is mock_credential

    def test_evaluate_groundedness_valid(self, mock_model_config):
        """Test basic evaluation flow"""
        groundedness_evaluator = GroundednessEvaluator(model_config=mock_model_config)
        groundedness_evaluator._flow = MagicMock(return_value=groundedness_response_async_mock())

        response = "The capital of France is Paris."
        context = "Paris is the capital of France."
        result = groundedness_evaluator(response=response, context=context)

        key = GroundednessEvaluator._RESULT_KEY
        assert result is not None
        assert key in result
        assert result[key] == 5
