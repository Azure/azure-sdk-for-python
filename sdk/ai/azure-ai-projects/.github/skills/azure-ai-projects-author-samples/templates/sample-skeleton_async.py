# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use <feature> with the asynchronous
    AIProjectClient.

USAGE:
    python sample_<feature>_async.py

    Before running the sample:

    pip install "azure-ai-projects" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Microsoft Foundry project endpoint.
"""

import asyncio
import os

from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]


async def main() -> None:
    created_resource = None

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        try:
            # TODO(<feature>): await the public operation and print meaningful results.
            created_resource = project_client
            print("Completed <feature> workflow")
        finally:
            if created_resource is not None:
                # TODO(<feature>): await deletion of service resources created by this sample.
                pass


if __name__ == "__main__":
    asyncio.run(main())
