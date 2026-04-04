# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on Toolboxes
    using the synchronous AIProjectClient.

    Toolboxes are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.toolboxes`.

USAGE:
    python sample_toolboxes_crud.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.2" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
"""

import os

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPTool, Tool

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    toolbox_name = "mcp"

    try:
        project_client.beta.toolboxes.delete(toolbox_name)
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

    created = project_client.beta.toolboxes.create(
        name=toolbox_name,
        description="Example toolbox created by the azure-ai-projects sample.",
        metadata={"status": "created"},
        tools=tools,
    )
    status = created.metadata.get("status", "unknown status") if created.metadata else "unknown status"
    print(f"Toolbox: {created.name} (tools: {len(created.tools)}) (status: {status})")

    fetched = project_client.beta.toolboxes.get(toolbox_name)
    print(f"Retrieved toolbox: {fetched.name} ({fetched.id})")

    updated = project_client.beta.toolboxes.update(
        toolbox_name,
        description="Updated description for the sample toolbox.",
        metadata={"status": "updated"},
        tools=tools,
    )
    status = updated.metadata.get("status", "unknown status") if updated.metadata else "unknown status"
    print(f"Toolbox: {updated.name} (tools: {len(updated.tools)}) (status: {status})")

    toolboxes = list(project_client.beta.toolboxes.list(limit=10))
    print(f"Found {len(toolboxes)} toolboxes")
    for item in toolboxes:
        print(f"  - {item.name} ({item.id})")

    project_client.beta.toolboxes.delete(toolbox_name)
    print("Toolbox deleted")
