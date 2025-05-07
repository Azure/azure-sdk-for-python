# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.ai.evaluation._evaluate._evaluate_aoai import (
    _split_evaluators_and_grader_configs,
    _convert_remote_eval_params_to_grader
)

from azure.ai.evaluation import F1ScoreEvaluator
from azure.ai.evaluation import (
    AzureOpenAIGrader,
    AzureOpenAITextSimilarityGrader,
    AzureOpenAILabelGrader,
    AzureOpenAIStringCheckGrader,
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
class TestAoaiIntegrationFeatures:
    def test_remote_eval_grader_generation(self, mock_aoai_model_config, mock_grader_config):
        """
        Test to ensure that the AoaiGrader class and its children validate their inputs
        properly.
        """
        # Needs a model config
        init_params = {}
        with pytest.raises(Exception) as excinfo:
            _convert_remote_eval_params_to_grader("", init_params=init_params)
        assert "Grader converter needs a valid 'model_config' key in init_params." in str(excinfo.value)

        # needs an ID
        init_params["model_config"] = mock_aoai_model_config
        init_params["grader_config"] = mock_grader_config
        
        with pytest.raises(Exception) as excinfo:
            _convert_remote_eval_params_to_grader("invalid id", init_params=init_params)
        assert "not recognized as an AOAI grader ID" in str(excinfo.value)

        # test general creation creation
        grader = _convert_remote_eval_params_to_grader(AzureOpenAIGrader.id, init_params=init_params)
        assert isinstance(grader, AzureOpenAIGrader)
        assert grader._model_config == mock_aoai_model_config
        assert grader._grader_config == mock_grader_config

        # Test text similarity creation
        init_params = {
            "model_config": mock_aoai_model_config,
            "evaluation_metric": "fuzzy_match",
            "input": "...",
            "pass_threshold": 0.5,
            "reference": "...",
            "name": "test",
        }
        grader = _convert_remote_eval_params_to_grader(AzureOpenAITextSimilarityGrader.id, init_params=init_params)
        assert isinstance(grader, AzureOpenAITextSimilarityGrader)
        assert grader._model_config == mock_aoai_model_config

        # Test string check creation
        init_params = {
            "model_config": mock_aoai_model_config,
            "input": "...",
            "name": "test",
            "operation": "eq",
            "reference": "...",
        }
        grader = _convert_remote_eval_params_to_grader(AzureOpenAIStringCheckGrader.id, init_params=init_params)
        assert isinstance(grader, AzureOpenAIStringCheckGrader)
        assert grader._model_config == mock_aoai_model_config

        # Test label creation
        init_params = {
            "model_config": mock_aoai_model_config,
            "input": [{"content": "...", "role": "user"}],
            "name": "test",
            "labels": ["label1", "label2"],
            "model": "gpt-35-turbo",
            "passing_labels": ["label1"],
        }
        grader = _convert_remote_eval_params_to_grader(AzureOpenAILabelGrader.id, init_params=init_params)
        assert isinstance(grader, AzureOpenAILabelGrader)
        assert grader._model_config == mock_aoai_model_config

    def test_grader_initialization(self, mock_aoai_model_config, mock_grader_config):
        bad_model_config = AzureOpenAIModelConfiguration(
            azure_deployment="...",
            azure_endpoint="...",
        )
        bad_grader_config = {}

        # Test with fully valid inputs
        AzureOpenAIGrader(
            model_config=mock_aoai_model_config,
            grader_config=mock_grader_config
        )

        # missing api_key in model config should throw an error 
        with pytest.raises(Exception) as excinfo:
            AzureOpenAIGrader(
                model_config=bad_model_config,
                grader_config=mock_grader_config
            )
        assert "Requires an api_key in the supplied model_config." in str(excinfo.value)

        # Test that validation bypass works to simplify other tests
        AzureOpenAIGrader(
            model_config=bad_model_config,
            grader_config=bad_grader_config,
            validate=False
        )

        # TODO add checks for bad grader config... maybe.
        # Need to decide if we really want grader validation at base grader level.

    def test_evaluate_grader_recognition(self, mock_aoai_model_config, mock_grader_config):
        """
        Test that checks the ability of the _split_evaluators_and_grader_configs
        method to correctly ID and separate normal, callable evaluators, and
        AOAI graders.
        """
        built_in_eval = F1ScoreEvaluator()
        custom_eval = lambda x: x
        aoai_grader = AzureOpenAIGrader(model_config=mock_aoai_model_config, grader_config=mock_grader_config)
        evaluators = {
            "f1_score": built_in_eval,
            "custom_eval": custom_eval,
            "aoai_grader": aoai_grader
        }

        just_evaluators, aoai_graders = _split_evaluators_and_grader_configs(evaluators)

        assert len(just_evaluators) == 2
        assert len(aoai_graders) == 1

        assert "f1_score" in just_evaluators
        assert "custom_eval" in just_evaluators
        assert "aoai_grader" in aoai_graders
