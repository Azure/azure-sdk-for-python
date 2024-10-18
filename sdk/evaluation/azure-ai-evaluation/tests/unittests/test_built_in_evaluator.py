from unittest.mock import MagicMock

import pytest
from random import uniform

from azure.ai.evaluation._exceptions import EvaluationException
from azure.ai.evaluation import FluencyEvaluator, GroundednessEvaluator, SimilarityEvaluator, RetrievalEvaluator


async def fluency_async_mock():
    return "1"

async def quality_async_passing_score_mock():
    return str(uniform(3,5))

async def quality_async_failing_score_mock():
    return str(uniform(1,2))

@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestBuiltInEvaluators:
    def test_fluency_evaluator(self, mock_model_config):
        fluency_eval = FluencyEvaluator(model_config=mock_model_config)
        fluency_eval._flow = MagicMock(return_value=fluency_async_mock())

        score = fluency_eval(query="What is the capital of Japan?", response="The capital of Japan is Tokyo.")

        assert score is not None
        assert score["gpt_fluency"] == 1

    def test_fluency_evaluator_non_string_inputs(self, mock_model_config):
        fluency_eval = FluencyEvaluator(model_config=mock_model_config)
        fluency_eval._flow = MagicMock(return_value=fluency_async_mock())

        score = fluency_eval(query={"foo": 1}, response={"bar": "2"})

        assert score is not None
        assert score["gpt_fluency"] == 1

    def test_fluency_evaluator_empty_string(self, mock_model_config):
        fluency_eval = FluencyEvaluator(model_config=mock_model_config)
        fluency_eval._flow = MagicMock(return_value=fluency_async_mock())

        with pytest.raises(EvaluationException) as exc_info:
            fluency_eval(query="What is the capital of Japan?", response=None)

        assert (
            "FluencyEvaluator: Either 'conversation' or individual inputs must be provided." in exc_info.value.args[0]
        )


    # passing_score behavior tested here is defined by PromptyEvaluatorBase - all children have different call
    # signatures, so instead of parametrizing this call, testing GroundednessEvaluator as an example
    def test_quality_evaluator_passing_score(self, mock_model_config):
        groundedness_eval = GroundednessEvaluator(model_config=mock_model_config)
        groundedness_eval._flow = MagicMock(return_value=quality_async_passing_score_mock())
        result = groundedness_eval(
            response="The capital of Japan is Tokyo.",
            context="Tokyo is Japan's capital, known for its blend of traditional culture and technological advancements."
        )
        assert len(result.keys()) == 2
        assert "gpt_groundedness" in result
        assert "gpt_groundedness_label" in result
        assert result["gpt_groundedness_label"] == True

        groundedness_eval_passing = GroundednessEvaluator(model_config=mock_model_config, passing_score=2.0)
        groundedness_eval_passing._flow = MagicMock(return_value=quality_async_passing_score_mock())
        result = groundedness_eval_passing(
            response="The capital of Japan is Tokyo.",
            context="Tokyo is Japan's capital, known for its blend of traditional culture and technological advancements."
        )
        assert len(result.keys()) == 2
        assert "gpt_groundedness" in result
        assert "gpt_groundedness_label" in result
        assert result["gpt_groundedness_label"] == True

        groundedness_eval_passing = GroundednessEvaluator(model_config=mock_model_config, passing_score=4.0)
        groundedness_eval_passing._flow = MagicMock(return_value=quality_async_failing_score_mock())
        result = groundedness_eval_passing(
            response="The capital of Japan is Tokyo.",
            context="Tokyo is Japan's capital, known for its blend of traditional culture and technological advancements."
        )
        assert len(result.keys()) == 2
        assert "gpt_groundedness" in result
        assert "gpt_groundedness_label" in result
        assert result["gpt_groundedness_label"] == False

    # This test can be removed once SimilarityEvaluator is refactored to inherit from PromptyEvaluatorBase
    # ADO Task #3563786
    def test_similarity_evaluator_passing_score(self, mock_model_config):
        similarity_eval = SimilarityEvaluator(model_config=mock_model_config)
        similarity_eval._async_evaluator._flow = MagicMock(return_value=quality_async_passing_score_mock())
        result = similarity_eval(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
            ground_truth="Tokyo is Japan's capital."
        )
        assert len(result.keys()) == 2
        assert "gpt_similarity" in result
        assert "gpt_similarity_label" in result
        assert result["gpt_similarity_label"] == True

        similarity_eval_passing = SimilarityEvaluator(model_config=mock_model_config, passing_score=2.0)
        similarity_eval_passing._async_evaluator._flow = MagicMock(return_value=quality_async_passing_score_mock())
        result = similarity_eval_passing(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
            ground_truth="Tokyo is Japan's capital."
        )
        assert len(result.keys()) == 2
        assert "gpt_similarity" in result
        assert "gpt_similarity_label" in result
        assert result["gpt_similarity_label"] == True

        similarity_eval_passing = SimilarityEvaluator(model_config=mock_model_config, passing_score=4.0)
        similarity_eval_passing._async_evaluator._flow = MagicMock(return_value=quality_async_failing_score_mock())
        result = similarity_eval_passing(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
            ground_truth="Tokyo is Japan's capital."
        )
        assert len(result.keys()) == 2
        assert "gpt_similarity" in result
        assert "gpt_similarity_label" in result
        assert result["gpt_similarity_label"] == False

    # This test can be removed once RetrievalEvaluator is refactored to inherit from PromptyEvaluatorBase
    # ADO Task #3563786
    def test_retrieval_evaluator_passing_score(self, mock_model_config):
        conversation = [
            {"role": "user", "content": "What is the value of 2 + 2?"},
            {"role": "assistant", "content": "2 + 2 = 4", "context": {
                "citations": [
                        {"id": "math_doc.md", "content": "Information about additions: 1 + 2 = 3, 2 + 2 = 4"}
                        ]
                }
            }
        ]

        retrieval_eval = RetrievalEvaluator(model_config=mock_model_config)
        retrieval_eval._async_evaluator._flow = MagicMock(return_value=quality_async_passing_score_mock())
        result = retrieval_eval(conversation=conversation)
        assert len(result.keys()) == 3
        assert "gpt_retrieval" in result
        assert "gpt_retrieval_label" in result
        assert result["gpt_retrieval_label"] == True

        retrieval_eval_passing = RetrievalEvaluator(model_config=mock_model_config, passing_score=2.0)
        retrieval_eval_passing._async_evaluator._flow = MagicMock(return_value=quality_async_passing_score_mock())
        result = retrieval_eval_passing(conversation=conversation)
        assert len(result.keys()) == 3
        assert "gpt_retrieval" in result
        assert "gpt_retrieval_label" in result
        assert result["gpt_retrieval_label"] == True

        retrieval_eval_passing = RetrievalEvaluator(model_config=mock_model_config, passing_score=4.0)
        retrieval_eval_passing._async_evaluator._flow = MagicMock(return_value=quality_async_failing_score_mock())
        result = retrieval_eval_passing(conversation=conversation)
        assert len(result.keys()) == 3
        assert "gpt_retrieval" in result
        assert "gpt_retrieval_label" in result
        assert result["gpt_retrieval_label"] == False
