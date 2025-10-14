# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    `.evaluations` methods to create, get and list evaluations.

USAGE:
    python sample_evaluations_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) CONNECTION_NAME - Required. The name of the connection of type Azure Storage Account, to use for the dataset upload.
    3) MODEL_ENDPOINT - Required. The Azure OpenAI endpoint associated with your Foundry project.
       It can be found in the Foundry overview page. It has the form https://<account_name>.openai.azure.com.
    4) MODEL_API_KEY - Required. The API key for the model endpoint. Can be found under "key" in the model details page
       (click "Models + endpoints" and select your model to get to the model details page).
    5) MODEL_DEPLOYMENT_NAME - Required. The name of the model deployment to use for evaluation.
    6) DATASET_NAME - Optional. The name of the Dataset to create and use in this sample.
    7) DATASET_VERSION - Optional. The version of the Dataset to create and use in this sample.
    8) DATA_FOLDER - Optional. The folder path where the data files for upload are located.
"""
import asyncio
import os

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    Evaluation,
    InputDataset,
    EvaluatorConfiguration,
    DatasetVersion,
    EvaluatorVersion,
)

# Construct the paths to the data folder and data file used in this sample
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "data_folder"))
data_file = os.path.join(data_folder, "sample_data_evaluation.jsonl")


async def main() -> None:

    endpoint = "https://anksingtest1rp.services.ai.azure.com/api/projects/anksingtest1rpproject"
    connection_name = os.environ["CONNECTION_NAME"]
    model_endpoint = os.environ["MODEL_ENDPOINT"]  # Sample: https://<account_name>.openai.azure.com.
    model_api_key = os.environ["MODEL_API_KEY"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]  # Sample : gpt-4o-mini
    dataset_name = os.environ.get("DATASET_NAME", "eval-data-2025-04-25_224852_UTC")
    dataset_version = os.environ.get("DATASET_VERSION", "1.0")
    evaluator_name = os.environ.get("EVALUATOR_NAME", "builtin.rouge_score")
    evaluator_version = os.environ.get("EVALUATOR_VERSION", "1")

    async with DefaultAzureCredential() as credential:

        async with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

            print("Upload a single file and create a new Dataset to reference the file.")
            dataset: DatasetVersion = await project_client.datasets.get(
                name=dataset_name,
                version=dataset_version
            )
            print(dataset)

            # Get a single evaluator version
            print("Get a single evaluator version")
            evaluator: EvaluatorVersion = await project_client.evaluators.get_evaluator_version(
                name=evaluator_name,
                version=evaluator_version if evaluator_version else "latest",
            )
            print(evaluator)

            print("Create an evaluation")
            evaluation: Evaluation = Evaluation(
                display_name="Sample Evaluation Async",
                description="Sample evaluation for testing",
                # Sample Dataset Id : azureai://accounts/<account_name>/projects/<project_name>/data/<dataset_name>/versions/<version>
                # azureai://accounts/anksingtest1rp/projects/anksingtest1rpproject/data/eval-data-2025-04-25_224852_UTC/versions/1
                data=InputDataset(id=dataset.id if dataset.id else ""),
                evaluators={
                    "rouge_score": EvaluatorConfiguration(
                        id=evaluator.id if evaluator.id else "",
                        init_params={
                            "rouge_type": "",
                            "precision_threshold": 0.5,
                            "recall_threshold": 0.5,
                            "f1_score_threshold": 0.5
                        },
                        data_mapping={
                            "response": "${data.response}",
                            "ground_truth": "${data.query}",    
                        },
                    ),
                },
            )

            evaluation_response: Evaluation = await project_client.evaluations.create(
                evaluation,
                headers={
                    "model-endpoint": model_endpoint,
                    "model-api-key": model_api_key,
                },
            )
            print(evaluation_response)

            print("Get evaluation")
            get_evaluation_response: Evaluation = await project_client.evaluations.get(evaluation_response.name)
            print(get_evaluation_response)

            print("List evaluations")
            async for evaluation in project_client.evaluations.list():
                print(evaluation)


if __name__ == "__main__":
    asyncio.run(main())
