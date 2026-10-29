# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Read a GPT Live conversation, list its items, and download its audio using
    project_client.beta.voice_agents.live_conversations.

    With no conversation ID, the sample creates a short greeting session and
    deletes its conversation and temporary agent version afterward. No microphone,
    input WAV, or Responses model is needed. Supplying an existing ID skips
    creation and leaves the existing agent and conversation untouched.

    WAV downloads remain in a unique user-temporary folder. The sample prints
    its path; remove the folder when finished. Files contain conversation
    content, not telemetry. BYOS audio requires your own storage credentials
    and is not downloaded.

USAGE:
    python sample_voice_agent_live_read_conversation.py

    pip install "azure-ai-projects[voice]" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required when creating a conversation) -
       Your GPT Live deployment name.
    3) FOUNDRY_VOICE_CONVERSATION_ID (optional) - An existing conversation ID.
       Unset or blank means create a conversation for this run.
    4) FOUNDRY_VOICE_AGENT_NAME - Required with an existing ID; otherwise an
       optional prefix for the temporary agent name.

    Uses DefaultAzureCredential. An existing conversation needs no model
    deployment or WebSocket. Use session.started.conversation_id, not session.id,
    from a completed speech session with store=True. The service must support
    Live REST routes; HTTP errors are raised without a Realtime fallback.
"""

from __future__ import annotations

import base64
from contextlib import contextmanager, ExitStack
from itertools import islice
import os
from pathlib import Path
import struct
from tempfile import mkdtemp
import time
from typing import Iterator

from dotenv import load_dotenv
from live_sample_utils import (
    audio_settings,
    check_event,
    check_session_open,
    close_session,
    recording_output,
    remaining_time,
    safe_print,
    sample_agent_name,
    wait_for_event,
)

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient, models
from azure.ai.projects.operations import BetaLiveConnection, BetaVoiceAgentsLiveConversationsOperations


_SESSION_TIMEOUT = 45.0
_FINALIZATION_TIMEOUT = 90.0


def _receive_greeting(connection: BetaLiveConnection) -> None:
    deadline = time.monotonic() + _SESSION_TIMEOUT
    next_input = time.monotonic()
    last_content = next_input
    speech_received = False
    input_bytes = output_bytes = 0
    while True:
        remaining = remaining_time(deadline, "the sample greeting audio")
        now = time.monotonic()
        if speech_received and now - last_content >= 2:
            print(f"Greeting audio: sent {input_bytes} silence bytes; received {output_bytes} PCM16 bytes.")
            return
        if now >= next_input:
            connection.session.input_audio.append(audio=bytes(2400))
            input_bytes += 2400
            next_input = now + 0.05
        try:
            event = connection.recv(timeout=min(remaining, max(0.001, next_input - time.monotonic())))
        except TimeoutError:
            continue
        check_event(event)
        check_session_open(event)
        if isinstance(event, models.LiveOutputAudioDelta):
            pcm = base64.b64decode(event.delta, validate=True)
            if len(pcm) % 2:
                raise ValueError("The service returned an incomplete PCM16 sample.")
            output_bytes += len(pcm)
            if any(abs(sample) > 256 for (sample,) in struct.iter_unpack("<h", pcm)):
                speech_received = True
                last_content = time.monotonic()
        elif isinstance(event, models.LiveServerEventLiveOutputTranscriptDelta) and event.delta.strip():
            safe_print(f"Greeting transcript: {event.delta}")
            last_content = time.monotonic()


def _wait_for_recording(
    conversations: BetaVoiceAgentsLiveConversationsOperations, agent_name: str, conversation_id: str
) -> None:
    print("Waiting for the sample conversation and audio to finish persisting.")
    deadline = time.monotonic() + _FINALIZATION_TIMEOUT
    while True:
        remaining_time(deadline, "stored conversation finalization")
        try:
            conversation = conversations.get(agent_name, conversation_id)
        except ResourceNotFoundError:
            pass
        else:
            if conversation.id != conversation_id:
                raise RuntimeError("The service returned a different stored conversation ID.")
            if conversation.status == "failed":
                raise RuntimeError(f"Sample conversation persistence failed: {conversation.last_error}")
            if conversation.status == "completed":
                try:
                    conversations.get_audio(agent_name, conversation_id)
                except HttpResponseError as exc:
                    if exc.status_code != 409 or getattr(exc.error, "code", None) != "recording_not_ready":
                        raise
                else:
                    items = conversations.list_items(agent_name, conversation_id, limit=20, order="asc")
                    if any(
                        isinstance(item, models.VoiceAgentLiveOutputConversationItem) and item.audio is not None
                        for item in islice(items, 20)
                    ):
                        return
            elif conversation.status != "in_progress":
                raise RuntimeError(f"Unexpected sample conversation status: {conversation.status}")
        time.sleep(min(1.0, remaining_time(deadline, "stored conversation finalization")))


@contextmanager
def _temporary_conversation(project_client: AIProjectClient, model: str) -> Iterator[tuple[str, str]]:
    agent_name = sample_agent_name("rest")
    conversations = project_client.beta.voice_agents.live_conversations
    with ExitStack() as cleanup:
        agent = project_client.agents.create_version(
            agent_name=agent_name,
            definition=models.VoiceAgentLiveDefinition(
                model=model,
                instructions="Greet the caller briefly.",
                greeting=models.VoiceAgentTemplateGreetingConfig(text="Hello, welcome."),
                audio=audio_settings(),
                delegation=models.LiveClientDelegationParam(),
                store=True,
            ),
        )
        cleanup.callback(project_client.agents.delete_version, agent_name=agent_name, agent_version=agent.version)
        with project_client.beta.voice_agents.live.connect(
            agent_name=agent_name, agent_version=agent.version, store=True
        ) as connection:
            try:
                started = wait_for_event(connection, "session.started")
                stored_id = started.get("conversation_id")
                if not isinstance(stored_id, str) or not stored_id.strip() or stored_id == started["session"]["id"]:
                    raise RuntimeError("The stored session did not return a valid stored conversation ID.")
                conversation_id = stored_id
                cleanup.callback(conversations.delete, agent_name, conversation_id)
                print(f"Created conversation: {conversation_id}")
                _receive_greeting(connection)
            finally:
                close_session(connection)
        _wait_for_recording(conversations, agent_name, conversation_id)
        yield agent_name, conversation_id
    print(f"Deleted sample conversation: {conversation_id} and temporary agent version: {agent.version}")


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


def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME", "").strip()
    conversation_id = os.environ.get("FOUNDRY_VOICE_CONVERSATION_ID", "").strip()
    model = ""
    if conversation_id:
        if not agent_name:
            raise ValueError("Provide a nonblank existing agent name with the stored Foundry conversation ID.")
    else:
        model = os.environ["FOUNDRY_VOICE_AGENT_MODEL"].strip()
        if not model:
            raise ValueError("Provide a nonblank GPT Live deployment name to create the sample conversation.")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        try:
            if conversation_id:
                _read_conversation(project_client.beta.voice_agents.live_conversations, agent_name, conversation_id)
                print(
                    "Read-only REST run: the existing agent, conversation, items, and stored audio were not modified."
                )
            else:
                with _temporary_conversation(project_client, model) as (created_agent, created_conversation):
                    _read_conversation(
                        project_client.beta.voice_agents.live_conversations, created_agent, created_conversation
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
