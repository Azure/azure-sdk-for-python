import os
from pprint import pprint

from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential

from azure.ai.client.models import Evaluation, Dataset, EvaluatorConfiguration


# Project Configuration Canary
Subscription = "2d385bf4-0756-4a76-aa95-28bf9ed3b625"
ResourceGroup = "rg-anksingai"
Workspace = "anksing-canary"
DataUri = "azureml://locations/eastus2euap/workspaces/a51c1ea7-5c29-4c32-a98e-7fa752f36e7c/data/test-remote-eval-data/versions/1"
Endpoint = "https://eastus2euap.api.azureml.ms"

# Create an Azure AI client
ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    connection=f"{Endpoint};{Subscription};{ResourceGroup};{Workspace}",
    logging_enable=True,  # Optional. Remove this line if you don't want to show how to enable logging
)

# Create an evaluation
evaluation = Evaluation(
    display_name="Remote Evaluation",
    description="Evaluation of dataset",
    data=Dataset(id=DataUri),
    evaluators={
        "f1_score": EvaluatorConfiguration(
            id="azureml://registries/jamahaja-evals-registry/models/F1ScoreEvaluator/versions/1"
        ),
        "relevance": EvaluatorConfiguration(
            id="azureml://registries/jamahaja-evals-registry/models/Relevance-Evaluator-AI-Evaluation/versions/2",
            init_params={
                "model_config": {
                    "api_key": "/subscriptions/2d385bf4-0756-4a76-aa95-28bf9ed3b625/resourceGroups/rg-anksingai/providers/Microsoft.MachineLearningServices/workspaces/anksing-canary/connections/ai-anksingai0771286510468288/credentials/key",
                    "azure_deployment": "gpt-4",
                    "api_version": "2023-07-01-preview",
                    "azure_endpoint": "https://ai-anksingai0771286510468288.openai.azure.com/",
                }
            },
        ),
    },
    # This is needed as a workaround until environment gets published to registry
    properties={"Environment": "azureml://registries/jamahaja-evals-registry/environments/eval-remote-env/versions/6"},
)

# Create evaluation
evaluation_response = ai_client.evaluations.create(
    evaluation=evaluation,
)

pprint(evaluation_response.as_dict())

# Get evaluation
get_evaluation_response = ai_client.evaluations.get(evaluation_response.id)

pprint(get_evaluation_response.as_dict())


evaluation_json = {
    "Data": {"Uri": DataUri},
    "DisplayName": "Remote Evaluation",
    "Description": "Testing",
    # "Environment": "azureml://registries/jamahaja-evals-registry/environments/eval-remote-env/versions/2",
    "Evaluators": {
        "f1_score": {"Id": "azureml://registries/jamahaja-evals-registry/models/F1ScoreEvaluator/versions/1"},
        "relevance": {
            "Id": "azureml://registries/jamahaja-evals-registry/models/Relevance-Evaluator-AI-Evaluation/versions/1",
            "initParams": {
                "model_config": {
                    "api_key": "/subscriptions/2d385bf4-0756-4a76-aa95-28bf9ed3b625/resourceGroups/rg-anksingai/providers/Microsoft.MachineLearningServices/workspaces/anksing-canary/connections/ai-anksingaicanary931822963616_aoai/credentials/key",
                    "azure_deployment": "gpt-4",
                    "api_version": "2023-07-01-preview",
                    "azure_endpoint": "https://ai-anksingaicanary931822963616.openai.azure.com/",
                }
            },
        },
        "hate_unfairness": {
            "Id": "azureml://registries/jamahaja-evals-registry/models/HateUnfairnessEvaluator/versions/2",
            "initParams": {
                "azure_ai_project": {
                    "subscription_id": "2d385bf4-0756-4a76-aa95-28bf9ed3b625",
                    "resource_group_name": "rg-anksingai",
                    "workspace_name": "anksing-canary",
                }
            },
        },
    },
    "properties": {
        "Environment": "azureml://registries/jamahaja-evals-registry/environments/eval-remote-env/versions/6",
        # "_azureml.evaluation_run": "promptflow.BatchRun"
    },
}
