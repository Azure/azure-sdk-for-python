# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on Toolboxes
    using the asynchronous AIProjectClient.

    Toolboxes are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.toolboxes`.

USAGE:
    python sample_toolboxes_crud_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.2" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
"""

import asyncio
import os

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import MCPTool, Tool

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]


async def main() -> None:

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        toolbox_name = "mcp"

        try:
            await project_client.beta.toolboxes.delete(toolbox_name)
            print(f"Toolbox `{toolbox_name}` deleted")
        except ResourceNotFoundError:
            pass

        tools: list[Tool] = [
            MCPTool(
                server_label="api_specs",
                server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
                require_approval="never",
            )
        ]

        created = await project_client.beta.toolboxes.create(
            toolbox_name=toolbox_name,
            description="Example toolbox created by the azure-ai-projects sample.",
            metadata={"status": "created"},
            tools=tools,
        )
        status = created.metadata.get("status", "unknown status") if created.metadata else "unknown status"
        print(f"Toolbox: {created.name} (tools: {len(created.tools)}) (status: {status})")

        fetched = await project_client.beta.toolboxes.get(toolbox_name=toolbox_name)
        print(f"Retrieved toolbox: {fetched.name} ({fetched.id})")

        # TODO: Restore this
        # updated = await project_client.beta.toolboxes.update(
        #     toolbox_name=toolbox_name,
        #     description="Updated description for the sample toolbox.",
        #     metadata={"status": "updated"},
        #     tools=tools,
        # )
        # status = updated.metadata.get("status", "unknown status") if updated.metadata else "unknown status"
        # print(f"Toolbox: {updated.name} (tools: {len(updated.tools)}) (status: {status})")

        toolboxes: list[str] = []
        async for item in project_client.beta.toolboxes.list(limit=10):
            toolboxes.append(item.name)
        print(f"Found {len(toolboxes)} toolboxes")

        await project_client.beta.toolboxes.delete(toolbox_name=toolbox_name)
        print("Toolbox deleted")


if __name__ == "__main__":
    asyncio.run(main())
