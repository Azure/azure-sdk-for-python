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
    2) CONNECTION_NAME - Required. The name of the Azure Storage Account connection to use for uploading files.
    3) DATASET_NAME - Optional. The name of the Dataset to create and use in this sample.
    4) DATASET_VERSION_1 - Optional. The first version of the Dataset to create and use in this sample.
    5) DATASET_VERSION_2 - Optional. The second version of the Dataset to create and use in this sample.
    6) DATA_FOLDER - Optional. The folder path where the data files for upload are located.
"""

import asyncio
import os
import re
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import DatasetVersion

# Construct the paths to the data folder and data file used in this sample
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "data_folder"))
data_file = os.path.join(data_folder, "data_file1.txt")


async def main() -> None:

    endpoint = os.environ["PROJECT_ENDPOINT"]
    connection_name = os.environ["CONNECTION_NAME"]
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
                file_path=data_file,
                connection_name=connection_name,
            )
            print(dataset)

            print(
                f"Upload files in a folder (including sub-folders) and create a new version `{dataset_version_2}` in the same Dataset, to reference the files."
            )
            dataset = await project_client.datasets.upload_folder(
                name=dataset_name,
                version=dataset_version_2,
                folder=data_folder,
                connection_name=connection_name,
                file_pattern=re.compile(r"\.(txt|csv|md)$", re.IGNORECASE),
            )
            print(dataset)

            print(f"Get an existing Dataset version `{dataset_version_1}`:")
            dataset = await project_client.datasets.get(name=dataset_name, version=dataset_version_1)
            print(dataset)

            print(f"Get credentials of an existing Dataset version `{dataset_version_1}`:")
            asset_credential = await project_client.datasets.get_credentials(
                name=dataset_name, version=dataset_version_1
            )
            print(asset_credential)

            print("List latest versions of all Datasets:")
            async for dataset in project_client.datasets.list():
                print(dataset)

            print(f"Listing all versions of the Dataset named `{dataset_name}`:")
            async for dataset in project_client.datasets.list_versions(name=dataset_name):
                print(dataset)

            print("Delete all Dataset versions created above:")
            await project_client.datasets.delete(name=dataset_name, version=dataset_version_1)
            await project_client.datasets.delete(name=dataset_name, version=dataset_version_2)


if __name__ == "__main__":
    asyncio.run(main())
