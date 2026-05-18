# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on Toolboxes
    using the synchronous AIProjectClient.

    It creates two toolbox versions with MCP tools configured with different
    `require_approval` values, switches the default version, and prints the
    MCP `require_approval` setting from the fetched default version.

    Toolboxes are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.toolboxes`.

USAGE:
    python sample_toolboxes_crud.py

    Before running the sample:

    pip install "azure-ai-projects>=2.1.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
"""

import logging
import os
import sys

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPTool, Tool

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]


def print_mcp_require_approval(tools: list[Tool]) -> None:
    for tool in tools:
        if isinstance(tool, MCPTool):
            print(f"  - MCP `{tool.server_label}` require_approval: {tool.require_approval}")


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, logging_enable=True) as project_client,
):

    toolbox_name = "toolbox_with_mcp_tool"

    try:
        project_client.beta.toolboxes.delete(toolbox_name)
        print(f"Toolbox `{toolbox_name}` deleted")
    except ResourceNotFoundError:
        pass

    tools_with_mcp_approval_required: list[Tool] = [
        MCPTool(
            server_label="api_specs",
            server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
            require_approval="never",
        )
    ]

    tools_with_mcp_approval_always: list[Tool] = [
        MCPTool(
            server_label="api_specs",
            server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
            require_approval="always",
        )
    ]

    created = project_client.beta.toolboxes.create_version(
        name=toolbox_name,
        description="Toolbox version with MCP require_approval set to 'never'.",
        tools=tools_with_mcp_approval_required,
    )
    print(f"Created toolbox: {created.name} with MCP tools requiring approval 'never' in version {created.version}")

    created = project_client.beta.toolboxes.create_version(
        name=toolbox_name,
        description="Toolbox version with MCP require_approval set to 'always'.",
        tools=tools_with_mcp_approval_always,
    )
    print(f"Created toolbox: {created.name} with MCP tools requiring approval 'always' in version {created.version}")

    updated = project_client.beta.toolboxes.update(
        toolbox_name,
        default_version="2",
    )
    print(f"Updated toolbox: {updated.name} default version is now {updated.default_version}")

    fetched = project_client.beta.toolboxes.get(name=toolbox_name)
    print(f"Retrieved toolbox with default version: {fetched.default_version}")
    fetched_version = project_client.beta.toolboxes.get_version(
        name=toolbox_name,
        version=fetched.default_version,
    )
    print_mcp_require_approval(fetched_version.tools)

    updated = project_client.beta.toolboxes.update(
        toolbox_name,
        default_version="1",
    )
    print(f"Updated toolbox: {updated.name} default version is now {updated.default_version}")

    fetched = project_client.beta.toolboxes.get(name=toolbox_name)
    print(f"Retrieved toolbox with default version: {fetched.default_version}")
    fetched_version = project_client.beta.toolboxes.get_version(
        name=toolbox_name,
        version=fetched.default_version,
    )
    print_mcp_require_approval(fetched_version.tools)

    toolboxes = list(project_client.beta.toolboxes.list())
    print(f"Found {len(toolboxes)} toolboxes")
    for item in toolboxes:
        print(f"  - {item.name} ({item.id})")

    project_client.beta.toolboxes.delete(name=toolbox_name)
    print("Toolbox deleted")
