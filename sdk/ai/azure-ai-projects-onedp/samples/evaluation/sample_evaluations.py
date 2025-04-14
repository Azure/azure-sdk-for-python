# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.evaluations` methods to create evaluation that runs in cloud, to get and list evaluations.

USAGE:
    python sample_evaluations.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.projects.onedp import AIProjectClient
from azure.ai.projects.onedp.models import (
    DatasetVersion,
    Evaluation,
    InputDataset,
    EvaluatorConfiguration,
    EvaluationMetrics,
)
from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ["PROJECT_ENDPOINT"]
dataset_name = os.environ["DATASET_NAME"]

with AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
    # credential=AzureKeyCredential(os.environ["PROJECT_API_KEY"]),
) as project_client:

    print("Create evaluation")
    print("Create dataset for evaluation")
    dataset: DatasetVersion = project_client.datasets.upload_file_and_create(
        name=dataset_name,
        version=1,
        file="sample_data/sample_eval.jsonl",
    )
    print(dataset)

    print("Create evaluation object")
    evaluation: Evaluation = Evaluation(
        display_name="My Sample Evaluation",
        data=InputDataset(id="azureml://locations/centraluseuap/workspaces/abc/data/abc/versions/11"),
        # data=InputDataset(id=dataset.id),
        evaluators={
            "relevance": EvaluatorConfiguration(
                id="azureml://registries/azureml/models/Violent-Content-Evaluator/versions/4",
                # id=f"aiservices:{EvaluationMetrics.Relevance.value}",
                init_params={
                    "deployment_name": "gpt-4o",
                },
            ),
            "hate_unfairness": EvaluatorConfiguration(
                id="azureml://registries/azureml/models/Violent-Content-Evaluator/versions/4",
                # id=f"aiservices:{EvaluationMetrics.HateUnfairness.value}",
                init_params={
                    "azure_ai_project": endpoint,
                },
            ),
        },
    )

    print("Submitting Evaluation")
    # Create evaluation
    evaluation_response: Evaluation = project_client.evaluations.create_run(
        evaluation=evaluation,
    )
    print(evaluation_response)

    print("Get evaluation")
    evaluation: Evaluation = project_client.evaluations.get(name=evaluation_response.id)
    print(evaluation)

    print("List evaluations")
    evaluations = project_client.evaluations.list()
    for evaluation in evaluations:
        print(evaluation)
