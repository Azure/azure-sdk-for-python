# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_deployment_async.py
DESCRIPTION:
    This sample demonstrates how to retrieve details of a deployment in a Conversation Authoring project (async).
USAGE:
    python sample_get_deployment_async.py
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME      # defaults to "<project-name>"
    (Optional) DEPLOYMENT_NAME   # defaults to "<deployment-name>"
"""

# [START conversation_authoring_get_deployment_async]
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

async def sample_get_deployment_async():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]

    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    deployment_name = os.environ.get("DEPLOYMENT_NAME", "<deployment-name>")

    # create an async client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    try:
        project_client = client.get_project_client(project_name)

        # get deployment details
        deployment = await project_client.deployment.get_deployment(deployment_name=deployment_name)

        print("=== Deployment Details ===")
        print(f"Deployment Name: {getattr(deployment, 'deployment_name', None)}")
        print(f"Model Id: {getattr(deployment, 'model_id', None)}")
        print(f"Last Trained On: {getattr(deployment, 'last_trained_on', None)}")
        print(f"Last Deployed On: {getattr(deployment, 'last_deployed_on', None)}")
        print(f"Deployment Expired On: {getattr(deployment, 'deployment_expired_on', None)}")
        print(f"Model Training Config Version: {getattr(deployment, 'model_training_config_version', None)}")

        # print assigned resources
        assigned_resources = getattr(deployment, "assigned_resources", None)
        if assigned_resources:
            for ar in assigned_resources:
                print(f"Resource ID: {getattr(ar, 'resource_id', None)}")
                print(f"Region: {getattr(ar, 'region', None)}")
                aoai = getattr(ar, "assigned_aoai_resource", None)
                if aoai:
                    print(f"AOAI Kind: {getattr(aoai, 'kind', None)}")
                    print(f"AOAI Resource ID: {getattr(aoai, 'resource_id', None)}")
                    print(f"AOAI Deployment Name: {getattr(aoai, 'deployment_name', None)}")
    finally:
        await client.close()

async def main():
    await sample_get_deployment_async()

if __name__ == "__main__":
    asyncio.run(main())
# [END conversation_authoring_get_deployment_async]
