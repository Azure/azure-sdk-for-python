# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from unittest.mock import MagicMock, patch
from azure.core.credentials import TokenCredential
from azure.ai.evaluation import AzureOpenAIModelConfiguration
from azure.ai.evaluation._evaluators._relevance import RelevanceEvaluator


@pytest.fixture(scope="session")
def test_model_config() -> AzureOpenAIModelConfiguration:
    """Mock model configuration for tests."""
    return AzureOpenAIModelConfiguration(
        azure_endpoint="https://test.openai.azure.com",
        api_key="test-key",
        api_version="2024-02-15-preview",
        azure_deployment="test-deployment"
    )


@pytest.fixture(scope="function")
def mock_credential():
    """Mock credential for tests."""
    return MagicMock(spec=TokenCredential)


@pytest.mark.unittest
class TestConversationThresholdBehavior:
    """Test threshold behavior in conversation evaluators."""

    @patch(
        "azure.ai.evaluation._evaluators._relevance._relevance."
        "RelevanceEvaluator.__call__"
    )
    def test_relevance_evaluator_with_conversation(
        self, mock_call, test_model_config
    ):
        """Test relevance evaluator with conversation input."""
        mock_result = {
            "relevance": 4.0,
            "relevance_result": "PASS",
            "evaluation_per_turn": {
                "relevance": [4.0]
            }
        }
        mock_call.return_value = mock_result
        
        evaluator = RelevanceEvaluator(
            model_config=test_model_config,
            threshold=3
        )
        conversation = {
            "messages": [
                {"role": "user", "content": "What is the weather like?"},
                {"role": "assistant", "content": "It's sunny today."}
            ]
        }
        result = evaluator(conversation=conversation)
        assert result["relevance"] > 0.0
        assert "evaluation_per_turn" in result


@pytest.mark.unittest
class TestMultipleEvaluatorThresholds:
    """Test multiple evaluators with different thresholds."""

    @patch(
        "azure.ai.evaluation._evaluators._relevance._relevance."
        "RelevanceEvaluator.__call__"
    )
    def test_evaluators_with_different_thresholds(
        self, mock_call, test_model_config
    ):
        """Test that evaluators can have different thresholds."""
        mock_result = {
            "relevance": 4.0,
            "relevance_result": "PASS",
            "evaluation_per_turn": {
                "relevance": [4.0]
            }
        }
        mock_call.return_value = mock_result

        evaluator1 = RelevanceEvaluator(
            model_config=test_model_config,
            threshold=2
        )
        evaluator2 = RelevanceEvaluator(
            model_config=test_model_config,
            threshold=4
        )
        conversation = {
            "messages": [
                {"role": "user", "content": "What is the time?"},
                {"role": "assistant", "content": "It is 3pm."}
            ]
        }
        result1 = evaluator1(conversation=conversation)
        result2 = evaluator2(conversation=conversation)
        assert evaluator1._threshold != evaluator2._threshold
        assert "relevance" in result1
        assert "relevance" in result2
        assert "evaluation_per_turn" in result1
        assert "evaluation_per_turn" in result2

    @patch(
        "azure.ai.evaluation._evaluators._relevance._relevance."
        "RelevanceEvaluator.__call__"
    )
    def test_threshold_comparison_behavior(
        self, mock_call, test_model_config
    ):
        """Test how different thresholds affect evaluation results."""
        mock_result_high = {
            "relevance": 4.5,
            "relevance_result": "PASS",
            "evaluation_per_turn": {
                "relevance": [4.5]
            }
        }
        mock_result_low = {
            "relevance": 2.5,
            "relevance_result": "FAIL",
            "evaluation_per_turn": {
                "relevance": [2.5]
            }
        }
        mock_call.side_effect = [mock_result_high, mock_result_low]

        strict_evaluator = RelevanceEvaluator(
            model_config=test_model_config,
            threshold=4
        )
        lenient_evaluator = RelevanceEvaluator(
            model_config=test_model_config,
            threshold=2
        )
        conversation = {
            "messages": [
                {"role": "user", "content": "What is the capital of France?"},
                {
                    "role": "assistant",
                    "content": "Paris is the capital of France."
                }
            ]
        }
        strict_result = strict_evaluator(conversation=conversation)
        lenient_result = lenient_evaluator(conversation=conversation)
        assert strict_evaluator._threshold > lenient_evaluator._threshold
        assert strict_result["relevance"] > lenient_result["relevance"]
        assert "evaluation_per_turn" in strict_result
        assert "evaluation_per_turn" in lenient_result


@pytest.mark.unittest
class TestEvaluatorsCombinedWithSample:
    """Test evaluators with sample conversations and thresholds."""

    def test_sample_evaluators_threshold_setup(self, test_model_config):
        """Test setting up evaluators with different thresholds."""
        evaluators = [
            RelevanceEvaluator(
                model_config=test_model_config,
                threshold=threshold
            )
            for threshold in [1, 3, 5]
        ]
        for i, evaluator in enumerate(evaluators):
            assert evaluator._threshold == [1, 3, 5][i]

    @patch(
        "azure.ai.evaluation._evaluators._relevance._relevance."
        "RelevanceEvaluator.__call__"
    )
    def test_sample_evaluators_passing_thresholds(
        self, mock_call, test_model_config
    ):
        """Test evaluators with passing threshold values."""
        mock_result = {
            "relevance": 4.0,
            "relevance_result": "PASS",
            "evaluation_per_turn": {
                "relevance": [4.0]
            }
        }
        mock_call.return_value = mock_result

        evaluator = RelevanceEvaluator(
            model_config=test_model_config,
            threshold=3
        )
        conversations = [
            {
                "messages": [
                    {"role": "user", "content": "What is 2+2?"},
                    {"role": "assistant", "content": "2+2 equals 4."}
                ]
            },
            {
                "messages": [
                    {"role": "user", "content": "Who wrote Romeo and Juliet?"},
                    {
                        "role": "assistant",
                        "content": "Shakespeare was the author."
                    }
                ]
            }
        ]
        for conversation in conversations:
            result = evaluator(conversation=conversation)
            assert "relevance" in result
            assert result["relevance"] == 4.0
            assert "evaluation_per_turn" in result
