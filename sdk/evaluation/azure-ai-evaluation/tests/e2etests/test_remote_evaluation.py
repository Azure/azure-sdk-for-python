# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.ai.projects.models import EvaluatorConfiguration
from azure.ai.evaluation import (
    AzureOpenAILabelGrader,
    AzureOpenAIStringCheckGrader,
    AzureOpenAITextSimilarityGrader,
    AzureOpenAIGrader,
)
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import Evaluation, Dataset
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import Evaluation, Dataset, EvaluatorConfiguration


# TODO check out https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/tests/evaluation/test_evaluation.py
# and see if the work here is work bootstrapping
@pytest.mark.usefixtures("recording_injection", "recorded_test")
class TestRemoteEvaluation():

    
    @pytest.mark.skipif(True, reason="WIP")
    def test_remote_aoai_evaluation(self, model_config, project_scope):
        sim_grader_config = EvaluatorConfiguration(
            id=AzureOpenAITextSimilarityGrader.id,
            init_params={
                "model_config": model_config,
                "evaluation_metric": "fuzzy_match",
                "input": "{{item.query}}",
                "name": "similarity",
                "pass_threshold": 1,
                "reference": "{{item.query}}",
            },
        )

        string_grader_config = EvaluatorConfiguration(
            id=AzureOpenAIStringCheckGrader.id,
            init_params={
                "model_config": model_config,
                "input": "{{item.query}}",
                "name": "contains hello",
                "operation": "like",
                "reference": "hello",
            },
        )

        label_grader_config = EvaluatorConfiguration(
            id=AzureOpenAILabelGrader.id,
            init_params={
                "model_config": model_config,
                "input": [{"content": "{{item.query}}", "role": "user"}],
                "labels": ["too short", "just right", "too long"],
                "passing_labels": ["just right"],
                "model": "gpt-4o",
                "name": "label",
            },
        )

        general_grader_config = EvaluatorConfiguration(
            id=AzureOpenAIGrader.id,
            init_params={
                "model_config": model_config,
                "grader_config": {
                    "input": "{{item.query}}",
                    "name": "contains hello",
                    "operation": "like",
                    "reference": "hello",
                    "type": "string_check",
                },
            },
        )

        from azure.ai.projects import AIProjectClient
        from azure.ai.projects.models import Evaluation, Dataset
        from azure.identity import DefaultAzureCredential
        # Note you might want to change the run name to avoid confusion with others
        run_name = "Test Remote AOAI Evaluation"
        evaluation = Evaluation(
            display_name=run_name,
            description="Evaluation started by test_remote_aoai_evaluation e2e test.",
            evaluators = {
                "label": label_grader_config,
                "general": general_grader_config,
                "string": string_grader_config,
                "similarity": sim_grader_config,
            },
            data=Dataset(id=dataset_id),
        )
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=project_connection_string,
        )
        created_evaluation = project_client.evaluations.create(evaluation)
        retrieved_evaluation = project_client.evaluations.get(created_evaluation.id)


