# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from collections.abc import Callable, Generator

import httpx
from typing import Any, cast
from agent_framework import Agent, SkillsProvider
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer  # type: ignore[import-untyped]
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

MCPSkillsSource = cast(Any, __import__("agent_framework", fromlist=["MCPSkillsSource"]).MCPSkillsSource)

load_dotenv()


class ToolboxAuth(httpx.Auth):
    """Attach a fresh Foundry bearer token to every request."""

    requires_response_body = True

    def __init__(self, token_provider: Callable[[], str]) -> None:
        self._token_provider = token_provider

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self._token_provider()}"
        yield request


async def main() -> None:
    project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    deployment = os.environ["FOUNDRY_MODEL_NAME"]
    toolbox_mcp_url = os.environ["MCP_SERVER_URL"]
    store_responses = os.environ.get("AGENT_STORE_RESPONSES", "false").lower() == "true"

    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")

    async with (
        httpx.AsyncClient(
            auth=ToolboxAuth(token_provider),
            headers={"Foundry-Features": "Routines=V1Preview"},
            timeout=httpx.Timeout(30.0, read=300.0),
            follow_redirects=True,
        ) as http_client,
        streamable_http_client(
            url=toolbox_mcp_url,
            http_client=http_client,
        ) as (read, write, _),
        ClientSession(read, write) as session,
    ):
        await session.initialize()

        skills_provider = SkillsProvider(MCPSkillsSource(client=session))

        agent = Agent(
            client=FoundryChatClient(
                project_endpoint=project_endpoint,
                model=deployment,
                credential=credential,
            ),
            name=os.environ.get("AGENT_NAME", "TOOLBOX_AGENT"),
            instructions=os.environ.get(
                "AGENT_INSTRUCTIONS",
            ),
            context_providers=[skills_provider],
            default_options={"store": store_responses},
        )

        server = ResponsesHostServer(agent)
        await server.run_async()


if __name__ == "__main__":
    asyncio.run(main())
