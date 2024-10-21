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
    python sample_agents_basics.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os, time
from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential
from azure.ai.client.models import Evaluation, Dataset, EvaluatorConfiguration

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# Upload data for evaluation
# Service side fix needed to make this work
# data_id = ai_client.upload_file("./evaluate_test_data.jsonl")
data_id = "azureml://locations/eastus2/workspaces/faa79f3d-91b3-4ed5-afdc-4cc0fe13fb85/data/remote-evals-data/versions/3"

# Create an evaluation
evaluation = Evaluation(
    display_name="Remote Evaluation",
    description="Evaluation of dataset",
    data=Dataset(id=data_id),
    evaluators={
        "f1_score": EvaluatorConfiguration(
            id="azureml://registries/jamahaja-evals-registry/models/F1ScoreEvaluator/versions/1"
        ),
        "relevance": EvaluatorConfiguration(
            id="azureml://registries/jamahaja-evals-registry/models/Relevance-Evaluator-AI-Evaluation/versions/2",
            init_params={
                "model_config": {
                    "api_key": "/subscriptions/e0fd569c-e34a-4249-8c24-e8d723c7f054/resourceGroups/rg-qunsongai/providers/Microsoft.MachineLearningServices/workspaces/qunsong-0951/connections/AOAIRAIEastus2/credentials/key",
                    "azure_deployment": "GPT-4-Prod",
                    "api_version": "2024-08-01-preview",
                    "azure_endpoint": "https://AOAI-RAI-Eastus2.openai.azure.com/",
                }
            },
            # data_mapping= {
            #     "response": "${data.answer}", "query": "${data.question}"
            # }
        ),
    },
    # This is needed as a workaround until environment gets published to registry
    properties={"Environment": "azureml://registries/jamahaja-evals-registry/environments/eval-remote-env/versions/6"},
)

# Create evaluation
evaluation_response = ai_client.evaluations.create(
    evaluation=evaluation,
)

# Get evaluation
get_evaluation_response = ai_client.evaluations.get(evaluation_response.id)

print(get_evaluation_response.as_dict())


# evaluation_json = {
#     "Data": {"Uri": DataUri},
#     "DisplayName": "Remote Evaluation",
#     "Description": "Testing",
#     # "Environment": "azureml://registries/jamahaja-evals-registry/environments/eval-remote-env/versions/2",
#     "Evaluators": {
#         "f1_score": {"Id": "azureml://registries/jamahaja-evals-registry/models/F1ScoreEvaluator/versions/1"},
#         "relevance": {
#             "Id": "azureml://registries/jamahaja-evals-registry/models/Relevance-Evaluator-AI-Evaluation/versions/1",
#             "initParams": {
#                 "model_config": {
#                     "api_key": "/subscriptions/2d385bf4-0756-4a76-aa95-28bf9ed3b625/resourceGroups/rg-anksingai/providers/Microsoft.MachineLearningServices/workspaces/anksing-canary/connections/ai-anksingaicanary931822963616_aoai/credentials/key",
#                     "azure_deployment": "gpt-4",
#                     "api_version": "2023-07-01-preview",
#                     "azure_endpoint": "https://ai-anksingaicanary931822963616.openai.azure.com/",
#                 }
#             },
#         },
#         "hate_unfairness": {
#             "Id": "azureml://registries/jamahaja-evals-registry/models/HateUnfairnessEvaluator/versions/2",
#             "initParams": {
#                 "azure_ai_project": {
#                     "subscription_id": "2d385bf4-0756-4a76-aa95-28bf9ed3b625",
#                     "resource_group_name": "rg-anksingai",
#                     "workspace_name": "anksing-canary",
#                 }
#             },
#         },
#     },
#     "properties": {
#         "Environment": "azureml://registries/jamahaja-evals-registry/environments/eval-remote-env/versions/6",
#         # "_azureml.evaluation_run": "promptflow.BatchRun"
#     },
# }
