# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Read a stored GPT Live conversation using the asynchronous preview
    project_client.beta.voice_agents.live_conversations REST APIs. Retrieve the
    conversation, recent conversations, ordered items, individual items, and
    merged/per-item audio metadata. No agent or WebSocket session is created.

    Requires an ended speech session with effective store=True. Use
    session.started.conversation_id, not session.id. These dedicated Live REST
    routes must be available on the service deployment; HTTP 404 is reported
    and raised, never replaced by calls to the older Realtime conversation API.

    By default, no audio files are written and nothing is deleted. Pass
    --output-dir to download Foundry-managed WAV recordings without overwriting
    existing files. BYOS recordings must be downloaded with your own storage
    credentials. Pass --delete only for a conversation you intend to remove:
    deletion also removes its stored items and audio. A read/download failure
    prevents deletion.

USAGE:
    python sample_voice_agent_live_read_conversation_async.py
    python sample_voice_agent_live_read_conversation_async.py --output-dir live-recordings
    python sample_voice_agent_live_read_conversation_async.py --delete

    pip install azure-ai-projects azure-identity python-dotenv aiohttp

    Environment variables (all required):
    1) FOUNDRY_PROJECT_ENDPOINT - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_NAME - The existing GPT Live agent name.
    3) FOUNDRY_VOICE_CONVERSATION_ID - The stored Foundry conversation ID.

    Authenticates with DefaultAzureCredential. No model deployment name,
    microphone, or WebSocket dependency is needed.
"""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from live_sample_utils import recording_output, safe_print

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects import models
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.aio.operations import BetaVoiceAgentsLiveConversationsOperations


async def _read_item(
    conversations: BetaVoiceAgentsLiveConversationsOperations,
    agent_name: str,
    conversation_id: str,
    item_id: str,
    index: int,
    output_directory: Optional[Path],
) -> None:
    detail = await conversations.get_item(agent_name, conversation_id, item_id)
    print(f"Item {detail.id}: type={detail.type}")
    if not isinstance(
        detail, (models.VoiceAgentLiveInputConversationItem, models.VoiceAgentLiveOutputConversationItem)
    ):
        print("  Non-speech item; there is no speech audio to download.")
        return
    safe_print(f"  Transcript: {detail.transcription or '(not captured)'}")
    if detail.audio is None:
        print("  No captured audio metadata for this speech item.")
        return
    audio = await conversations.get_audio_item(agent_name, conversation_id, item_id)
    print(f"  Audio: role={audio.role}, sample_rate={audio.sample_rate}, duration={audio.duration_ms}")
    if audio.blob_uri:
        print("  BYOS item: download from your storage using your own credentials.")
        if output_directory is not None:
            raise RuntimeError("This sample downloads Foundry-managed audio only, not BYOS audio.")
    elif output_directory is not None:
        with recording_output(output_directory / f"item-{index:04d}.wav") as output:
            stream = await conversations.download_audio_item(agent_name, conversation_id, item_id)
            async for chunk in stream:
                output.write(chunk)


async def _read_conversation(
    conversations: BetaVoiceAgentsLiveConversationsOperations,
    agent_name: str,
    conversation_id: str,
    *,
    output_directory: Optional[Path],
    delete: bool,
) -> None:
    conversation = await conversations.get(agent_name, conversation_id)
    if conversation.status != "completed":
        raise RuntimeError(
            f"The stored session must finish successfully before reading its recording; "
            f"status={conversation.status}, error={conversation.last_error}"
        )
    print(f"Conversation {conversation.id}: status={conversation.status}, created_at={conversation.created_at}")

    print("Recent stored Live conversations (up to five):")
    count = 0
    async for recent in conversations.list(agent_name, limit=5, order="desc"):
        print(f"  {recent.id}: status={recent.status}")
        count += 1
        if count == 5:
            break

    if output_directory is not None:
        output_directory.mkdir(parents=True, exist_ok=True)

    seen_items: set[str] = set()
    index = 0
    async for item in conversations.list_items(agent_name, conversation_id, limit=20, order="asc"):
        index += 1
        if item.id in seen_items:
            raise RuntimeError("The conversation pager repeated an item instead of advancing.")
        seen_items.add(item.id)
        await _read_item(conversations, agent_name, conversation_id, item.id, index, output_directory)

    recording = await conversations.get_audio(agent_name, conversation_id)
    print(
        f"Merged recording: format={recording.format}, sample_rate={recording.sample_rate}, "
        f"channels={recording.channels}, duration={recording.duration_ms}"
    )
    if recording.blob_uri:
        print("BYOS recording: download from your storage using your own credentials.")
        if output_directory is not None:
            raise RuntimeError("This sample downloads Foundry-managed audio only, not BYOS audio.")
    elif output_directory is not None:
        with recording_output(output_directory / "conversation.wav") as output:
            stream = await conversations.download_audio(agent_name, conversation_id)
            async for chunk in stream:
                output.write(chunk)

    if delete:
        await conversations.delete(agent_name, conversation_id)
        try:
            await conversations.get(agent_name, conversation_id)
        except ResourceNotFoundError:
            print(f"Deleted conversation {conversation_id}; confirmed HTTP 404.")
        else:
            raise RuntimeError("The conversation remains readable after deletion.")
    else:
        print("Read-only run: the conversation, items, and audio were not deleted.")


async def main(*, output_directory: Optional[Path] = None, delete: bool = False) -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ["FOUNDRY_VOICE_AGENT_NAME"]
    conversation_id = os.environ["FOUNDRY_VOICE_CONVERSATION_ID"]
    if not agent_name.strip() or not conversation_id.strip():
        raise ValueError("Provide a nonblank existing agent name and stored Foundry conversation ID.")

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        try:
            await _read_conversation(
                project_client.beta.voice_agents.live_conversations,
                agent_name,
                conversation_id,
                output_directory=output_directory,
                delete=delete,
            )
        except HttpResponseError as exc:
            print(f"GPT Live conversation REST request failed: HTTP {exc.status_code}.")
            if exc.status_code == 404:
                print(
                    "Confirm the stored conversation ID and store=True, and that this deployment supports "
                    "/protocols/voice/live/conversations. No older-route fallback is used."
                )
            elif exc.status_code == 409:
                print("Recording finalization may still be pending or unavailable; inspect the service error code.")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read a stored GPT Live conversation through the dedicated REST API.")
    parser.add_argument(
        "--output-dir", type=Path, help="Explicitly save audio to this directory; files are not overwritten."
    )
    parser.add_argument("--delete", action="store_true", help="Delete the selected conversation, its items, and audio.")
    options = parser.parse_args()
    asyncio.run(main(output_directory=options.output_dir, delete=options.delete))
