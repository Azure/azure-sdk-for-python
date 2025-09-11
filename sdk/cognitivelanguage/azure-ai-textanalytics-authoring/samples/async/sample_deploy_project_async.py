# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_deploy_project_async.py
DESCRIPTION:
    This sample demonstrates how to deploy a **Text Authoring** project (async).
USAGE:
    python sample_deploy_project_async.py
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
    PROJECT_NAME         # defaults to "<project-name>"
    DEPLOYMENT_NAME      # defaults to "<deployment-name>"
    TRAINED_MODEL_LABEL  # defaults to "<trained-model-label>"
"""

# [START text_authoring_deploy_project_async]
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import CreateDeploymentDetails


async def sample_deploy_project_async():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    deployment_name = os.environ.get("DEPLOYMENT_NAME", "<deployment-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL_LABEL", "<trained-model-label>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    async with TextAuthoringClient(endpoint, credential=credential) as client:
        # project-scoped client
        project_client = client.get_project_client(project_name)

        # build request body for deployment
        details = CreateDeploymentDetails(trained_model_label=trained_model_label)

        # begin deploy (LRO) and handle success/error
        poller = await project_client.deployment.begin_deploy_project(
            deployment_name=deployment_name,
            body=details,
        )
        try:
            await poller.result()  # completes with None; raises on failure
            print("Deploy completed.")
            print(f"done: {poller.done()}")
            print(f"status: {poller.status()}")
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)


# [END text_authoring_deploy_project_async]


async def main():
    await sample_deploy_project_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
