# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Ask a same-project prompt agent a spoken question through GPT-Live (preview).
    Send the bundled spoken question, print the reply transcript and audio size, and delete
    both temporary agent versions. No microphone or speakers are needed.

USAGE:
    python sample_voice_agent_live_managed_agent_async.py

    pip install "azure-ai-projects[voice]>=2.11.0" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required) - An existing GPT-Live deployment.
    3) FOUNDRY_MODEL_NAME (required) - A prompt-agent deployment in the same project.
    4) FOUNDRY_VOICE_AUDIO_INPUT_PATH (optional) - Override audio/question.wav
       with your own PCM16, mono, 24-kHz WAV of at most 30 seconds.
    5) FOUNDRY_VOICE_AGENT_NAME (optional) - Prefix for unique owned names.

    Uses DefaultAzureCredential. Foundry runs the backend; the client only
    streams audio. Reply audio is counted, not played or saved. Capture ends
    after three quiet seconds; a long pause can cut off a reply.
"""

from __future__ import annotations

import asyncio
from contextlib import AsyncExitStack
import os

from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects import models

from live_sample_utils import close_session_async, input_audio_path, sample_agent_name, wait_for_event_async
from managed_agent_sample_utils import (
    PROMPT_INSTRUCTIONS,
    check_managed_session,
    live_definition,
    print_reply,
    read_input_audio,
    stream_managed_audio_async,
)


async def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_VOICE_AGENT_MODEL"]
    backend_model = os.environ["FOUNDRY_MODEL_NAME"]
    pcm = read_input_audio(input_audio_path())
    backend_name = sample_agent_name("managed-backend")
    voice_name = sample_agent_name("managed-frontend")

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
        AsyncExitStack() as cleanup,
    ):
        backend = await project_client.agents.create_version(
            agent_name=backend_name,
            definition=models.PromptAgentDefinition(model=backend_model, instructions=PROMPT_INSTRUCTIONS),
        )
        cleanup.push_async_callback(
            project_client.agents.delete_version, agent_name=backend_name, agent_version=backend.version
        )
        voice = await project_client.agents.create_version(
            agent_name=voice_name, definition=live_definition(model, backend_name, backend.version)
        )
        cleanup.push_async_callback(
            project_client.agents.delete_version, agent_name=voice_name, agent_version=voice.version
        )

        async with project_client.beta.voice_agents.live.connect(
            agent_name=voice_name, agent_version=voice.version, store=False
        ) as connection:
            try:
                started = await wait_for_event_async(connection, "session.started")
                if not isinstance(started, models.LiveServerEventLiveSessionStarted):
                    raise RuntimeError("Expected a typed session.started event from the Live handshake.")
                check_managed_session(started.session, backend_name, backend.version)
                output = await stream_managed_audio_async(connection, pcm)
            finally:
                await close_session_async(connection)
        print_reply(output, len(pcm))
    print("Deleted only the Live and prompt-agent versions created by this run.")


if __name__ == "__main__":
    asyncio.run(main())
