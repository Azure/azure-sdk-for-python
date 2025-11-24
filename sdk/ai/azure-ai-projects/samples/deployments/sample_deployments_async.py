# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    `.deployments` methods to enumerate AI models deployed to your Microsoft Foundry Project.

USAGE:
    python sample_deployments_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv aiohttp 

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - Required. The name of the deployment to retrieve.
    3) MODEL_PUBLISHER - Optional. The publisher of the model to filter by.
    4) MODEL_NAME - Optional. The name of the model to filter by.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import ModelDeployment

load_dotenv()


async def main() -> None:

    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]
    model_publisher = os.environ.get("MODEL_PUBLISHER", "Microsoft")
    model_name = os.environ.get("MODEL_NAME", "Phi-4")

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        print("List all deployments:")
        async for deployment in project_client.deployments.list():
            print(deployment)

        print(f"List all deployments by the model publisher `{model_publisher}`:")
        async for deployment in project_client.deployments.list(model_publisher=model_publisher):
            print(deployment)

        print(f"List all deployments of model `{model_name}`:")
        async for deployment in project_client.deployments.list(model_name=model_name):
            print(deployment)

        print(f"Get a single deployment named `{model_deployment_name}`:")
        deployment = await project_client.deployments.get(model_deployment_name)
        print(deployment)

        # At the moment, the only deployment type supported is ModelDeployment
        if isinstance(deployment, ModelDeployment):
            print(f"Type: {deployment.type}")
            print(f"Name: {deployment.name}")
            print(f"Model Name: {deployment.model_name}")
            print(f"Model Version: {deployment.model_version}")
            print(f"Model Publisher: {deployment.model_publisher}")
            print(f"Capabilities: {deployment.capabilities}")
            print(f"SKU: {deployment.sku}")
            print(f"Connection Name: {deployment.connection_name}")


if __name__ == "__main__":
    asyncio.run(main())
