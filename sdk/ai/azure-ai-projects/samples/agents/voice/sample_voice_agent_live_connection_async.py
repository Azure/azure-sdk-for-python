# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Create a temporary GPT Live agent, open a session, update its settings,
    add instructions, and close it. The sample deletes the agent version it
    creates. No user input or audio devices are needed. Silent audio frames
    advance the Live timeline while it acknowledges the appended instructions.

USAGE:
    python sample_voice_agent_live_connection_async.py

    pip install "azure-ai-projects[voice]>=2.11.0" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required) - Your GPT Live deployment name.
    3) FOUNDRY_VOICE_AGENT_NAME (optional) - Prefix for the temporary agent name.

    Uses DefaultAzureCredential. Foundry starts the session automatically;
    wait for session.started rather than sending session.start.
"""

import asyncio
import os

from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects import models

from live_sample_utils import (
    audio_settings,
    close_session_async,
    sample_agent_name,
    wait_for_event_async,
    wait_for_event_with_audio_clock_async,
)


async def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_VOICE_AGENT_MODEL"]
    agent_name = sample_agent_name("connection")

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        created_version = None
        try:
            created_version = await project_client.agents.create_version(
                agent_name=agent_name,
                definition=models.VoiceAgentLiveDefinition(
                    model=model,
                    model_type=models.VoiceModelType.SELF_DEPLOYED,
                    instructions="You are a concise, friendly voice assistant.",
                    audio=audio_settings(),
                    delegation=models.VoiceAgentLiveClientDelegation(),
                    store=False,
                ),
            )
            async with project_client.beta.voice_agents.live.connect(
                agent_name=agent_name, agent_version=created_version.version, store=False
            ) as connection:
                try:
                    started = await wait_for_event_async(connection, "session.started")
                    print(f"Live session started: {started['session']['id']}")
                    await connection.session.update(
                        session=models.LiveSessionUpdateParams(
                            delegation=models.LiveSessionUpdateParamsDelegationLiveClientDelegationParam()
                        )
                    )
                    await wait_for_event_async(connection, "session.updated")
                    await connection.session.instructions.append(
                        content="Keep responses brief. Do not invent external facts.", delegation_id=None
                    )
                    await wait_for_event_with_audio_clock_async(connection, "session.instructions.appended")
                    print("Confirmed session.updated and session.instructions.appended.")
                finally:
                    # session.close is a command; leaving the context closes the transport.
                    await close_session_async(connection)
        finally:
            if created_version is not None:
                await project_client.agents.delete_version(agent_name=agent_name, agent_version=created_version.version)
                print(f"Deleted sample agent version: {created_version.version}")


if __name__ == "__main__":
    asyncio.run(main())
