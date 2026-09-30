# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import FoundryToolbox, ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    credential = DefaultAzureCredential()

    toolbox = FoundryToolbox(url=os.environ["MCP_SERVER_URL"], credential=credential)

    # set disable_load_skill_approval to avoid approval required for loading skills
    skills_provider = toolbox.as_skills_provider(disable_load_skill_approval=True)

    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL_NAME"],
        credential=credential,
        allow_preview=True,
    )

    agent = Agent(
        client=client,
        tools=toolbox,
        context_providers=[skills_provider],
    )

    server = ResponsesHostServer(agent)
    await server.run_async()


if __name__ == "__main__":
    asyncio.run(main())
