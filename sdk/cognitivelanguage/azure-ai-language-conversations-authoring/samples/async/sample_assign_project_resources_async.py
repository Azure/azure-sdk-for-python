# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_assign_project_resources_async.py
DESCRIPTION:
    This sample demonstrates how to assign deployment resources to a Conversation Authoring project (async).
USAGE:
    python sample_assign_project_resources_async.py

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
    RESOURCE_ID          # defaults to "<azure-resource-id>"
    RESOURCE_DOMAIN      # defaults to "<custom-domain>"
    RESOURCE_REGION      # defaults to "<region>"
"""

# [START conversation_authoring_assign_project_resources_async]
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ResourceMetadata,
    AssignDeploymentResourcesDetails,
)


async def sample_assign_project_resources_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]

    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    resource_id = os.environ.get("RESOURCE_ID", "<azure-resource-id>")
    resource_domain = os.environ.get("RESOURCE_DOMAIN", "<custom-domain>")
    resource_region = os.environ.get("RESOURCE_REGION", "<region>")

    # async client (AAD)
    credential = DefaultAzureCredential()
    async with ConversationAuthoringClient(endpoint, credential=credential) as client:
        project_client = client.get_project_client(project_name)

        # build request body
        resource = ResourceMetadata(
            azure_resource_id=resource_id,
            custom_domain=resource_domain,
            region=resource_region,
        )
        details = AssignDeploymentResourcesDetails(metadata=[resource])

        # start assign (async long-running operation)
        poller = await project_client.project.begin_assign_project_resources(body=details)

        try:
            await poller.result()
            print("Assign completed.")
            print(f"done: {poller.done()}")
            print(f"status: {poller.status()}")
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)


# [END conversation_authoring_assign_project_resources_async]


async def main():
    await sample_assign_project_resources_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
