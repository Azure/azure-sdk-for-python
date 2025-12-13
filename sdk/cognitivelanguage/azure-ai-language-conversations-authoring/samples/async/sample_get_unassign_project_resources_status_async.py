# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_unassign_project_resources_status_async.py
DESCRIPTION:
    This sample demonstrates how to get the status of a project unassign-resources job in a Conversation Authoring project (async).

USAGE:
    python sample_get_unassign_project_resources_status_async.py

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
    PROJECT_NAME         # defaults to "<project-name>"
"""

# [START conversation_authoring_get_unassign_project_resources_status_async]
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import ProjectResourcesState


async def sample_get_unassign_project_resources_status_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # Example job ID (replace with real one returned by unassign operation)
    job_id = "00000000-0000-0000-0000-000000000000"

    credential = DefaultAzureCredential()
    async with ConversationAuthoringClient(endpoint, credential=credential) as client:
        project_client = client.get_project_client(project_name)

        # start get-status call
        try:
            state = await project_client.project.get_unassign_project_resources_status(job_id)
            print("Status retrieved successfully.")
            print(f"Job ID: {state.job_id}")
            print(f"Status: {state.status}")
            print(f"Created On: {state.created_on}")
            print(f"Last Updated On: {state.last_updated_on}")
            print(f"Expires On: {state.expires_on}")
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)


# [END conversation_authoring_get_unassign_project_resources_status_async]


async def main():
    await sample_get_unassign_project_resources_status_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
