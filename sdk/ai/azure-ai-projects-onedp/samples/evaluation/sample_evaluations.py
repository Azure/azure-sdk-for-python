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

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) DATASET_NAME - Required. The name of the Dataset to create and use in this sample.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects.onedp import AIProjectClient
from azure.ai.projects.onedp.models import Evaluation, InputDataset, EvaluatorConfiguration, EvaluationMetrics
from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ["PROJECT_ENDPOINT"]
dataset_name = os.environ["DATASET_NAME"]

with AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
) as project_client:

    # [START evaluations_sample]
    print(
        "Upload a single file and create a new Dataset to reference the file. Here we explicitly specify the dataset version."
    )
    # dataset: DatasetVersion = project_client.datasets.upload_file_and_create(
    #     name=dataset_name,
    #     version="1",
    #     file="./samples_folder/sample_data_evaluation.jsonl",
    # )
    # print(dataset)

    print("Create an evaluation")
    # evaluation = Evaluation(
    #     display_name="Sample Evaluation",
    #     data=InputDataset(id="azureml://locations/centraluseuap/workspaces/abc/data/abc/versions/11"),
    #     evaluators={
    #         "relevance": EvaluatorConfiguration(
    #             id=f"aiservices:{EvaluationMetrics.Relevance.value}",
    #             # id="azureml://registries/azureml/models/Retrieval-Evaluator/versions/4",
    #             # either client or service (TBD) resolves to azureml://registries/azureml/models/Retrieval-Evaluator/versions/...
    #             init_params={
    #                 "deployment_name": "gpt-4o",
    #             },
    #         ),
    #         "hate_unfairness": EvaluatorConfiguration(
    #             # id=f"aiservices:{EvaluationMetrics.HateUnfairness.value}",
    #             id="azureml://registries/azureml/models/Retrieval-Evaluator/versions/4",
    #             # either client or service (TBD) resolves to azureml://registries/azureml/models/Hate-Unfairness-Evaluator/versions/...
    #             init_params={
    #                 "azure_ai_project": endpoint,
    #             },
    #         ),
    #     },
    # )
    #
    # evaluation_respone = project_client.evaluations.create_run(evaluation)

    print("Get evaluation")
    # get_evaluation_response = project_client.evaluations.get(evaluation_respone.id)
    # print(get_evaluation_response)

    # [END evaluations_sample]
