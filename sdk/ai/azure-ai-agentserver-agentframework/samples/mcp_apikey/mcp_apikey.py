# Copyright (c) Microsoft. All rights reserved.
from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from agent_framework import ChatAgent, MCPStreamableHTTPTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

from azure.ai.agentserver.agentframework import from_agent_framework

MCP_TOOL_NAME = "github"  # Expected tool name exposed by the GitHub MCP server
MCP_TOOL_URL = "https://api.githubcopilot.com/mcp/"  # Base MCP server endpoint

load_dotenv()  # Load .env with Azure + GitHub credentials


@asynccontextmanager
async def create_agent() -> AsyncIterator[ChatAgent]:
    """Async context manager yielding a configured ChatAgent instance."""

    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise RuntimeError(
            "GITHUB_TOKEN environment variable not set. Provide a GitHub token with MCP access."
        )

    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as chat_client:
            agent = chat_client.create_agent(
                name="DocsAgent",
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
                yield agent


async def main():
    async with create_agent() as agent:
        await from_agent_framework(agent).run_async()


if __name__ == "__main__":
    asyncio.run(main())
