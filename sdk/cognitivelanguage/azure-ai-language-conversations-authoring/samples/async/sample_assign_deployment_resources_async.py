# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_assign_deployment_resources_async.py
DESCRIPTION:
    This sample demonstrates how to assign deployment resources to a Conversation Authoring project (async).
USAGE:
    python sample_assign_deployment_resources_async.py
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME         # defaults to "<project-name>"
    (Optional) RESOURCE_ID          # defaults to "<azure-resource-id>"
    (Optional) RESOURCE_DOMAIN      # defaults to "<custom-domain>"
    (Optional) RESOURCE_REGION      # defaults to "<region>"
"""

# [START conversation_authoring_assign_deployment_resources_async]
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ResourceMetadata,
    AssignDeploymentResourcesDetails,
    DeploymentResourcesState,
)


async def sample_assign_deployment_resources_async():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]

    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    resource_id = os.environ.get("RESOURCE_ID", "<azure-resource-id>")
    resource_domain = os.environ.get("RESOURCE_DOMAIN", "<custom-domain>")
    resource_region = os.environ.get("RESOURCE_REGION", "<region>")

    # create an async client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    try:
        project_client = client.get_project_client(project_name)

        # build request body
        resource = ResourceMetadata(
            azure_resource_id=resource_id,
            custom_domain=resource_domain,
            region=resource_region,
        )
        details = AssignDeploymentResourcesDetails(metadata=[resource])

        # start assign (async long-running operation)
        poller = await project_client.project.begin_assign_deployment_resources(body=details)

        # wait for completion and get the result
        result: DeploymentResourcesState = await poller.result()

        # print result details
        print("=== Assign Deployment Resources Result ===")
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
    await sample_assign_deployment_resources_async()


if __name__ == "__main__":
    asyncio.run(main())
# [END conversation_authoring_assign_deployment_resources_async]
