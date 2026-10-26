# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Send one or more text messages through one preview GPT Live session configured
    with a Responses delegation. Each turn waits for nested response.completed
    before sending the next prompt, retaining the conversation in that session.
    This is not the Realtime protocol's response.done.

USAGE:
    python sample_voice_agent_live_text_conversation.py

    Leave TEXT_PROMPTS as None for the single-turn example. To demonstrate
    a headless multi-turn conversation, set TEXT_PROMPTS in this file to
    ["My name is Ada.", "What is my name?"] before running it.

    pip install "azure-ai-projects[voice]" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required) - Your GPT Live DEPLOYMENT name.
    3) FOUNDRY_MODEL_NAME (required) - A Responses backend DEPLOYMENT name
       available to the Live resource, not a model catalog identifier.
    4) FOUNDRY_VOICE_AGENT_NAME (optional) - Prefix for a uniquely named sample
       agent. Only the version created by this run is deleted.

    Authenticates with DefaultAzureCredential. No microphone or speaker needed.
    This sample prints the backend text; use the audio sample for Live speech.
"""

from __future__ import annotations

import os
from typing import Optional, Sequence

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient, models

from live_sample_utils import (
    audio_settings,
    close_session,
    receive_response,
    safe_print,
    sample_agent_name,
    text_conversation_prompts,
    wait_for_event,
)


TEXT_PROMPTS: Optional[Sequence[str]] = None


def _run_text_conversation(
    project_client: AIProjectClient, agent_name: str, agent_version: str, prompts: Sequence[str]
) -> None:
    with project_client.beta.voice_agents.live.connect(
        agent_name=agent_name, agent_version=agent_version, store=False
    ) as connection:
        try:
            wait_for_event(connection, "session.started")
            for prompt in prompts:
                safe_print(f"You: {prompt}")
                connection.response.item.create(
                    item={"type": "message", "role": "user", "content": [{"type": "input_text", "text": prompt}]}
                )
                connection.response.create()
                text, calls = receive_response(connection)
                if calls:
                    raise RuntimeError("The text-only backend unexpectedly requested a function tool.")
                if not text:
                    raise RuntimeError("The Responses backend completed without returning any output text.")
                safe_print(f"Responses backend: {text}")
        finally:
            close_session(connection)


def main() -> None:
    prompts = text_conversation_prompts(TEXT_PROMPTS)
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_VOICE_AGENT_MODEL"]
    backend_model = os.environ["FOUNDRY_MODEL_NAME"]
    agent_name = sample_agent_name("text")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        created_version = None
        try:
            created_version = project_client.agents.create_version(
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
            _run_text_conversation(project_client, agent_name, created_version.version, prompts)
        finally:
            if created_version is not None:
                project_client.agents.delete_version(agent_name=agent_name, agent_version=created_version.version)
                print(f"Deleted sample agent version: {created_version.version}")


if __name__ == "__main__":
    main()
