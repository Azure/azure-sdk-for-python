# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.evaluation._aoai.aoai_grader import AoaiGrader

from azure.ai.projects.models import Evaluation, Dataset, EvaluatorConfiguration


# TODO check out https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/tests/evaluation/test_evaluation.py
# and see if the work here is work bootstrapping
@pytest.mark.usefixtures("recording_injection", "recorded_test")
class TestRemoteEvaluation():

    
    @pytest.mark.skipif(True, reason="WIP")
    def test_remote_aoai_evaluation(self, model_config, project_scope):

        placeholder_grader_config = {
            "type": "stringCheck",
            "model": "gpt-35-turbo",
        }
        grader = AoaiGrader(model_config, placeholder_grader_config)
        eval_config_init_params = {
            "model_config": model_config,
            "grader_config": placeholder_grader_config,
        }

        grader_eval_config = EvaluatorConfiguration(
            id=grader.id,
            init_params=eval_config_init_params,
        )

        f1_eval_config = EvaluatorConfiguration(
            id="azureml://registries/azureml/models/F1Score-Evaluator/versions/4",
            init_params={},
        )

        evalutors = {
            "aoai_grader": grader_eval_config,
            "f1_score": f1_eval_config,
        }

        evaluation = Evaluation(
            display_name="Test Remote AOAI Evaluation",
            description="Evaluation started by test_remote_aoai_evaluation e2e test.",
            evaluators=evalutors,
            data=Dataset(id="..."),
            properties={ "Environment":"..."}
        )

        project_connection_string = "..."
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=project_connection_string,
        )
        breakpoint()
        created_evaluation = project_client.evaluations.create(evaluation)
        breakpoint()
        retrieved_evaluation = project_client.evaluations.get(created_evaluation.id)
        breakpoint()
        pass


        set_bodiless_matcher()
        default_aoai_connection_name = kwargs.pop("azure_ai_projects_evaluations_tests_default_aoai_connection_name")
        project_client = self.get_sync_client(**kwargs)
        default_aoai_connection = project_client.connections.get(
            connection_name=default_aoai_connection_name, include_credentials=True
        )
        deployment_name = kwargs.get("azure_ai_projects_evaluations_tests_deployment_name")
        api_version = kwargs.get("azure_ai_projects_evaluations_tests_api_version")
        model_config = default_aoai_connection.to_evaluator_model_config(
            deployment_name=deployment_name, api_version=api_version, include_credentials=True
        )
        assert model_config["api_key"] == default_aoai_connection.key