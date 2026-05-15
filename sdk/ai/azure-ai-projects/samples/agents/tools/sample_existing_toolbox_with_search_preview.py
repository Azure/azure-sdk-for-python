# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample is the ``azure-ai-projects`` equivalent of using
    ``langchain_azure_ai.tools.AzureAIProjectToolbox`` + LangGraph's
    ``create_react_agent``: it points at an *existing* Foundry toolbox by
    name and version and asks the agent what tools are available.

    A toolbox version that includes ``ToolboxSearchPreviewTool`` exposes only
    two meta tools at its ``/mcp`` endpoint -- ``tool_search`` and
    ``call_tool``. The Foundry Prompt Agent uses an ``MCPTool`` pointed at
    that endpoint to discover and invoke every other tool in the toolbox.

USAGE:
    python sample_existing_toolbox_with_search_preview.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv openai

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the
       Overview page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under
       the "Name" column in the "Models + endpoints" tab.
    3) FOUNDRY_TOOLBOX_NAME - The name of an existing toolbox (created with
       ``project_client.beta.toolboxes.create_version`` and including
       ``ToolboxSearchPreviewTool``).
    4) FOUNDRY_TOOLBOX_VERSION - The toolbox version to target (e.g. ``"1"``).
"""

import os

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPTool, PromptAgentDefinition

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment = os.environ["FOUNDRY_MODEL_NAME"]
toolbox_name = os.environ["FOUNDRY_TOOLBOX_NAME"]
toolbox_version = os.environ["FOUNDRY_TOOLBOX_VERSION"]

TOOLBOX_MCP_LABEL = "search-tool"


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # The toolbox's /mcp endpoint requires an Entra bearer token (scope
    # ``https://ai.azure.com/.default``) plus the experimental preview
    # opt-in header ``Foundry-Features: Toolboxes=V1Preview``.
    toolbox_mcp_url = f"{endpoint}/toolboxes/{toolbox_name}/versions/{toolbox_version}/mcp?api-version=v1"
    token = credential.get_token("https://ai.azure.com/.default").token

    toolbox_mcp_tool = MCPTool(
        server_label=TOOLBOX_MCP_LABEL,
        server_url=toolbox_mcp_url,
        authorization=token,
        headers={"Foundry-Features": "Toolboxes=V1Preview"},
        require_approval="never",
    )

    agent = project_client.agents.create_version(
        agent_name="MyToolboxAgent",
        definition=PromptAgentDefinition(
            model=model_deployment,
            instructions=(
                "You can search and call tools inside a Foundry toolbox via MCP. "
                "Use `tool_search` to discover relevant tools, then `call_tool` "
                "with the tool name returned by the search."
            ),
            tools=[toolbox_mcp_tool],
        ),
    )
    print(f"Agent created (name: {agent.name}, version: {agent.version}).")

    response = openai_client.responses.create(
        input="What tools are available?",
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )

    for item in response.output:
        if item.type == "mcp_list_tools":
            print(f"mcp_list_tools server_label={item.server_label}, tools={[t.name for t in (item.tools or [])]}")
        elif item.type == "mcp_call":
            print(f"mcp_call server_label={item.server_label}, name={item.name}, error={item.error}")
        elif item.type == "mcp_approval_request":
            print(f"mcp_approval_request server_label={item.server_label}, name={item.name}")

    print(f"Response: {response.output_text}")

    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print(f"Agent version {agent.version} deleted.")
