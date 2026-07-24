# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_and_manage_voice_agent_async.py

DESCRIPTION:
    This sample demonstrates the voice-agent management lifecycle using the async
    client: creating a voice agent, retrieving it, listing the agents in the
    project, and deleting it.

USAGE:
    python sample_create_and_manage_voice_agent_async.py

    Set the environment variable before running the sample:
    1) AZURE_VOICE_AGENTS_ENDPOINT - the Foundry project endpoint, in the form
       https://<account>.services.ai.azure.com/api/projects/<project>

    Optional:
    2) AZURE_VOICE_AGENTS_MODEL - the realtime model deployment to use.
       Defaults to "gpt-realtime".

    The sample authenticates with DefaultAzureCredential, so sign in first
    (for example, with `az login`). An async HTTP transport such as aiohttp must
    be installed (`pip install aiohttp`).
"""

import asyncio
import os
from typing import Final

from azure.identity.aio import DefaultAzureCredential

from azure.ai.voiceagents.aio import VoiceAgentsClient
from azure.ai.voiceagents.models import AgentDefinitionOptInKeys, VoiceAgentDefinition


async def create_and_manage_voice_agent() -> None:
    endpoint = os.environ["AZURE_VOICE_AGENTS_ENDPOINT"]
    model = os.environ.get("AZURE_VOICE_AGENTS_MODEL", "gpt-realtime")
    agent_name = "sample-voice-agent-async"
    preview: Final = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

    credential = DefaultAzureCredential()
    async with credential, VoiceAgentsClient(endpoint=endpoint, credential=credential) as client:
        created = await client.voice_agents.create_voice_agent(
            name=agent_name,
            definition=VoiceAgentDefinition(
                model_type="managed",
                model=model,
                instructions="You are a friendly voice assistant. Keep replies short and natural.",
                # Persist conversations so they can be read back later. Defaults to False.
                store=True,
            ),
            description="Created by the azure-ai-voiceagents async sample.",
            foundry_features=preview,
        )
        print(f"Created voice agent: {created.name}")

        agent = await client.voice_agents.get_voice_agent(agent_name, foundry_features=preview)
        print(f"Retrieved voice agent: {agent.name}")

        print("Voice agents in this project:")
        async for item in client.voice_agents.list_voice_agents(foundry_features=preview):
            print(f"  - {item.name}")

        await client.voice_agents.delete_voice_agent(agent_name, foundry_features=preview)
        print(f"Deleted voice agent: {agent_name}")


if __name__ == "__main__":
    asyncio.run(create_and_manage_voice_agent())
