# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on Toolsets
    using the synchronous AIProjectClient.

    Toolsets are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.toolsets`.

USAGE:
    python sample_toolsets_crud.py

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

    toolset_name = "mcp"

    try:
        project_client.beta.toolsets.delete(toolset_name)
        print(f"Toolset `{toolset_name}` deleted")
    except ResourceNotFoundError:
        pass

    tools: list[Tool] = [
        MCPTool(
            server_label="api_specs",
            server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
            require_approval="never",
        )
    ]

    toolset = project_client.beta.toolsets.create(
        name=toolset_name,
        description="Example toolset created by the azure-ai-projects sample.",
        metadata={"sample": "true"},
        tools=tools,
    )
    print(f"Created toolset: {toolset.name} ({toolset.id})")

    fetched = project_client.beta.toolsets.get(toolset_name)
    print(f"Retrieved toolset: {fetched.name} ({fetched.id})")

    updated = project_client.beta.toolsets.update(
        toolset_name,
        description="Updated description for the sample toolset.",
        metadata={"sample": "true", "updated": "true"},
        tools=tools,
    )
    print(f"Updated toolset: {updated.name} (tools: {len(updated.tools)})")

    toolsets = list(project_client.beta.toolsets.list(limit=10))
    print(f"Found {len(toolsets)} toolsets")
    for item in toolsets:
        print(f"  - {item.name} ({item.id})")

    deleted = project_client.beta.toolsets.delete(toolset_name)
    print(f"Deleted toolset: {deleted.deleted}")
