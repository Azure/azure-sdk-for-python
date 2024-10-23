# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_basics.py

DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_evaluations.py

    Before running the sample:

    pip install azure-identity
    pip install "git+https://github.com/Azure/azure-sdk-for-python.git@users/singankit/ai_project_utils#egg=azure-ai-client&subdirectory=sdk/ai/azure-ai-client"
    pip install "git+https://github.com/Azure/azure-sdk-for-python.git@users/singankit/demo_evaluators_id#egg=azure-ai-evaluation&subdirectory=sdk/evaluation/azure-ai-evaluation"

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os, time
from azure.ai.project import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.project.models import Evaluation, Dataset, EvaluatorConfiguration, ConnectionType
from azure.ai.evaluation import F1ScoreEvaluator, RelevanceEvaluator, HateUnfairnessEvaluator

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# Upload data for evaluation
# Service side fix needed to make this work
# data_id = project_client.upload_file("./evaluate_test_data.jsonl")
data_id = (
    "azureml://locations/eastus2/workspaces/faa79f3d-91b3-4ed5-afdc-4cc0fe13fb85/data/remote-evals-data/versions/3"
)

default_connection = project_client.connections.get_default(connection_type=ConnectionType.AZURE_OPEN_AI)


# Create an evaluation
evaluation = Evaluation(
    display_name="Remote Evaluation",
    description="Evaluation of dataset",
    data=Dataset(id=data_id),
    evaluators={
        "f1_score": EvaluatorConfiguration(
            id=F1ScoreEvaluator.evaluator_id,
        ),
        "relevance": EvaluatorConfiguration(
            id=RelevanceEvaluator.evaluator_id,
            init_params={
                "model_config": default_connection.to_evaluator_model_config(
                    deployment_name="GPT-4-Prod", api_version="2024-08-01-preview"
                )
            },
        ),
        "hate_unfairness": EvaluatorConfiguration(
            id=HateUnfairnessEvaluator.evaluator_id,
            init_params={"azure_ai_project": project_client.scope},
        ),
    },
    # This is needed as a workaround until environment gets published to registry
    properties={"Environment": "azureml://registries/jamahaja-evals-registry/environments/eval-remote-env/versions/6"},
)

# Create evaluation
evaluation_response = project_client.evaluations.create(
    evaluation=evaluation,
)

# Get evaluation
get_evaluation_response = project_client.evaluations.get(evaluation_response.id)

print("----------------------------------------------------------------")
print("Created evaluation, evaluation ID: ", get_evaluation_response.id)
print("Evaluation status: ", get_evaluation_response.status)
print("AI Studio URI: ", get_evaluation_response.properties["AiStudioEvaluationUri"])
print("----------------------------------------------------------------")
