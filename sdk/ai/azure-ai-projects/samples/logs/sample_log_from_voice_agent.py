# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Save Realtime voice-agent diagnostics to a temporary log file using
    azure.ai.projects.realtime. Logs contain connection events, event types,
    and byte counts, not message content or credentials. OpenTelemetry is
    not required.

    The sample sends one text prompt and deletes the agent version it creates.
    No microphone or speaker is needed.

USAGE:
    python samples/logs/sample_log_from_voice_agent.py

    pip install "azure-ai-projects[voice]" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL - Optional managed model; defaults to "gpt-realtime".
    3) FOUNDRY_VOICE_AGENT_NAME - Optional agent name; defaults to a unique sample name.

    Authenticates with DefaultAzureCredential. The sample prints the log file path
    and restores the logger's configuration when it finishes.
"""

import logging
import os
import time
import uuid

from dotenv import load_dotenv
from log_utils import create_timestamped_temp_log_file
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    RealtimeConversationItemMessageUser,
    RealtimeConversationItemMessageUserContent,
    RealtimeConversationItemType,
    RealtimeServerEventError,
    RealtimeServerEventResponseDone,
    VoiceAgentAudioConfig,
    VoiceAgentAudioOutputConfig,
    VoiceAgentDefinition,
    VoiceModelType,
    VoiceOutputModality,
    VoiceType,
)

load_dotenv()


def _run_conversation(project_client: AIProjectClient, agent_name: str) -> None:
    """Send one text prompt and wait for completion.

    :param project_client: The Foundry project client.
    :type project_client: ~azure.ai.projects.AIProjectClient
    :param agent_name: The sample's voice agent name.
    :type agent_name: str
    """
    with project_client.beta.voice_agents.realtime.connect(agent_name=agent_name) as connection:
        connection.conversation.item.create(
            item=RealtimeConversationItemMessageUser(
                type=RealtimeConversationItemType.MESSAGE,
                content=[RealtimeConversationItemMessageUserContent(type="input_text", text="What is two plus three?")],
            )
        )
        connection.response.create()
        deadline = time.monotonic() + 60
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("The voice response did not finish within 60 seconds.")
            event = connection.recv(timeout=remaining)
            if isinstance(event, RealtimeServerEventError):
                raise RuntimeError("The realtime service returned an error. Inspect its error event.")
            if isinstance(event, RealtimeServerEventResponseDone):
                if event.response.status != "completed":
                    raise RuntimeError("The voice response did not complete successfully.")
                break


def main() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ.get("FOUNDRY_VOICE_AGENT_MODEL") or "gpt-realtime"
    agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or f"sample-voice-agent-logs-{uuid.uuid4().hex[:8]}"
    log_file = create_timestamped_temp_log_file(__file__)
    file_handler = logging.FileHandler(filename=log_file, encoding="utf-8")
    logger = logging.getLogger("azure.ai.projects.realtime")
    previous_level = logger.level
    previous_propagate = logger.propagate
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(file_handler)

    try:
        with (
            DefaultAzureCredential() as credential,
            AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
        ):
            created_version = None
            try:
                created_version = project_client.agents.create_version(
                    agent_name=agent_name,
                    definition=VoiceAgentDefinition(
                        model_type=VoiceModelType.MANAGED,
                        model=model,
                        instructions="You are a helpful assistant. Keep replies short.",
                        audio=VoiceAgentAudioConfig(
                            output=VoiceAgentAudioOutputConfig(
                                voice="en-US-AvaNeural", voice_type=VoiceType.AZURE_STANDARD
                            )
                        ),
                        output_modalities=[VoiceOutputModality.TEXT],
                        store=False,
                    ),
                )
                _run_conversation(project_client, agent_name)
            finally:
                if created_version is not None:
                    project_client.agents.delete_version(agent_name=agent_name, agent_version=created_version.version)
    finally:
        logger.removeHandler(file_handler)
        file_handler.close()
        logger.setLevel(previous_level)
        logger.propagate = previous_propagate

    print(f"Voice Agent realtime logs written to {log_file}")


if __name__ == "__main__":
    main()
