# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer  # type: ignore[import-untyped]
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    deployment = os.environ["FOUNDRY_MODEL_NAME"]
    store_responses = os.environ.get("AGENT_STORE_RESPONSES", "false").lower() == "true"

    with DefaultAzureCredential() as credential:
        agent = Agent(
            client=FoundryChatClient(
                project_endpoint=project_endpoint,
                model=deployment,
                credential=credential,
                allow_preview=True,
            ),
            name=os.environ.get("AGENT_NAME", "BASIC_AGENT"),
            instructions=os.environ.get(
                "AGENT_INSTRUCTIONS",
            ),
            default_options={"store": store_responses},
        )

        server = ResponsesHostServer(agent)
        await server.run_async()


if __name__ == "__main__":
    asyncio.run(main())
