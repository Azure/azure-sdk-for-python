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
       Azure AI Foundry project.
    2) DATASET_NAME - Required. The name of the Dataset to create and use in this sample.
"""
import asyncio
import os

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    Evaluation,
    InputDataset,
    EvaluatorConfiguration,
    EvaluatorIds,
    # DatasetVersion,
)


async def main() -> None:
    endpoint = os.environ[
        "PROJECT_ENDPOINT"
    ]  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
    model_endpoint = os.environ["MODEL_ENDPOINT"]  # Sample : https://<account_name>.services.ai.azure.com
    model_api_key = os.environ["MODEL_API_KEY"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]  # Sample : gpt-4o-mini

    async with DefaultAzureCredential() as credential:

        async with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

            # [START evaluations_sample]
            # TODO : Uncomment the following lines once dataset creation works
            # print(
            #     "Upload a single file and create a new Dataset to reference the file. Here we explicitly specify the dataset version."
            # )
            # dataset: DatasetVersion = await project_client.datasets.upload_file(
            #     name=dataset_name,
            #     version="1",
            #     file="./samples_folder/sample_data_evaluation.jsonl",
            # )
            # print(dataset)

            print("Create an evaluation")
            evaluation: Evaluation = Evaluation(
                display_name="Sample Evaluation Async",
                description="Sample evaluation for testing",
                # Sample Dataset Id : azureai://accounts/<account_name>/projects/<project_name>/data/<dataset_name>/versions/<version>
                data=InputDataset(id="<>"),
                evaluators={
                    "relevance": EvaluatorConfiguration(
                        id=EvaluatorIds.RELEVANCE.value,
                        init_params={
                            "deployment_name": model_deployment_name,
                        },
                        data_mapping={
                            "query": "${data.query}",
                            "response": "${data.response}",
                        },
                    ),
                    "violence": EvaluatorConfiguration(
                        id=EvaluatorIds.VIOLENCE.value,
                        init_params={
                            "azure_ai_project": endpoint,
                        },
                    ),
                    "bleu_score": EvaluatorConfiguration(
                        id=EvaluatorIds.BLEU_SCORE.value,
                    ),
                },
            )

            evaluation_response: Evaluation = await project_client.evaluations.create(
                evaluation,
                headers={
                    "model-endpoint": model_endpoint,
                    "api-key": model_api_key,
                },
            )
            print(evaluation_response)

            print("Get evaluation")
            get_evaluation_response: Evaluation = await project_client.evaluations.get(evaluation_response.name)

            print(get_evaluation_response)

            print("List evaluations")
            async for evaluation in project_client.evaluations.list():
                print(evaluation)

            # [END evaluations_sample]


if __name__ == "__main__":
    asyncio.run(main())
