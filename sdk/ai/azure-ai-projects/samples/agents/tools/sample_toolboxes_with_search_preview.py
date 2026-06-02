# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a Toolbox in tool-search mode and
    invoke it from a Prompt Agent using the synchronous AIProjectClient and
    the OpenAI-compatible client.

    A toolbox version that includes 'ToolboxSearchPreviewTool' exposes only
    two meta tools at its '/mcp' endpoint -- 'tool_search' and 'call_tool'
    -- and defers every other tool behind them. The agent uses an 'MCPTool'
    pointed at the toolbox's versioned '/mcp' URL to discover and invoke
    those inner tools.

    Toolboxes and tool search are preview features. CRUD goes through
    'project_client.beta.toolboxes'.

USAGE:
    python sample_toolboxes_with_search_preview.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv openai

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) MCP_PROJECT_CONNECTION_ID - The connection resource ID in Custom keys used by
       the inner MCP server inside the toolbox.
"""

import os

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MCPTool,
    PromptAgentDefinition,
    ToolboxSearchPreviewTool,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

TOOLBOX_NAME = "toolbox_with_mcp_tool"
INNER_MCP_LABEL = "github"
INNER_MCP_URL = "https://api.githubcopilot.com/mcp"
TOOLBOX_MCP_LABEL = "search-tool"


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    inner_mcp_tool = MCPTool(
        server_label=INNER_MCP_LABEL,
        server_url=INNER_MCP_URL,
        require_approval="never",
        project_connection_id=os.environ["MCP_PROJECT_CONNECTION_ID"],
    )

    toolbox_version = project_client.beta.toolboxes.create_version(
        name=TOOLBOX_NAME,
        description=f"Toolbox with `{INNER_MCP_LABEL}` MCP server and tool search enabled.",
        tools=[inner_mcp_tool, ToolboxSearchPreviewTool()],
    )
    print(f"Created toolbox `{TOOLBOX_NAME}` (version {toolbox_version.version}).")

    toolbox_mcp_url = f"{endpoint}/toolboxes/{TOOLBOX_NAME}/versions/{toolbox_version.version}/mcp?api-version=v1"
    token = credential.get_token("https://ai.azure.com/.default").token

    toolbox_mcp_tool = MCPTool(
        server_label=TOOLBOX_MCP_LABEL,
        server_url=toolbox_mcp_url,
        authorization=token,
        headers={"Foundry-Features": "Toolboxes=V1Preview"},
        require_approval="never",
    )

    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions=(
                "Always use the toolbox search tool to answer questions and perform tasks. "
                "Use `tool_search` to discover a relevant tool, then `call_tool` "
                "with the tool name returned by the search."
            ),
            tools=[toolbox_mcp_tool],
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version}).")

    response = openai_client.responses.create(
        input="What is my username in Github profile?",
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )

    for item in response.output:
        if item.type == "mcp_approval_request":
            print(f"server_label={item.server_label}, name={item.name}")
        elif item.type == "mcp_list_tools":
            print(f"server_label={item.server_label}, tools={[t.name for t in (item.tools or [])]}")
        elif item.type == "mcp_call":
            print(f"server_label={item.server_label}, name={item.name}, error={item.error}")
        else:
            print()

    print(f"Response: {response.output_text}")

    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print(f"Agent version {agent.version} deleted.")
