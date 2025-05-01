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
    2) DATASET_NAME - Optional. The name of the Dataset to create and use in this sample.
    3) DATASET_VERSION_1 - Optional. The first version of the Dataset to create and use in this sample.
    4) DATASET_VERSION_2 - Optional. The second version of the Dataset to create and use in this sample.
"""

import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import DatasetVersion


async def sample_datasets_async() -> None:

    endpoint = os.environ["PROJECT_ENDPOINT"]
    dataset_name = os.environ.get("DATASET_NAME", "dataset-test")
    dataset_version_1 = os.environ.get("DATASET_VERSION_1", "1.0")
    dataset_version_2 = os.environ.get("DATASET_VERSION_2", "2.0")

    async with DefaultAzureCredential() as credential:

        async with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

            print(
                f"Upload a single file and create a new Dataset `{dataset_name}`, version `{dataset_version_1}`, to reference the file."
            )
            dataset: DatasetVersion = await project_client.datasets.upload_file(
                name=dataset_name,
                version=dataset_version_1,
                file_path="sample_folder/sample_file1.txt",
            )
            print(dataset)

            print(
                f"Upload all files in a folder (including sub-folders) and create a new version `{dataset_version_2}` in the same Dataset, to reference the files."
            )
            dataset = await project_client.datasets.upload_folder(
                name=dataset_name,
                version=dataset_version_2,
                folder="sample_folder",
            )
            print(dataset)

            print(f"Get an existing Dataset version `{dataset_version_1}`:")
            dataset = await project_client.datasets.get(name=dataset_name, version=dataset_version_1)
            print(dataset)

            print("List latest versions of all Datasets:")
            async for dataset in project_client.datasets.list():
                print(dataset)

            print(f"Listing all versions of the Dataset named `{dataset_name}`:")
            async for dataset in project_client.datasets.list_versions(name=dataset_name):
                print(dataset)

            print("Delete all Dataset versions created above:")
            await project_client.datasets.delete(name=dataset_name, version=dataset_version_1)
            await project_client.datasets.delete(name=dataset_name, version=dataset_version_2)


async def main():
    await sample_datasets_async()


if __name__ == "__main__":
    asyncio.run(main())
