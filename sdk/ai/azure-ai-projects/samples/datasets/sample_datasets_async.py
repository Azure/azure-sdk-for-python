# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    `.datasets` methods to upload files, create Datasets that reference those files,
    list Datasets and delete Datasets.

USAGE:
    python sample_datasets_async.py

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
from azure.ai.projects.models import DatasetVersion


async def sample_datasets_async() -> None:

    endpoint = os.environ["PROJECT_ENDPOINT"]
    dataset_name = os.environ["DATASET_NAME"]

    async with AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    ) as project_client:

        print(
            """Upload a single file and create a new Dataset to reference the file.
        Here we explicitly specify the dataset version."""
        )
        dataset: DatasetVersion = await project_client.datasets.upload_file_and_create(
            name=dataset_name,
            version="1",
            file="sample_folder/sample_file1.txt",
        )
        print(dataset)

        """
        print("Upload all files in a folder (including subfolders) to the existing Dataset to reference the folder. Here again we explicitly specify the a new dataset version")
        dataset = await project_client.datasets.upload_folder_and_create(
            name=dataset_name,
            version="2",
            folder="sample_folder",
        )
        print(dataset)

        print("Upload a single file to the existing dataset, while letting the service increment the version")
        dataset: DatasetVersion = await project_client.datasets.upload_file_and_create(
            name=dataset_name,
            file="sample_folder/file2.txt",
        )
        print(dataset)

        print("Get an existing Dataset version `1`:")
        dataset = await project_client.datasets.get_version(name=dataset_name, version="1")
        print(dataset)

        print(f"Listing all versions of the Dataset named `{dataset_name}`:")
        async for dataset in project_client.datasets.list_versions(name=dataset_name):
            print(dataset)

        print("List latest versions of all Datasets:")
        async for dataset in project_client.datasets.list_latest():
            print(dataset)

        print("Delete all Dataset versions created above:")
        await project_client.datasets.delete_version(name=dataset_name, version="1")
        await project_client.datasets.delete_version(name=dataset_name, version="2")
        await project_client.datasets.delete_version(name=dataset_name, version="3")
        """


async def main():
    await sample_datasets_async()


if __name__ == "__main__":
    asyncio.run(main())
