# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Send text through GPT Live and print the Responses backend's reply.
    Set TEXT_PROMPTS to a list for multiple turns in one session.
    The sample deletes its temporary agent version when finished.

USAGE:
    python sample_voice_agent_live_text_conversation_async.py

    pip install "azure-ai-projects[voice]>=2.11.0" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required) - Your GPT Live deployment name.
    3) FOUNDRY_MODEL_NAME (required) - A Responses deployment available to Live.
    4) FOUNDRY_VOICE_AGENT_NAME (optional) - Prefix for the temporary agent name.

    Uses DefaultAzureCredential. No audio devices are needed.
    Printed text does not mean voice playback has finished.
"""

from __future__ import annotations

import asyncio
import os
from typing import Optional, Sequence

from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects import models

from live_sample_utils import (
    audio_settings,
    close_session_async,
    receive_response_async,
    safe_print,
    sample_agent_name,
    text_conversation_prompts,
    wait_for_event_async,
)

TEXT_PROMPTS: Optional[Sequence[str]] = None


async def _run_text_conversation(
    project_client: AIProjectClient, agent_name: str, agent_version: str, prompts: Sequence[str]
) -> None:
    async with project_client.beta.voice_agents.live.connect(
        agent_name=agent_name, agent_version=agent_version, store=False
    ) as connection:
        try:
            await wait_for_event_async(connection, "session.started")
            for prompt in prompts:
                safe_print(f"You: {prompt}")
                await connection.response.item.create(
                    item={"type": "message", "role": "user", "content": [{"type": "input_text", "text": prompt}]}
                )
                await connection.response.create()
                text, calls = await receive_response_async(connection)
                if calls:
                    raise RuntimeError("The text-only backend unexpectedly requested a function tool.")
                if not text:
                    raise RuntimeError("The Responses backend completed without returning any output text.")
                safe_print(f"Responses backend: {text}")
        finally:
            await close_session_async(connection)


async def main() -> None:
    prompts = text_conversation_prompts(TEXT_PROMPTS)
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_VOICE_AGENT_MODEL"]
    backend_model = os.environ["FOUNDRY_MODEL_NAME"]
    agent_name = sample_agent_name("text")

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
                    instructions="You are a friendly voice assistant. Delegate text questions to the backend.",
                    audio=audio_settings(),
                    delegation=models.VoiceAgentLiveResponsesDelegation(
                        responses=models.LiveResponsesDelegationSettingsInputParam(
                            model=backend_model, instructions="Answer in one short sentence."
                        )
                    ),
                    store=False,
                ),
            )
            await _run_text_conversation(project_client, agent_name, created_version.version, prompts)
        finally:
            if created_version is not None:
                await project_client.agents.delete_version(agent_name=agent_name, agent_version=created_version.version)
                print(f"Deleted sample agent version: {created_version.version}")


if __name__ == "__main__":
    asyncio.run(main())
