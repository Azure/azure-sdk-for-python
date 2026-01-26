# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

from dotenv import load_dotenv
from importlib.metadata import version
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import AzureChatOpenAI

from azure.ai.agentserver.langgraph import from_langgraph

load_dotenv()  # Load .env with Azure + GitHub credentials


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{name}'. Please define it in your .env file."
        )
    return value


def create_agent(model, tools):
    # for different langgraph versions
    langgraph_version = version("langgraph")
    if langgraph_version < "1.0.0":
        from langgraph.prebuilt import create_react_agent

        return create_react_agent(model, tools)
    else:
        from langchain.agents import create_agent

        return create_agent(model, tools)


async def build_agent():
    deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o")
    model = AzureChatOpenAI(model=deployment)

    github_token = _get_required_env("GITHUB_TOKEN")

    client = MultiServerMCPClient(
        {
            "github": {
                "url": "https://api.githubcopilot.com/mcp/",
                "transport": "streamable_http",
                "headers": {"Authorization": f"Bearer {github_token}"},
            }
        }
    )

    tools = await client.get_tools()
    agent = create_agent(model, tools)
    return agent


async def _main():
    agent = await build_agent()
    await from_langgraph(agent).run_async()


if __name__ == "__main__":
    asyncio.run(_main())
