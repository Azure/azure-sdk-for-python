# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.evaluations` methods to create, get and list evaluations.

USAGE:
    python sample_evaluations.py

    Before running the sample:

    pip install azure-ai-projects azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) CONNECTION_NAME - Required. The name of the connection of type Azure Storage Account, to use for the dataset upload.
    3) MODEL_ENDPOINT - Required. The Azure OpenAI endpoint associated with your Foundry project.
       It can be found in the Foundry overview page. It has the form https://<account_name>.openai.azure.com.
    4) MODEL_API_KEY - Required. The API key for the model endpoint. Can be found under "key" in the model details page
       (click "Models + endpoints" and select your model to get to the model details page).
    5) AZURE_AI_MODEL_DEPLOYMENT_NAME - Required. The name of the model deployment to use for evaluation.
    6) DATASET_NAME - Optional. The name of the Dataset to create and use in this sample.
    7) DATASET_VERSION - Optional. The version of the Dataset to create and use in this sample.
    8) DATA_FOLDER - Optional. The folder path where the data files for upload are located.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    Evaluation,
    InputDataset,
    EvaluatorConfiguration,
    EvaluatorVersion,
    DatasetVersion,
    ModelResponseGenerationTarget,
    SystemMessage,
    DeveloperMessage,
)

load_dotenv()

endpoint = os.environ[
    "AZURE_AI_PROJECT_ENDPOINT"
]  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
connection_name = os.environ.get("CONNECTION_NAME", "")
model_endpoint = os.environ.get("MODEL_ENDPOINT", "")  # Sample: https://<account_name>.openai.azure.com.
model_api_key = os.environ.get("MODEL_API_KEY", "")
model_deployment_name = os.environ.get("MODEL_DEPLOYMENT_NAME", "")  # Sample : gpt-4o-mini
dataset_name = os.environ.get("DATASET_NAME", "eval-data-2025-04-25_224852_UTC")
dataset_version = os.environ.get("DATASET_VERSION", "1")
evaluator_name = os.environ.get("EVALUATOR_NAME", "builtin.rouge_score")
evaluator_version = os.environ.get("EVALUATOR_VERSION", "1")

# Construct the paths to the data folder and data file used in this sample
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "data_folder"))
data_file = os.path.join(data_folder, "sample_data_evaluation.jsonl")

with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential, api_version="2025-10-15-preview") as project_client:

        # [START evaluations_sample]
        print("Upload a single file and create a new Dataset to reference the file.")
        dataset: DatasetVersion = project_client.datasets.get(
            name=dataset_name,
            version=dataset_version,
        )
        print(dataset)
        
        relevance: EvaluatorVersion = project_client.evaluators.get_evaluator_version(name="builtin.relevance", version="latest")
        print("Relevance Evaluator: ", relevance)
        
        violence: EvaluatorVersion = project_client.evaluators.get_evaluator_version(name="builtin.violence", version="latest")
        print("Violence Evaluator: ", violence)
        
        bleu_score: EvaluatorVersion = project_client.evaluators.get_evaluator_version(name="builtin.bleu_score", version="latest")
        print("BLEU Score Evaluator: ", bleu_score)

        print("Create an evaluation")
        evaluation: Evaluation = Evaluation(
            display_name="Sample Evaluation Test",
            description="Sample evaluation for testing",
            # Sample Dataset Id : azureai://accounts/<account_name>/projects/<project_name>/data/<dataset_name>/versions/<version>
            data=InputDataset(id=dataset.id if dataset.id else ""),
            target=ModelResponseGenerationTarget(
                base_messages=[
                    SystemMessage(content= "You are an AI assistant helping users"),
                    DeveloperMessage(content="Could you please provide answers to my questions")
                ],
                model_deployment_name="tiger5/gpt-4o-mini", 
                model_params={
                        "max_tokens": 1024,
                        "temperature": 0.7,
                        "dataMapping": {
                            "query": "${data.query}",
                            "response": "${data.response}",
                        },
                    },
                ),
            evaluators={
                "relevance": EvaluatorConfiguration(
                    id=relevance.id,
                    init_params={
                        "deployment_name": model_deployment_name,
                    },
                    data_mapping={
                        "query": "${data.query}",
                        "response": "${data.response}",
                    },
                ),
                "violence": EvaluatorConfiguration(
                    id=violence.id,
                    init_params={
                        "azure_ai_project": endpoint,
                    },
                ),
                "bleu_score": EvaluatorConfiguration(
                    id=bleu_score.id,
                ),
            },
        )

        evaluation_response: Evaluation = project_client.evaluations.create(
            evaluation
        )
        print(evaluation_response)

        print("Get evaluation")
        get_evaluation_response: Evaluation = project_client.evaluations.get(evaluation_response.name)
        print(get_evaluation_response)

        print("List evaluations")
        for evaluation in project_client.evaluations.list():
            print(evaluation)

        print("Canceling the evaluation")
        # project_client.evaluations.cancel(get_evaluation_response.name)
        print(evaluation_response)
        
        print("deleting the evaluation")
        project_client.evaluations.delete(get_evaluation_response.name)
        
        # [END evaluations_sample]