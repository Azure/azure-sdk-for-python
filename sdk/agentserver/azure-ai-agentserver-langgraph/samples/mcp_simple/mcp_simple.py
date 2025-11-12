# Copyright (c) Microsoft. All rights reserved.
"""Minimal LangGraph + MCP sample.

Loads an MCP server (Microsoft Learn) and exposes a LangGraph ReAct agent
 through the agents_adapter server.
"""

import asyncio
import os

from dotenv import load_dotenv
from importlib.metadata import version
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import AzureChatOpenAI

from azure.ai.agentserver.langgraph import from_langgraph

load_dotenv()


def create_agent(model, tools):
    # for different langgraph versions
    langgraph_version = version("langgraph")
    if langgraph_version < "1.0.0":
        from langgraph.prebuilt import create_react_agent

        return create_react_agent(model, tools)
    else:
        from langchain.agents import create_agent

        return create_agent(model, tools)


async def quickstart():
    """Build and return a LangGraph agent wired to an MCP client."""
    deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o")
    model = AzureChatOpenAI(model=deployment)
    client = MultiServerMCPClient(
        {
            "mslearn": {
                "url": "https://learn.microsoft.com/api/mcp",
                "transport": "streamable_http",
            }
        }
    )
    tools = await client.get_tools()
    return create_agent(model, tools)


async def main():  # pragma: no cover - sample entrypoint
    agent = await quickstart()
    await from_langgraph(agent).run_async()


if __name__ == "__main__":
    asyncio.run(main())
