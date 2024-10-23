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
    pip install azure-ai-project
    pip install azure-ai-evaluation

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os, time
from azure.ai.project import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.project.models import Evaluation, Dataset, EvaluatorConfiguration, ConnectionType
from azure.ai.evaluation import F1ScoreEvaluator, RelevanceEvaluator, ViolenceEvaluator

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str="<connection_string>",
)

# Upload data for evaluation
data_id = project_client.upload_file("./evaluate_test_data.jsonl")
# data_id = "azureml://registries/remote-eval-testing/data/content_harm_data_tiny/versions/1"
# To use an existing dataset, replace the above line with the following line
# data_id = "<dataset_id>"

default_connection = project_client.connections.get_default(connection_type=ConnectionType.AZURE_OPEN_AI)

deployment_name = "gpt-4-ignite-bugbash"
api_version = "2024-08-01-preview"

model_config = default_connection.to_evaluator_model_config(deployment_name=deployment_name, api_version=api_version)

# Create an evaluation
evaluation = Evaluation(
    display_name="Remote Evaluation",
    description="Evaluation of dataset",
    data=Dataset(id=data_id),
    evaluators={
        "f1_score": EvaluatorConfiguration(
            id=F1ScoreEvaluator.id,
        ),
        "relevance": EvaluatorConfiguration(
            id=RelevanceEvaluator.id,
            init_params={
                "model_config": model_config
            },
        ),
        "violence": EvaluatorConfiguration(
            id=ViolenceEvaluator.id,
            init_params={
                "azure_ai_project": project_client.scope
            },
        ),
        "friendliness": EvaluatorConfiguration(
            id="azureml://registries/remote-eval-testing/models/FriendlinessMeasureEvaluator/versions/2",
            init_params={
                "model_config": model_config
            }
        )
    },
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
