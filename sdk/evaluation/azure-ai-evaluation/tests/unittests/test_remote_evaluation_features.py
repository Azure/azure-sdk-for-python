# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.ai.evaluation import F1ScoreEvaluator
from azure.ai.evaluation import (
    AzureOpenAIGrader,
)
from azure.ai.evaluation import AzureOpenAIModelConfiguration


@pytest.fixture
def mock_aoai_model_config():
    return AzureOpenAIModelConfiguration(
            azure_deployment="...",
            azure_endpoint="...",
            api_key="...",
            api_version="...",
        )


@pytest.fixture
def mock_grader_config():
    return {}

def _get_file(name):
    """Get the file from the unittest data folder."""
    import os, pathlib
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, name)

@pytest.fixture
def questions_file():
    return _get_file("questions.jsonl")

def simple_eval_function():
    return "123"

@pytest.mark.unittest
class TestRemoteEvaluationFeatures:

    def test_eval_name_mapping(self, mock_aoai_model_config, mock_grader_config):
        """
        Test that the name mapping works properly.
        TODO upgrade test to test EVERY KNOWN EVALUATOR.
        """
        # create f1 score eval
        f1_score_eval = F1ScoreEvaluator()
        # create aoai grader
        aoai_grader = AzureOpenAIGrader(model_config=mock_aoai_model_config, grader_config=mock_grader_config)
        from azure.ai.evaluation._evaluate._evaluate import _map_names_to_builtins
        from azure.ai.evaluation._eval_mapping import EVAL_CLASS_MAP

        evaluators = {
            "my_f1": f1_score_eval,
        }
        graders = {
            "my_aoai": aoai_grader,
        }
        result = _map_names_to_builtins(evaluators, graders)
        assert result is not None
        assert result["my_f1"] == EVAL_CLASS_MAP[F1ScoreEvaluator]
        assert result["my_aoai"] == AzureOpenAIGrader.id
