from unittest.mock import MagicMock, patch

import pytest

from azure.ai.evaluation._exceptions import EvaluationException
from azure.ai.evaluation import (
    FluencyEvaluator,
    SimilarityEvaluator,
    RetrievalEvaluator,
    RelevanceEvaluator,
    GroundednessEvaluator,
    QAEvaluator,
)


async def quality_response_async_mock(*args, **kwargs):
    llm_output = (
        "<S0>Let's think step by step: The response 'Honolulu' is a single word. "
        "It does not form a complete sentence, lacks grammatical structure, and does not "
        "convey any clear idea or message. It is not possible to assess vocabulary range, "
        "sentence complexity, coherence, or overall readability from a single word. Therefore,"
        "it falls into the category of minimal command of the language.</S0>"
        "<S1>The response is a single word and does not provide any meaningful content to evaluate"
        " fluency. It is largely incomprehensible and does not meet the criteria for higher fluency "
        "levels.</S1><S2>1</S2>"
    )
    return {"llm_output": llm_output}


async def quality_no_response_async_mock():
    return {"llm_output": "1"}


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
            "FluencyEvaluator: Either 'conversation' or individual inputs must be provided."
            in exc_info.value.args[0]
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
        assert len(result) == 11
        # Verify all expected keys are present
        assert set(result.keys()) == {
            "similarity",
            "gpt_similarity",
            "similarity_result",
            "similarity_threshold",
            "similarity_prompt_tokens",
            "similarity_completion_tokens",
            "similarity_total_tokens",
            "similarity_finish_reason",
            "similarity_model",
            "similarity_sample_input",
            "similarity_sample_output",
        }

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
                            {
                                "id": "math_doc.md",
                                "content": "Information about additions: 1 + 2 = 3, 2 + 2 = 4",
                            }
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
            quality_eval(
                response="The capital of Japan is Tokyo."
            )  # Retrieval requires query and context

        assert (
            "RetrievalEvaluator: Either 'conversation' or individual inputs must be provided."
            in exc_info.value.args[0]
        )

    @patch(
        "azure.ai.evaluation._evaluators._groundedness._groundedness.AsyncPrompty.load"
    )
    def test_groundedness_evaluator_with_agent_response(
        self, mock_async_prompty, mock_model_config
    ):
        """Test GroundednessEvaluator with query, response, and tool_definitions"""
        groundedness_eval = GroundednessEvaluator(model_config=mock_model_config)
        mock_async_prompty.return_value = quality_response_async_mock

        # Test with query, response, and tool_definitions
        result = groundedness_eval(
            query="What is the capital of Japan?",
            response=[
                {
                    "createdAt": "2025-08-01T00:02:38Z",
                    "run_id": "run_CmSdDdrq0CzwGOwqmWVADYwi",
                    "tool_call_id": "call_AU6kCcVwxv1cjM8HIQHMFFGh",
                    "role": "tool",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_result": [
                                {
                                    "file_id": "assistant-6QeBNfMsJpL3AHnE3T6dwY",
                                    "file_name": "product_info_1.md",
                                    "score": 0.03333333507180214,
                                    "attributes": {},
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "# Information about product item_number: 1\n\n## Brand\nContoso Galaxy Innovations\n\n## Category\nSmart Eyewear\n",
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                },
                {
                    "createdAt": "2025-08-01T00:02:38Z",
                    "run_id": "run_CmSdDdrq0CzwGOwqmWVADYwi",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "One of the Contoso products identified is the **SmartView Glasses**",
                        }
                    ],
                },
                {
                    "createdAt": "2025-08-01T00:02:38Z",
                    "run_id": "run_CmSdDdrq0CzwGOwqmWVADYwi",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_call",
                            "tool_call_id": "call_AU6kCcVwxv1cjM8HIQHMFFGh",
                            "name": "file_search",
                            "arguments": {
                                "ranking_options": {
                                    "ranker": "default_2024_08_21",
                                    "score_threshold": 0.0,
                                }
                            },
                        }
                    ],
                },
            ],
            tool_definitions=[
                {
                    "name": "file_search",
                    "type": "file_search",
                    "description": "Search for information in files",
                }
            ],
        )

        assert result is not None
        assert result["groundedness"] == result["gpt_groundedness"] == 1
        assert "groundedness_reason" in result

    @patch(
        "azure.ai.evaluation._evaluators._groundedness._groundedness.AsyncPrompty.load"
    )
    def test_groundedness_evaluator_respects_reasoning_model_on_query_prompty(
        self, mock_async_prompty, mock_model_config
    ):
        """Ensure is_reasoning_model and credentials propagate when switching templates"""
        credential = object()
        mock_async_prompty.return_value = quality_response_async_mock

        groundedness_eval = GroundednessEvaluator(
            model_config=mock_model_config, credential=credential, is_reasoning_model=True
        )

        result = groundedness_eval(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
            context="Tokyo is the capital of Japan.",
        )

        assert result["groundedness"] == result["gpt_groundedness"] == 1
        assert mock_async_prompty.call_count >= 2

        last_call = mock_async_prompty.call_args_list[-1]
        assert last_call.kwargs["is_reasoning_model"] is True
        assert last_call.kwargs["token_credential"] is credential
        assert last_call.kwargs["source"].endswith(GroundednessEvaluator._PROMPTY_FILE_WITH_QUERY)

    def test_groundedness_evaluator_with_context(self, mock_model_config):
        """Test GroundednessEvaluator with direct context (traditional use)"""
        groundedness_eval = GroundednessEvaluator(model_config=mock_model_config)
        groundedness_eval._flow = MagicMock(return_value=quality_response_async_mock())

        result = groundedness_eval(
            response="The capital of Japan is Tokyo.",
            context="Tokyo is the capital of Japan and is located on the eastern coast of Honshu island.",
        )

        assert result is not None
        assert result["groundedness"] == result["gpt_groundedness"] == 1
        assert "groundedness_reason" in result

    def test_groundedness_evaluator_missing_required_inputs(self, mock_model_config):
        """Test GroundednessEvaluator with missing required inputs for agent response mode"""
        groundedness_eval = GroundednessEvaluator(model_config=mock_model_config)
        groundedness_eval._flow = MagicMock(return_value=quality_response_async_mock())

        with pytest.raises(EvaluationException) as exc_info:
            groundedness_eval(
                query="What is the capital of Japan?",
                # Missing response
            )

        assert (
            "Either 'conversation' or individual inputs must be provided. For Agent groundedness 'query' and 'response' are required."
            in exc_info.value.args[0]
        )

    def test_qa_evaluator_is_reasoning_model_default(self, mock_model_config):
        """Test QAEvaluator initializes with is_reasoning_model defaulting to False"""
        qa_eval = QAEvaluator(model_config=mock_model_config)
        # Check that all model-based evaluators have is_reasoning_model set to False
        for evaluator in qa_eval._evaluators:
            if hasattr(evaluator, "_is_reasoning_model"):
                assert evaluator._is_reasoning_model is False

    def test_qa_evaluator_is_reasoning_model_true(self, mock_model_config):
        """Test QAEvaluator properly passes is_reasoning_model=True to sub-evaluators"""
        qa_eval = QAEvaluator(model_config=mock_model_config, is_reasoning_model=True)
        # Check that all model-based evaluators have is_reasoning_model set to True
        for evaluator in qa_eval._evaluators:
            if hasattr(evaluator, "_is_reasoning_model"):
                assert evaluator._is_reasoning_model is True
