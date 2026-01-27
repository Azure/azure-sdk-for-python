# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_deploy_project_async.py
DESCRIPTION:
    This sample demonstrates how to deploy a trained model to a deployment slot
    in a Conversation Authoring project (async).

    NOTE ABOUT API VERSIONS:
      - In the 2025-11-01 GA service version:
          * `azureResourceIds` is a list of strings (resource IDs).
      - In the 2025-11-15-preview service version:
          * `azureResourceIds` is a list of AssignedProjectResource objects
            (includes resource ID, region, and optional data-generation settings).

USAGE:
    python sample_deploy_project_async.py

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
    PROJECT_NAME       # defaults to "<project-name>"
    DEPLOYMENT_NAME    # defaults to "<deployment-name>"
    TRAINED_MODEL      # defaults to "<trained-model-label>"
"""

# [START conversation_authoring_deploy_project_async]
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    CreateDeploymentDetails,
)


async def sample_deploy_project_async():
    # Settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    deployment_name = os.environ.get("DEPLOYMENT_NAME", "<deployment-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL", "<trained-model-label>")

    credential = DefaultAzureCredential()

    # 1) 2025-11-01 GA:
    # async with ConversationAuthoringClient(
    #     endpoint,
    #     credential=credential,
    #     api_version="2025-11-01",
    # ) as client:

    # 2) 2025-11-15-preview (current default):
    async with ConversationAuthoringClient(endpoint, credential=credential) as client:
        project_client = client.get_project_client(project_name)

        # Minimal request (works for both versions).
        details = CreateDeploymentDetails(trained_model_label=trained_model_label)

        # --- Example for 2025-11-01 GA: azureResourceIds as list[str] ----------------
        #
        # azure_resource_ids = [
        #     "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/"
        #     "providers/Microsoft.CognitiveServices/accounts/<language-or-ai-account-name>",
        #     "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/"
        #     "providers/Microsoft.CognitiveServices/accounts/<another-account-name>",
        # ]
        #
        # details = CreateDeploymentDetails(
        #     trained_model_label=trained_model_label,
        #     azure_resource_ids=azure_resource_ids,
        # )

        # --- Example for 2025-11-15-preview: azureResourceIds as AssignedProjectResource --
        #
        # assigned_resource = AssignedProjectResource(
        #     resource_id=(
        #         "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/"
        #         "providers/Microsoft.CognitiveServices/accounts/<language-or-ai-account-name>"
        #     ),
        #     region="<region-name>",  # e.g. "westus2"
        #     # assigned_aoai_resource=DataGenerationConnectionInfo(
        #     #     kind="AzureOpenAI",
        #     #     deployment_name="<aoai-deployment-name>",
        #     #     resource_id=(
        #     #         "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/"
        #     #         "providers/Microsoft.CognitiveServices/accounts/<aoai-account-name>"
        #     #     ),
        #     # ),
        # )
        #
        # details = CreateDeploymentDetails(
        #     trained_model_label=trained_model_label,
        #     azure_resource_ids=[assigned_resource],
        # )

        # Start deploy
        poller = await project_client.deployment.begin_deploy_project(
            deployment_name=deployment_name,
            body=details,
        )

        try:
            await poller.result()
            print("Deploy completed.")
            print(f"done: {poller.done()}")
            print(f"status: {poller.status()}")
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)


# [END conversation_authoring_deploy_project_async]


async def main():
    await sample_deploy_project_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
