# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_swap_deployments_async.py
DESCRIPTION:
    This sample demonstrates how to swap two deployments within a Conversation Authoring project (async).
USAGE:
    python sample_swap_deployments_async.py

REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET

NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
      - AZURE_CONVERSATIONS_AUTHORING_KEY

OPTIONAL ENV VARS:
    PROJECT_NAME          # defaults to "<project-name>"
    FIRST_DEPLOYMENT      # defaults to "<first-deployment>"
    SECOND_DEPLOYMENT     # defaults to "<second-deployment>"
"""

# [START conversation_authoring_swap_deployments_async]
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import SwapDeploymentsDetails


async def sample_swap_deployments_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    deployment_name_1 = os.environ.get("FIRST_DEPLOYMENT", "<first-deployment>")
    deployment_name_2 = os.environ.get("SECOND_DEPLOYMENT", "<second-deployment>")

    credential = DefaultAzureCredential()
    async with ConversationAuthoringClient(endpoint, credential=credential) as client:
        project_client = client.get_project_client(project_name)

        # build swap details
        details = SwapDeploymentsDetails(
            first_deployment_name=deployment_name_1,
            second_deployment_name=deployment_name_2,
        )

        # start swap (async long-running operation)
        poller = await project_client.project.begin_swap_deployments(body=details)

        try:
            await poller.result()
            print("Swap completed.")
            print(f"done: {poller.done()}")
            print(f"status: {poller.status()}")
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)


# [END conversation_authoring_swap_deployments_async]


async def main():
    await sample_swap_deployments_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
