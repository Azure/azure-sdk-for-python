# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a Toolbox in tool-search mode and
    invoke it from a Prompt Agent using the asynchronous AIProjectClient and
    the OpenAI-compatible client.

    A toolbox version that includes 'ToolboxSearchPreviewTool' exposes only
    two meta tools at its '/mcp' endpoint -- 'tool_search' and 'call_tool'
    -- and defers every other tool behind them. The agent uses an 'MCPTool'
    pointed at the toolbox's versioned '/mcp' URL to discover and invoke
    those inner tools.

    Toolboxes and tool search are preview features. CRUD goes through
    'project_client.toolboxes'.

USAGE:
    python sample_toolboxes_with_search_preview_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv openai aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
    4) MCP_PROJECT_CONNECTION_ID - The connection resource ID in Custom keys used by
       the inner MCP server inside the toolbox.
"""

import asyncio
import os
from dotenv import load_dotenv
from util import create_version_with_endpoint_async
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    MCPTool,
    MCPToolboxTool,
    ToolboxSearchPreviewToolboxTool,
    PromptAgentDefinition,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

TOOLBOX_NAME = "toolbox_with_mcp_tool"
INNER_MCP_LABEL = "github"
INNER_MCP_URL = "https://api.githubcopilot.com/mcp"
TOOLBOX_MCP_LABEL = "search-tool"
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client(agent_name=agent_name) as openai_client,
    ):

        inner_mcp_tool = MCPToolboxTool(
            server_label=INNER_MCP_LABEL,
            server_url=INNER_MCP_URL,
            require_approval="never",
            project_connection_id=os.environ["MCP_PROJECT_CONNECTION_ID"],
        )

        toolbox_version = await project_client.toolboxes.create_version(
            name=TOOLBOX_NAME,
            description=f"Toolbox with `{INNER_MCP_LABEL}` MCP server and tool search enabled.",
            tools=[inner_mcp_tool, ToolboxSearchPreviewToolboxTool()],
        )
        print(f"Created toolbox `{TOOLBOX_NAME}` (version {toolbox_version.version}).")

        toolbox_mcp_url = f"{endpoint}/toolboxes/{TOOLBOX_NAME}/versions/{toolbox_version.version}/mcp?api-version=v1"
        token = (await credential.get_token("https://ai.azure.com/.default")).token

        toolbox_mcp_tool = MCPTool(
            server_label=TOOLBOX_MCP_LABEL,
            server_url=toolbox_mcp_url,
            authorization=token,
            require_approval="never",
        )

        async with create_version_with_endpoint_async(
            project_client=project_client,
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=os.environ["FOUNDRY_MODEL_NAME"],
                instructions=(
                    "Always use the toolbox search tool to answer questions and perform tasks. "
                    "Use `tool_search` to discover a relevant tool, then `call_tool` "
                    "with the tool name returned by the search."
                ),
                tools=[toolbox_mcp_tool],
            ),
        ) as agent:
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version}).")

            response = await openai_client.responses.create(
                input="What is my username in Github profile?",
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


if __name__ == "__main__":
    asyncio.run(main())
