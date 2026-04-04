# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_swap_deployments_async.py
DESCRIPTION:
    This sample demonstrates how to swap two **Text Authoring** deployments within a project (async).
USAGE:
    python sample_swap_deployments_async.py
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
    PROJECT_NAME            # defaults to "<project-name>"
    FIRST_DEPLOYMENT_NAME   # defaults to "<deployment-name-1>"
    SECOND_DEPLOYMENT_NAME  # defaults to "<deployment-name-2>"
"""

# [START text_authoring_swap_deployments_async]
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import SwapDeploymentsDetails


async def sample_swap_deployments_async():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    first_deployment = os.environ.get("FIRST_DEPLOYMENT_NAME", "<deployment-name-1>")
    second_deployment = os.environ.get("SECOND_DEPLOYMENT_NAME", "<deployment-name-2>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    async with TextAuthoringClient(endpoint, credential=credential) as client:
        # project-scoped client
        project_client = client.get_project_client(project_name)

        # prepare swap details
        details = SwapDeploymentsDetails(
            first_deployment_name=first_deployment,
            second_deployment_name=second_deployment,
        )

        # begin swap (LRO) and handle success/error
        poller = await project_client.project.begin_swap_deployments(body=details)
        try:
            await poller.result()  # completes with None; raises on failure
            print("Swap deployments completed.")
            print(f"done: {poller.done()}")
            print(f"status: {poller.status()}")
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)


# [END text_authoring_swap_deployments_async]


async def main():
    await sample_swap_deployments_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
