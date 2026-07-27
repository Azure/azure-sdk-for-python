# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: sample_live_conversation_async.py

DESCRIPTION:
    End-to-end sample that ties the voice-agent management APIs together with a
    live session driven by the azure-ai-voicelive SDK:

      1. Create a voice agent (with ``store = true`` so its conversations persist).
      2. Publish a new version of the agent.
      3. Open a live session against the agent with azure-ai-voicelive, exchange a
         couple of turns, and capture the conversation id the service creates.
      4. Read the persisted conversation back with the voice-agents client.
      5. Delete the conversation and the agent.

    The live session is driven over text so the sample needs no microphone or
    speaker. A real voice client would stream audio instead, but the management,
    read, and cleanup steps are identical.

    This sample uses two packages:
      pip install azure-ai-voiceagents azure-ai-voicelive aiohttp azure-identity

USAGE:
    python sample_live_conversation_async.py

    Set the environment variable before running the sample:
    1) AZURE_VOICE_AGENTS_ENDPOINT - the Foundry project endpoint, in the form
       https://<account>.services.ai.azure.com/api/projects/<project>

    Optional:
    2) AZURE_VOICE_AGENTS_MODEL - the realtime model deployment to use.
       Defaults to "gpt-realtime".

    The sample authenticates with DefaultAzureCredential, so sign in first
    (for example, with `az login`).
