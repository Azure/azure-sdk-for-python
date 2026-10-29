# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Send text messages through GPT Live and print the replies from a Responses
    backend model. Multiple messages share one session. The sample waits for
    response.completed before sending the next message and deletes its temporary
    agent version when finished.

USAGE:
    python sample_voice_agent_live_text_conversation.py

    Leave TEXT_PROMPTS as None for one message, or set it to a list such as
    ["My name is Ada.", "What is my name?"] for a multi-turn conversation.

    pip install "azure-ai-projects[voice]" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required) - Your GPT Live deployment name.
    3) FOUNDRY_MODEL_NAME (required) - A Responses model deployment available
       to your Live resource. It handles the delegated text requests.
    4) FOUNDRY_VOICE_AGENT_NAME (optional) - Prefix for the temporary agent name.

    Uses DefaultAzureCredential. No microphone or speaker is needed.
    Printed text does not signal that voice playback has finished.
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
