# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_unassign_deployment_resources_async.py
DESCRIPTION:
    This sample demonstrates how to unassign deployment resources from a Text Authoring project (async).
USAGE:
    python sample_unassign_deployment_resources_async.py
REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_TEXT_AUTHORING_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET
NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_TEXT_AUTHORING_ENDPOINT
      - AZURE_TEXT_AUTHORING_KEY
OPTIONAL ENV VARS:
    PROJECT_NAME   # defaults to "<project-name>"
    RESOURCE_ID    # defaults to "<azure-resource-id>"
"""

# [START text_authoring_unassign_deployment_resources_async]
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    UnassignDeploymentResourcesDetails,
)


async def sample_unassign_deploy_resources_async():
    # settings
    endpoint = os.environ["AZURE_TEXT_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    resource_id = os.environ.get("RESOURCE_ID", "<azure-resource-id>")

    credential = DefaultAzureCredential()
    async with TextAuthoringClient(endpoint, credential=credential) as client:
        # get project-scoped client
        project_client = client.get_project_client(project_name)

        # build request body
        details = UnassignDeploymentResourcesDetails(assigned_resource_ids=[resource_id])

        # start unassign (async long-running operation)
        poller = await project_client.project.begin_unassign_deployment_resources(body=details)

        try:
            await poller.result()
            print("Unassign completed.")
            print(f"done: {poller.done()}")
            print(f"status: {poller.status()}")
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)


# [END text_authoring_unassign_deployment_resources_async]


async def main():
    await sample_unassign_deploy_resources_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
