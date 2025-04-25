# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    `.indexes` methods to upload a file, create Indexes that reference those files,
    list Indexes and delete Indexes.

USAGE:
    python sample_indexes_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) INDEX_NAME - Required. The name of an Index to create and use in this sample.
"""
import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient


async def sample_indexes_async() -> None:

    endpoint = os.environ["PROJECT_ENDPOINT"]
    index_name = os.environ["INDEX_NAME"]

    async with AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    ) as project_client:

        print("Get an existing Index version `1`:")
        index = await project_client.indexes.get_version(name=index_name, version="1")
        print(index)

        print(f"Listing all versions of the Index named `{index_name}`:")
        async for index in project_client.indexes.list_versions(name=index_name):
            print(index)

        print("List latest versions of all Indexes:")
        async for index in project_client.indexes.list_latest():
            print(index)

        print("Delete the Index versions created above:")
        await project_client.indexes.delete_version(name=index_name, version="1")
        await project_client.indexes.delete_version(name=index_name, version="2")


async def main():
    await sample_indexes_async()


if __name__ == "__main__":
    asyncio.run(main())
