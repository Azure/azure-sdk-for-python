# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
from unittest.mock import MagicMock

import pytest

from azure.ai.evaluation import SimilarityEvaluator


def _mock_flow(llm_output):
    async def flow_async_mock():
        return {"llm_output": llm_output}

    return MagicMock(return_value=flow_async_mock())


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestPromptyScoreFallback:
    """Tests for the free-text score fallback in ``PromptyEvaluatorBase._do_eval``.

    SimilarityEvaluator is used because its result key is not in
    PROMPT_BASED_REASON_EVALUATORS, so a judge reply that is not parseable JSON
    reaches the numeric-extraction fallback.
    """

    @pytest.mark.parametrize(
        "llm_output, expected",
        [
            ("5", 5.0),
            ("The answer is grounded. 5", 5.0),
            ("Score: 4 (one minor gap)", 4.0),
            ("The answer makes 3 claims, all supported. Score: 5", 5.0),
            ("2 of the statements are unsupported, so this is not grounded: 1", 1.0),
            ("10 out of 10", 10.0),
        ],
    )
    def test_fallback_extracts_verdict_score(self, mock_model_config, llm_output, expected):
        similarity_eval = SimilarityEvaluator(model_config=mock_model_config)
        similarity_eval._flow = _mock_flow(llm_output)

        result = similarity_eval(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
            ground_truth="Tokyo is Japan's capital.",
        )
        assert result["similarity_score"] == expected

    def test_fallback_without_number_returns_nan(self, mock_model_config):
        similarity_eval = SimilarityEvaluator(model_config=mock_model_config)
        similarity_eval._flow = _mock_flow("The answer is well grounded.")

        result = similarity_eval(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
            ground_truth="Tokyo is Japan's capital.",
        )
        assert math.isnan(result["similarity_score"])
        assert result["similarity_result"] == "unknown"
