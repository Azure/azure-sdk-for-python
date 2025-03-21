
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    datasets methods to upload files, create datasets that reference those files,
    list datasets and delete datasets.

USAGE:
    python sample_datasets_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) DATASET_NAME - Required. The name of the dataset to create and use in this sample.
"""

import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.dp1.aio import AIProjectClient
from azure.ai.projects.dp1.models import DatasetVersion, ListViewType

async def sample_datasets_async() -> None:

    endpoint = os.environ["PROJECT_ENDPOINT"]
    dataset_name = os.environ["DATASET_NAME"]

    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    print("Upload a single file and create a new dataset to reference the file:")
    dataset: DatasetVersion = await project_client.datasets.upload_file_and_create_version(
        name=dataset_name,
        version="1.0",
        file="sample_folder/file1.txt",
    )
    print(dataset)


    print("Upload all files in a folder (including subfolders) and create a new dataset version to reference the folder:")
    dataset = await project_client.datasets.upload_folder_and_create_version(
        name=dataset_name,
        version="2.0",
        folder="sample_folder",
    )
    print(dataset)


    print("Get the existing dataset version `1.0`:")
    dataset = await project_client.datasets.get_version(name=dataset_name, version="1.0")
    print(dataset)


    print(f"Listing all versions of the dataset named `{dataset_name}`:")
    async for dataset in project_client.datasets.list_versions(name=dataset_name, list_view_type=ListViewType.ALL):
        print(dataset)


    print("List latest versions of all datasets:")
    async for dataset in project_client.datasets.list_latest(list_view_type=ListViewType.ALL):
        print(dataset)


    print("Delete the dataset versions created above:")
    await project_client.datasets.delete_version(name=dataset_name, version="1.0")
    await project_client.datasets.delete_version(name=dataset_name, version="2.0")


async def main():
    await sample_datasets_async()


if __name__ == "__main__":
    asyncio.run(main())
