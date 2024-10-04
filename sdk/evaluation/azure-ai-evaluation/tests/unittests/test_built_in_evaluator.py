from unittest.mock import MagicMock

import pytest

from azure.ai.evaluation._exceptions import EvaluationException
from azure.ai.evaluation import FluencyEvaluator


async def fluency_async_mock():
    return "1"


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

        assert "Missing input" in exc_info.value.args[0]
