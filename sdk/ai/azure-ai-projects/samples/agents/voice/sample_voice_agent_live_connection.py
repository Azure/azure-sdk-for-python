# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Open a preview GPT Live voice-agent session, update its client delegation,
    append instructions, and confirm graceful session shutdown. Foundry starts
    the session from the persisted agent definition; do not send session.start.
    This is a protocol/lifecycle example, not a text or microphone conversation.

USAGE:
    python sample_voice_agent_live_connection.py

    pip install "azure-ai-projects[voice]" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required) - Your GPT Live DEPLOYMENT name,
       not a model catalog identifier.
    3) FOUNDRY_VOICE_AGENT_NAME (optional) - Prefix for a uniquely named sample
       agent. Only the version created by this run is deleted.

    Authenticates with DefaultAzureCredential. No audio devices are needed.
"""

import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient, models

from live_sample_utils import audio_settings, close_session, sample_agent_name, wait_for_event


def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_VOICE_AGENT_MODEL"]
    agent_name = sample_agent_name("connection")

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
                    instructions="You are a concise, friendly voice assistant.",
                    audio=audio_settings(),
                    delegation=models.LiveClientDelegationParam(),
                    store=False,
                ),
            )
            with project_client.beta.voice_agents.live.connect(
                agent_name=agent_name, agent_version=created_version.version, store=False
            ) as connection:
                try:
                    started = wait_for_event(connection, "session.started")
                    print(f"Live session started: {started['session']['id']}")
                    connection.session.update(
                        session=models.LiveSessionUpdateParams(delegation=models.LiveClientDelegationParam())
                    )
                    wait_for_event(connection, "session.updated")
                    connection.session.instructions.append(
                        content="Keep responses brief. Do not invent external facts.", delegation_id=None
                    )
                    wait_for_event(connection, "session.instructions.appended")
                    print("Confirmed session.updated and session.instructions.appended.")
                finally:
                    # session.close is a command; leaving the context closes the transport.
                    close_session(connection)
        finally:
            if created_version is not None:
                project_client.agents.delete_version(agent_name=agent_name, agent_version=created_version.version)
                print(f"Deleted sample agent version: {created_version.version}")


if __name__ == "__main__":
    main()
