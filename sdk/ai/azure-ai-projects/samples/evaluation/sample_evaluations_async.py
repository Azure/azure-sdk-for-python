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
    DatasetVersion,
)
from dotenv import load_dotenv

load_dotenv()


async def sample_evaluations_async() -> None:
    endpoint = os.environ["PROJECT_ENDPOINT"]
    dataset_name = os.environ["DATASET_NAME"]

    async with AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
    ) as project_client:

        # [START evaluations_sample]
        # TODO : Uncomment the following lines once dataset creation works
        # print(
        #     "Upload a single file and create a new Dataset to reference the file. Here we explicitly specify the dataset version."
        # )
        # dataset: DatasetVersion = await project_client.datasets.upload_file_and_create(
        #     name=dataset_name,
        #     version="1",
        #     file="./samples_folder/sample_data_evaluation.jsonl",
        # )
        # print(dataset)

        print("Create an evaluation")
        evaluation: Evaluation = Evaluation(
            display_name="Sample Evaluation",
            description="Sample evaluation for testing",  # TODO: Can we optional once bug 4115256 is fixed
            data=InputDataset(id="<dataset_id>"),  # TODO: update this to use the correct id
            evaluators={
                "relevance": EvaluatorConfiguration(
                    id=EvaluatorIds.RELEVANCE.value,  # TODO: update this to use the correct id
                    init_params={
                        "deployment_name": "gpt-4o",
                    },
                ),
            },
        )

        evaluation_response: Evaluation = await project_client.evaluations.create_run(evaluation)
        print(evaluation_response)

        print("Get evaluation")
        get_evaluation_response: Evaluation = await project_client.evaluations.get(evaluation_response.name)

        print(get_evaluation_response)

        print("List evaluations")
        async for evaluation in project_client.evaluations.list():
            print(evaluation)

        # [END evaluations_sample]


async def main():
    await sample_evaluations_async()


if __name__ == "__main__":
    asyncio.run(main())
