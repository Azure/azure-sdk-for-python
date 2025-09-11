# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_delete_project_async.py
DESCRIPTION:
    This sample demonstrates how to delete a **Text Authoring** project (async).
USAGE:
    python sample_delete_project_async.py
REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_TEXT_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET
NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_TEXT_ENDPOINT
      - AZURE_TEXT_KEY
OPTIONAL ENV VARS:
    PROJECT_NAME  # defaults to "<project-name>"
"""

# [START text_authoring_delete_project_async]
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient


async def sample_delete_project_async():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    async with TextAuthoringClient(endpoint, credential=credential) as client:
        # delete the project (LRO)
        poller = await client.begin_delete_project(project_name)

        # handle success/error from the LRO
        try:
            await poller.result()  # completes with None; raises on failure
            print("Delete completed.")
            print(f"done: {poller.done()}")
            print(f"status: {poller.status()}")
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)


# [END text_authoring_delete_project_async]


async def main():
    await sample_delete_project_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
