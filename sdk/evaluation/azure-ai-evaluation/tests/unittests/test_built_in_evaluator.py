from unittest.mock import MagicMock

import pytest

from azure.ai.evaluation import FluencyEvaluator, RetrievalEvaluator, SimilarityEvaluator
from azure.ai.evaluation._exceptions import EvaluationException


async def quality_async_mock():
    return "1"


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestBuiltInEvaluators:
    def test_fluency_evaluator(self, mock_model_config):
        fluency_eval = FluencyEvaluator(model_config=mock_model_config)
        fluency_eval._flow = MagicMock(return_value=quality_async_mock())

        score = fluency_eval(query="What is the capital of Japan?", response="The capital of Japan is Tokyo.")

        assert score is not None
        assert score["fluency"] == score["gpt_fluency"] == 1

    def test_fluency_evaluator_non_string_inputs(self, mock_model_config):
        fluency_eval = FluencyEvaluator(model_config=mock_model_config)
        fluency_eval._flow = MagicMock(return_value=quality_async_mock())

        score = fluency_eval(query={"foo": 1}, response={"bar": "2"})

        assert score is not None
        assert score["fluency"] == score["gpt_fluency"] == 1

    def test_fluency_evaluator_empty_string(self, mock_model_config):
        fluency_eval = FluencyEvaluator(model_config=mock_model_config)
        fluency_eval._flow = MagicMock(return_value=quality_async_mock())

        with pytest.raises(EvaluationException) as exc_info:
            fluency_eval(query="What is the capital of Japan?", response=None)

        assert (
            "FluencyEvaluator: Either 'conversation' or individual inputs must be provided." in exc_info.value.args[0]
        )

    def test_similarity_evaluator_keys(self, mock_model_config):
        similarity_eval = SimilarityEvaluator(model_config=mock_model_config)
        similarity_eval._async_evaluator._flow = MagicMock(return_value=quality_async_mock())

        result = similarity_eval(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
            ground_truth="Tokyo is Japan's capital, known for its blend of traditional culture and technological advancements.",
        )
        assert result["similarity"] == result["gpt_similarity"] == 1

    def test_retrieval_evaluator_keys(self, mock_model_config):
        retrieval_eval = RetrievalEvaluator(model_config=mock_model_config)
        retrieval_eval._async_evaluator._flow = MagicMock(return_value=quality_async_mock())
        conversation = {
            "messages": [
                {"role": "user", "content": "What is the value of 2 + 2?"},
                {"role": "assistant", "content": "2 + 2 = 4", "context": {
                    "citations": [
                            {"id": "math_doc.md", "content": "Information about additions: 1 + 2 = 3, 2 + 2 = 4"}
                        ]
                    }
                }
            ]
        }

        result = retrieval_eval(conversation=conversation)
        assert result["retrieval"] == result["gpt_retrieval"] == 1