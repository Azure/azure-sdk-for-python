# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Read a stored GPT Live conversation using the preview
    project_client.beta.voice_agents.live_conversations REST APIs. Retrieve the
    conversation, recent conversations, ordered items, individual items, and
    merged/per-item audio metadata. No agent or WebSocket session is created.

    Requires an ended speech session with effective store=True. Use
    session.started.conversation_id, not session.id. These dedicated Live REST
    routes must be available on the service deployment; HTTP 404 is reported
    and raised, never replaced by calls to the older Realtime conversation API.

    Download Foundry-managed WAV recordings into a unique folder in your user
    temporary directory and print its location. The files remain available
    after the sample exits and are not overwritten. Downloads contain stored
    conversation content; remove the local folder when it is no longer needed.
    BYOS recordings require your own storage credentials and are not downloaded.
    The existing agent, conversation, items, and stored audio are never deleted.

USAGE:
    python sample_voice_agent_live_read_conversation.py

    pip install azure-ai-projects azure-identity python-dotenv

    Environment variables (all required):
    1) FOUNDRY_PROJECT_ENDPOINT - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_NAME - The existing GPT Live agent name.
    3) FOUNDRY_VOICE_CONVERSATION_ID - The stored Foundry conversation ID.

    Authenticates with DefaultAzureCredential. No model deployment name,
    microphone, or WebSocket dependency is needed.
"""

from __future__ import annotations

from itertools import islice
import os
from pathlib import Path
from tempfile import mkdtemp

from dotenv import load_dotenv
from live_sample_utils import recording_output, safe_print

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient, models
from azure.ai.projects.operations import BetaVoiceAgentsLiveConversationsOperations


def _read_item(
    conversations: BetaVoiceAgentsLiveConversationsOperations,
    agent_name: str,
    conversation_id: str,
    item_id: str,
    index: int,
    output_directory: Path,
) -> None:
    detail = conversations.get_item(agent_name, conversation_id, item_id)
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
    audio = conversations.get_audio_item(agent_name, conversation_id, item_id)
    print(f"  Audio: role={audio.role}, sample_rate={audio.sample_rate}, duration={audio.duration_ms}")
    if audio.blob_uri:
        print("  BYOS item: download from your storage using your own credentials.")
        raise RuntimeError("This sample downloads Foundry-managed audio only, not BYOS audio.")
    with recording_output(output_directory / f"item-{index:04d}.wav") as output:
        for chunk in conversations.download_audio_item(agent_name, conversation_id, item_id):
            output.write(chunk)


def _read_conversation(
    conversations: BetaVoiceAgentsLiveConversationsOperations,
    agent_name: str,
    conversation_id: str,
) -> None:
    conversation = conversations.get(agent_name, conversation_id)
    if conversation.status != "completed":
        raise RuntimeError(
            f"The stored session must finish successfully before reading its recording; "
            f"status={conversation.status}, error={conversation.last_error}"
        )
    print(f"Conversation {conversation.id}: status={conversation.status}, created_at={conversation.created_at}")

    print("Recent stored Live conversations (up to five):")
    for recent in islice(conversations.list(agent_name, limit=5, order="desc"), 5):
        print(f"  {recent.id}: status={recent.status}")

    output_directory = Path(mkdtemp(prefix="voice-agent-live-"))
    print(f"Audio output directory: {output_directory}")

    seen_items: set[str] = set()
    for index, item in enumerate(conversations.list_items(agent_name, conversation_id, limit=20, order="asc"), 1):
        if item.id in seen_items:
            raise RuntimeError("The conversation pager repeated an item instead of advancing.")
        seen_items.add(item.id)
        _read_item(conversations, agent_name, conversation_id, item.id, index, output_directory)

    recording = conversations.get_audio(agent_name, conversation_id)
    print(
        f"Merged recording: format={recording.format}, sample_rate={recording.sample_rate}, "
        f"channels={recording.channels}, duration={recording.duration_ms}"
    )
    if recording.blob_uri:
        print("BYOS recording: download from your storage using your own credentials.")
        raise RuntimeError("This sample downloads Foundry-managed audio only, not BYOS audio.")
    with recording_output(output_directory / "conversation.wav") as output:
        for chunk in conversations.download_audio(agent_name, conversation_id):
            output.write(chunk)

    print("Read-only REST run: the existing agent, conversation, items, and stored audio were not modified.")


def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ["FOUNDRY_VOICE_AGENT_NAME"]
    conversation_id = os.environ["FOUNDRY_VOICE_CONVERSATION_ID"]
    if not agent_name.strip() or not conversation_id.strip():
        raise ValueError("Provide a nonblank existing agent name and stored Foundry conversation ID.")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        try:
            _read_conversation(
                project_client.beta.voice_agents.live_conversations,
                agent_name,
                conversation_id,
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
    main()
