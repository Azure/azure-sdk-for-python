# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    Cancel a Realtime reply and confirm that its audio item was truncated.
    No audio is played, so the sample reports zero heard milliseconds.
    It deletes its own conversation and agent version afterward.

USAGE:
    python sample_voice_agent_realtime_interruption_async.py
    pip install "azure-ai-projects[voice]>=2.11.0" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required) - A managed Realtime model deployment.
    3) FOUNDRY_VOICE_AGENT_NAME (optional) - Prefix for the temporary agent.

    Uses DefaultAzureCredential; no audio devices are needed. A real player
    must report its actual playback position, not zero.
"""

import asyncio
import os
from uuid import uuid4

from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.core.exceptions import ResourceNotFoundError

from realtime_interruption_utils import (
    InterruptedTurn,
    interrupt_reply_async,
    interruption_definition,
)


async def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_VOICE_AGENT_MODEL"]
    prefix = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or "sample-realtime-interruption"
    agent_name = f"{prefix}-{uuid4().hex[:8]}"
    turn = InterruptedTurn()

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as client,
    ):
        created = None
        try:
            created = await client.agents.create_version(
                agent_name=agent_name, definition=interruption_definition(model)
            )
            async with client.voice_agents.realtime.connect(agent_name=agent_name) as connection:
                await interrupt_reply_async(connection, turn)
            print(
                f"Confirmed response cancellation and item truncation. Received {turn.received_audio_bytes} PCM bytes."
            )
        finally:
            try:
                if turn.conversation_id:
                    try:
                        await client.voice_agents.conversations.delete(agent_name, turn.conversation_id)
                    except ResourceNotFoundError:
                        print("Conversation cleanup returned 404; no persisted conversation was found.")
            finally:
                if created is not None:
                    await client.agents.delete_version(agent_name=agent_name, agent_version=created.version)


if __name__ == "__main__":
    asyncio.run(main())
