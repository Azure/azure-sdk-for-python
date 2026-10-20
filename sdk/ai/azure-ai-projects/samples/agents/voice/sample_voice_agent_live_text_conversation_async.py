# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Run a headless, asynchronous GPT Live text conversation using Responses
    delegation. Send multiple prompts sequentially over the same session,
    waiting for nested response.completed before beginning the next turn.
    Backend text is printed; it does not signal completion of frontend speech.

USAGE:
    python sample_voice_agent_live_text_conversation_async.py
    python sample_voice_agent_live_text_conversation_async.py "My name is Ada." "What is my name?"

    Omit prompts for the same single-turn example as the synchronous sample.

    pip install "azure-ai-projects[voice]" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required) - Your GPT Live DEPLOYMENT name.
    3) FOUNDRY_MODEL_NAME (required) - A Responses backend DEPLOYMENT name
       available to the Live resource, not a model catalog identifier.
    4) FOUNDRY_VOICE_AGENT_NAME (optional) - Prefix for a uniquely named sample
       agent. Only the version created by this run is deleted.

    Authenticates with DefaultAzureCredential. No microphone, speaker, or
    audio-device dependency is needed. Ctrl-C cancels local work and closes
    the session; Live has no response.cancel command.
"""

from __future__ import annotations

import argparse
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


async def main(prompts: Optional[Sequence[str]] = None) -> None:
    prompts = text_conversation_prompts(prompts)
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
                    instructions="You are a friendly voice assistant. Delegate text questions to the backend.",
                    audio=audio_settings(),
                    delegation=models.LiveResponsesDelegationParam(
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
    parser = argparse.ArgumentParser(description="Run a headless, asynchronous GPT Live text conversation.")
    parser.add_argument("prompts", nargs="*", help="Quoted text prompts to send sequentially in one session.")
    arguments = parser.parse_args()
    asyncio.run(main(arguments.prompts or None))
