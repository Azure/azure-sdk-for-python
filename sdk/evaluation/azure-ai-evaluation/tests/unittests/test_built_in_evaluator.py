from unittest.mock import MagicMock

import pytest

from azure.ai.evaluation._exceptions import EvaluationException
from azure.ai.evaluation import FluencyEvaluator, SimilarityEvaluator, RetrievalEvaluator, RelevanceEvaluator


async def quality_response_async_mock():
    return (
        "<S0>Let's think step by step: The response 'Honolulu' is a single word. "
        "It does not form a complete sentence, lacks grammatical structure, and does not "
        "convey any clear idea or message. It is not possible to assess vocabulary range, "
        "sentence complexity, coherence, or overall readability from a single word. Therefore,"
        "it falls into the category of minimal command of the language.</S0>"
        "<S1>The response is a single word and does not provide any meaningful content to evaluate"
        " fluency. It is largely incomprehensible and does not meet the criteria for higher fluency "
        "levels.</S1><S2>1</S2>"
    )


async def quality_no_response_async_mock():
    return "1"


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestBuiltInEvaluators:
    def test_fluency_evaluator(self, mock_model_config):
        fluency_eval = FluencyEvaluator(model_config=mock_model_config)
        fluency_eval._flow = MagicMock(return_value=quality_response_async_mock())

        score = fluency_eval(response="The capital of Japan is Tokyo.")

        assert score is not None
        assert score["fluency"] == score["gpt_fluency"] == 1

    def test_fluency_evaluator_non_string_inputs(self, mock_model_config):
        fluency_eval = FluencyEvaluator(model_config=mock_model_config)
        fluency_eval._flow = MagicMock(return_value=quality_response_async_mock())

        score = fluency_eval(response={"bar": "2"})

        assert score is not None
        assert score["fluency"] == score["gpt_fluency"] == 1

    def test_fluency_evaluator_empty_string(self, mock_model_config):
        fluency_eval = FluencyEvaluator(model_config=mock_model_config)
        fluency_eval._flow = MagicMock(return_value=quality_response_async_mock())

        with pytest.raises(EvaluationException) as exc_info:
            fluency_eval(response=None)

        assert (
            "FluencyEvaluator: Either 'conversation' or individual inputs must be provided." in exc_info.value.args[0]
        )

    def test_similarity_evaluator_keys(self, mock_model_config):
        similarity_eval = SimilarityEvaluator(model_config=mock_model_config)
        similarity_eval._flow = MagicMock(return_value=quality_no_response_async_mock())

        result = similarity_eval(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
            ground_truth="Tokyo is Japan's capital, known for its blend of traditional culture and technological advancements.",
        )
        assert result["similarity"] == result["gpt_similarity"] == 1
        # Updated assertion to expect 4 keys instead of 2
        assert len(result) == 4
        # Verify all expected keys are present
        assert set(result.keys()) == {"similarity", "gpt_similarity", "similarity_result", "similarity_threshold"}

    def test_retrieval_evaluator_keys(self, mock_model_config):
        retrieval_eval = RetrievalEvaluator(model_config=mock_model_config)
        retrieval_eval._flow = MagicMock(return_value=quality_response_async_mock())
        result = retrieval_eval(
            query="What is the value of 2 + 2?",
            context="1 + 2 = 2",
        )
        assert result["retrieval"] == result["gpt_retrieval"] == 1
        assert result["retrieval"] == result["gpt_retrieval"]
        assert result["retrieval_reason"]

        retrieval_eval = RetrievalEvaluator(model_config=mock_model_config)
        retrieval_eval._flow = MagicMock(return_value=quality_response_async_mock())
        conversation = {
            "messages": [
                {"role": "user", "content": "What is the value of 2 + 2?"},
                {
                    "role": "assistant",
                    "content": "2 + 2 = 4",
                    "context": {
                        "citations": [
                            {"id": "math_doc.md", "content": "Information about additions: 1 + 2 = 3, 2 + 2 = 4"}
                        ]
                    },
                },
            ]
        }

        result = retrieval_eval(conversation=conversation)
        assert result["retrieval"] == result["gpt_retrieval"] == 1

        retrieval_eval = RetrievalEvaluator(model_config=mock_model_config)
        retrieval_eval._flow = MagicMock(return_value=quality_response_async_mock())
        conversation = {
            "messages": [
                {"role": "user", "content": "What is the value of 2 + 2?"},
                {
                    "role": "assistant",
                    "content": "2 + 2 = 4",
                    "context": "Information about additions: 1 + 2 = 3, 2 + 2 = 4",
                },
            ]
        }

        result = retrieval_eval(conversation=conversation)
        assert result["retrieval"] == result["gpt_retrieval"] == 1

    def test_quality_evaluator_missing_input(self, mock_model_config):
        """All evaluators that inherit from EvaluatorBase are covered by this test"""
        quality_eval = RetrievalEvaluator(model_config=mock_model_config)
        quality_eval._flow = MagicMock(return_value=quality_response_async_mock())

        with pytest.raises(EvaluationException) as exc_info:
            quality_eval(response="The capital of Japan is Tokyo.")  # Retrieval requires query and context

        assert (
            "RetrievalEvaluator: Either 'conversation' or individual inputs must be provided." in exc_info.value.args[0]
        )
