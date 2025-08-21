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
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME          # defaults to "<project-name>"
    (Optional) FIRST_DEPLOYMENT      # defaults to "<first-deployment>"
    (Optional) SECOND_DEPLOYMENT     # defaults to "<second-deployment>"
"""

# [START conversation_authoring_swap_deployments_async]
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import SwapDeploymentsDetails, SwapDeploymentsState

async def sample_swap_deployments_async():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]

    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    deployment_name_1 = os.environ.get("FIRST_DEPLOYMENT", "<first-deployment>")
    deployment_name_2 = os.environ.get("SECOND_DEPLOYMENT", "<second-deployment>")

    # create an async client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    try:
        project_client = client.get_project_client(project_name)

        # build swap details
        details = SwapDeploymentsDetails(
            first_deployment_name=deployment_name_1,
            second_deployment_name=deployment_name_2,
        )

        # start swap (async long-running operation)
        poller = await project_client.project.begin_swap_deployments(body=details)

        # wait for job completion and get the result
        result: SwapDeploymentsState = await poller.result()

        # print result details
        print("=== Swap Deployments Result ===")
        print(f"Job ID: {result.job_id}")
        print(f"Status: {result.status}")
        print(f"Created on: {result.created_on}")
        print(f"Last updated on: {result.last_updated_on}")
        print(f"Expires on: {result.expires_on}")
        print(f"Warnings: {result.warnings}")
        print(f"Errors: {result.errors}")
    finally:
        await client.close()

async def main():
    await sample_swap_deployments_async()

if __name__ == "__main__":
    asyncio.run(main())
# [END conversation_authoring_swap_deployments_async]
