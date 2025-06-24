# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    `.telemetry` methods to get the Application Insights connection string and enable
    tracing.

USAGE:
    python sample_telemetry_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
"""

import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import ConnectionType


async def main() -> None:

    endpoint = os.environ["PROJECT_ENDPOINT"]

    async with DefaultAzureCredential() as credential:

        async with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

            print("Get the Application Insights connection string:")
            connection_string = await project_client.telemetry.get_connection_string()
            print(connection_string)


if __name__ == "__main__":
    asyncio.run(main())
