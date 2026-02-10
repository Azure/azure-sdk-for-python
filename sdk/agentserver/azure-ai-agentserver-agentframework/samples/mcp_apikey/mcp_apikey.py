# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

from agent_framework import MCPStreamableHTTPTool
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from azure.ai.agentserver.agentframework import from_agent_framework

MCP_TOOL_NAME = "github"  # Expected tool name exposed by the GitHub MCP server
MCP_TOOL_URL = "https://api.githubcopilot.com/mcp/"  # Base MCP server endpoint

load_dotenv()


async def main() -> None:
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise RuntimeError(
            "GITHUB_TOKEN environment variable not set. Provide a GitHub token with MCP access."
        )

    agent = AzureOpenAIChatClient(credential=DefaultAzureCredential()).create_agent(
        instructions="You are a helpful assistant that answers GitHub questions. Use only the exposed MCP tools.",
        tools=MCPStreamableHTTPTool(
            name=MCP_TOOL_NAME,
            url=MCP_TOOL_URL,
            headers={
                "Authorization": f"Bearer {github_token}",
            },
        ),
    )

    async with agent:
        await from_agent_framework(agent).run_async()


if __name__ == "__main__":
    asyncio.run(main())
