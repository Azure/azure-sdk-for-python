"""
DESCRIPTION:
    Triage sub-agent for the SDK Dev Agent. The triage agent
    answers questions about the live engineering state of the SDKs: open or
    recently merged PRs, open issues by label or keyword, and matching an
    error message against existing issues. It uses the GitHub MCP server
    for `Azure/azure-sdk-for-python`, `Azure/azure-sdk-for-js`, and
    `Azure/azure-sdk-for-net`.

"""

import os
from typing import Any

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPTool, PromptAgentDefinition


def triage_agent(project: AIProjectClient) -> Any:
    """Create the Triage sub-agent version in Foundry and return the Agent."""
    return project.agents.create_version(
        agent_name="sdk-triage-agent",
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions=(
                "You are the SDK Triage Agent. You answer questions about the live "
                "engineering state of the azure-ai-projects and azure-ai-agents SDKs in "
                "Azure/azure-sdk-for-python, azure-sdk-for-js, and azure-sdk-for-net.\n"
                "\n"
                "Use the github tools to find open or recently merged PRs touching a "
                "package, open issues (by label, area, or error keyword), what's actively "
                "being worked on, and to diagnose an error the user is hitting by "
                "searching existing issues. Default to Azure/azure-sdk-for-python; switch "
                "to the JS or .NET repo when the question says so.\n"
                "\n"
                "Always return concrete results, not generalities. List each PR or issue "
                "with its number, title, state, and URL, and end with a one-sentence "
                "read on what the activity means. If a search returns nothing, say so "
                "explicitly. Never invent PR or issue numbers."
            ),
            tools=[
                MCPTool(
                    server_label="github",
                    server_url="https://api.githubcopilot.com/mcp/",
                    require_approval="never",
                    project_connection_id=os.environ["GITHUB_MCP_CONNECTION_ID"],
                ),
            ],
        ),
    )