"""

import asyncio
import os
from typing import Final, List, Optional, Tuple
from urllib.parse import urlparse

import aiohttp
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import AioHttpTransport
from azure.identity.aio import DefaultAzureCredential

from azure.ai.voiceagents.aio import VoiceAgentsClient
from azure.ai.voiceagents.models import (
    AgentDefinitionOptInKeys,
    VoiceAgentDefinition,
    VoiceOutputModality,
)

from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    ClientEventConversationItemCreate,
    ClientEventResponseCreate,
    RequestTextContentPart,
    ServerEventType,
    UserMessageItem,
)

PREVIEW: Final = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW


def _account_endpoint_and_project(project_endpoint: str) -> Tuple[str, str]:
    """Split a Foundry project endpoint into ``(account endpoint, project name)``.

    VoiceLive connects to the account endpoint and takes the project name as a
    separate argument, while the voice-agents client uses the full project
    endpoint. Both are derived from the same URL.
    """
    parsed = urlparse(project_endpoint)
    account_endpoint = f"{parsed.scheme}://{parsed.netloc}"
    project_name = parsed.path.rstrip("/").rsplit("/", 1)[-1]
    return account_endpoint, project_name


async def _run_live_session(
    *,
    account_endpoint: str,
    project_name: str,
    agent_name: str,
    agent_version: Optional[str],
    credential: DefaultAzureCredential,
) -> Optional[str]:
    """Open a VoiceLive session against the agent, exchange a few text turns, and
    return the id of the conversation the service created for the session."""
    prompts = [
        "Hi! Can you help me plan a birthday party?",
        "Great - suggest three party themes for a six year old.",
    ]
    conversation_id: Optional[str] = None

    async with connect(
        credential=credential,
        endpoint=account_endpoint,
        project_name=project_name,
        agent_name=agent_name,
        agent_version=agent_version,
    ) as connection:
        for prompt in prompts:
            print(f"You:   {prompt}")

            # Add a user message to the conversation, then ask for a response.
            await connection.send(
                ClientEventConversationItemCreate(
                    item=UserMessageItem(content=[RequestTextContentPart(text=prompt)])
                )
            )
            await connection.send(ClientEventResponseCreate())

            # Read server events until this response completes.
            reply: List[str] = []
            while True:
                event = await connection.recv()
                if event.type == ServerEventType.RESPONSE_TEXT_DELTA:
                    reply.append(event.delta)
                elif event.type == ServerEventType.RESPONSE_DONE:
                    # The conversation id is stable across turns; capture it once.
                    conversation_id = event.response.conversation_id or conversation_id
                    break
                elif event.type == ServerEventType.ERROR:
                    print(f"Session error: {event.error.message}")
                    return conversation_id

            print(f"Agent: {''.join(reply)}")

    return conversation_id


async def _read_conversation(
    client: VoiceAgentsClient, agent_name: str, conversation_id: str
) -> None:
    """Read the persisted conversation back over the read-only conversation API."""
    conversations = client.agent_endpoint_conversations

    conversation = await conversations.get_agent_conversation(
        agent_name, conversation_id, foundry_features=PREVIEW
    )
    print(f"Conversation {conversation.id}: status={conversation.status}, created_at={conversation.created_at}")

    print("Items (transcript):")
    async for item in conversations.list_agent_conversation_items(
        agent_name, conversation_id, foundry_features=PREVIEW
    ):
        print(f"  - {item.get('type')} id={item.get('id')}")


async def end_to_end_conversation() -> None:
    project_endpoint = os.environ["AZURE_VOICE_AGENTS_ENDPOINT"]
    model = os.environ.get("AZURE_VOICE_AGENTS_MODEL", "gpt-realtime")
    account_endpoint, project_name = _account_endpoint_and_project(project_endpoint)
    agent_name = "sample-end-to-end-agent"

    credential = DefaultAzureCredential()
    # The Foundry endpoint can return Brotli-compressed responses (Content-Encoding: br),
    # which azure-core's aiohttp transport does not decode. Ask only for gzip/deflate so
    # the transport can decompress the response itself.
    transport = AioHttpTransport(
        session=aiohttp.ClientSession(auto_decompress=False, headers={"Accept-Encoding": "gzip, deflate"})
    )

    async with credential, VoiceAgentsClient(
        endpoint=project_endpoint, credential=credential, transport=transport
    ) as client:
        conversation_id: Optional[str] = None
        try:
            # 1) Create the agent. `store = true` persists conversations for later reading,
            #    and a text output modality lets us drive the session without audio hardware.
            await client.voice_agents.create_voice_agent(
                name=agent_name,
                definition=VoiceAgentDefinition(
                    model_type="managed",
                    model=model,
                    instructions="You are a friendly party-planning assistant. Keep replies short.",
                    output_modalities=[VoiceOutputModality.TEXT],
                    store=True,
                ),
                description="Created by the azure-ai-voiceagents end-to-end sample.",
                foundry_features=PREVIEW,
            )
            print(f"Created voice agent: {agent_name}")

            # 2) Publish a new version with refined instructions.
            new_version = await client.voice_agents.create_voice_agent_version(
                agent_name,
                definition=VoiceAgentDefinition(
                    model_type="managed",
                    model=model,
                    instructions="You are an enthusiastic party planner. Offer concrete, kid-friendly ideas.",
                    output_modalities=[VoiceOutputModality.TEXT],
                    store=True,
                ),
                description="Refined instructions.",
                foundry_features=PREVIEW,
            )
            print(f"Published agent version: {new_version.version}")

            # 3) Hold a live conversation with the agent through the VoiceLive SDK.
            print("Starting live session...")
            conversation_id = await _run_live_session(
                account_endpoint=account_endpoint,
                project_name=project_name,
                agent_name=agent_name,
                agent_version=new_version.version,
                credential=credential,
            )

            # 4) Read the persisted conversation back with the voice-agents client.
            if conversation_id:
                print(f"Reading persisted conversation {conversation_id}...")
                await _read_conversation(client, agent_name, conversation_id)
            else:
                print("No conversation id was returned; nothing to read.")
        except HttpResponseError as e:
            print(f"Service responded with an error: {e.status_code} {e.reason}")
        finally:
            # 5) Clean up: delete the conversation, then the agent.
            if conversation_id:
                try:
                    await client.agent_endpoint_conversations.delete_agent_conversation(
                        agent_name, conversation_id, foundry_features=PREVIEW
                    )
                    print(f"Deleted conversation: {conversation_id}")
                except HttpResponseError as e:
                    print(f"Could not delete conversation: {e.status_code} {e.reason}")
            try:
                await client.voice_agents.delete_voice_agent(agent_name, foundry_features=PREVIEW)
                print(f"Deleted voice agent: {agent_name}")
            except HttpResponseError as e:
                print(f"Could not delete agent: {e.status_code} {e.reason}")


if __name__ == "__main__":
    asyncio.run(end_to_end_conversation())
