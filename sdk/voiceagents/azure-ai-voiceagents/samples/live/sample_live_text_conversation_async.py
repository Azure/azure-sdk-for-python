# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: sample_live_text_conversation_async.py

DESCRIPTION:
    End-to-end typed voice-agent conversation using only the azure-ai-voiceagents
    SDK (REST management + realtime streaming):

      1. Create an agent with ``store = true`` so conversations persist.
      2. Publish a new version.
      3. Open a realtime session and hold a typed, multi-turn conversation: each
         prompt you type is sent to the agent and its spoken reply streams back
         as audio plus a transcript. Blank line (or ``exit`` / ``quit``) ends it.
         Runs headless -- no microphone needed.
      4. Read the persisted conversation back.
      5. Delete the agent.

    Reply audio is base64 PCM16, mono, 24 kHz, played through the speakers when
    ``pyaudio`` is installed. For a hands-free mic conversation with barge-in,
    see sample_live_audio_conversation_async.py.

      pip install azure-ai-voiceagents aiohttp azure-identity pyaudio

USAGE:
    python sample_live_text_conversation_async.py

    Environment variables:
    1) AZURE_VOICE_AGENTS_ENDPOINT (required) - Foundry project endpoint:
       https://<account>.services.ai.azure.com/api/projects/<project>
    2) AZURE_VOICE_AGENTS_MODEL (optional) - realtime deployment. Default "gpt-realtime".

    Authenticates with DefaultAzureCredential, so sign in first (e.g. `az login`).
"""

import asyncio
import base64
import os
from typing import Final, Optional

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

PREVIEW: Final = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

# Timeout (seconds) to wait for the agent to finish its spoken reply.
_RESPONSE_TIMEOUT: Final = 45

# The agent streams its reply as PCM16, mono, 24 kHz audio.
_SAMPLE_RATE: Final = 24000

try:
    import pyaudio
except ImportError:  # pragma: no cover - optional playback dependency
    pyaudio = None  # type: ignore[assignment]


class _SpeakerPlayer:
    """Play streamed PCM16 audio deltas through the speakers with pyaudio.

    Playback is optional: when pyaudio is not installed the player is a no-op and
    the sample still runs headless, reporting the amount of audio it received.
    """

    def __init__(self) -> None:
        self._audio = None
        self._stream = None
        self._bytes = 0
        if pyaudio is not None:
            self._audio = pyaudio.PyAudio()
            self._stream = self._audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=_SAMPLE_RATE,
                output=True,
            )

    @property
    def enabled(self) -> bool:
        return self._stream is not None

    def play(self, pcm: bytes) -> None:
        """Write one decoded PCM16 chunk to the speaker (if playback is enabled)."""
        self._bytes += len(pcm)
        if self._stream is not None:
            self._stream.write(pcm)

    def close(self) -> None:
        """Drain and release the audio device."""
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        if self._audio is not None:
            self._audio.terminate()
            self._audio = None

    @property
    def seconds(self) -> float:
        """Total audio received, in seconds (PCM16 = 2 bytes/sample)."""
        return self._bytes / 2 / _SAMPLE_RATE


async def _run_text_conversation(
    client: VoiceAgentsClient,
    agent_name: str,
) -> Optional[str]:
    """Hold a typed, multi-turn conversation and return the persisted conversation id."""
    conversation_id: Optional[str] = None
    audio_delta_count = 0
    player = _SpeakerPlayer()

    try:
        async with client.realtime.connect(
            agent_name=agent_name,
            foundry_features=PREVIEW,
        ) as conn:
            print("Type a message and press Enter. Blank line (or 'exit') ends the session.")

            async def pump() -> None:
                nonlocal conversation_id, audio_delta_count
                async for event in conn:
                    event_type = event.get("type")
                    if event_type == "conversation.created":
                        # Only ``conversation.created`` carries the persisted id;
                        # the id on ``response.done`` is a per-turn runtime id.
                        conversation_id = event.get("conversation_id") or conversation_id
                        print(f"(conversation.created -> persisted id: {conversation_id})")
                    elif event_type in ("response.output_audio.delta", "response.audio.delta"):
                        # Each delta is a base64 PCM16 chunk of the reply; play it.
                        audio_delta_count += 1
                        player.play(base64.b64decode(event.get("delta", "")))
                    elif event_type in (
                        "response.output_audio_transcript.done",
                        "response.audio_transcript.done",
                    ):
                        print(f"Agent: {event.get('transcript', '')}")
                    elif event_type == "response.done":
                        return
                    elif event_type == "error":
                        error = event.get("error") or {}
                        print(f"Session error: {error.get('message', error)}")
                        return

            while True:
                # input() blocks, so read it off the loop in a worker thread.
                prompt = (await asyncio.to_thread(input, "You:   ")).strip()
                if not prompt or prompt.lower() in ("exit", "quit"):
                    break

                # Send the user turn and ask the agent to respond.
                await conn.conversation.item.create(
                    item={
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}],
                    }
                )
                await conn.response.create()

                try:
                    await asyncio.wait_for(pump(), timeout=_RESPONSE_TIMEOUT)
                except asyncio.TimeoutError:
                    print("Timed out waiting for the agent's reply.")
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n(ending session...)")
    finally:
        played = player.enabled
        player.close()

    detail = "played" if played else "received"
    print(f"(streamed {audio_delta_count} audio chunks, {detail} {player.seconds:.2f}s of audio)")
    if not played:
        print("(install pyaudio to hear the reply: pip install pyaudio)")
    return conversation_id


async def _read_conversation(client: VoiceAgentsClient, agent_name: str, conversation_id: str) -> None:
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
        role = item.get("role") or item.get("type")
        # Audio turns expose ``transcript``; text turns expose ``text``.
        parts = [
            (part.get("transcript") or part.get("text") or "").strip()
            for part in (item.get("content") or [])
        ]
        transcript = " ".join(p for p in parts if p)
        print(f"  - {role} id={item.get('id')}")
        if transcript:
            print(f"      {transcript}")


async def text_conversation() -> None:
    project_endpoint = os.environ["AZURE_VOICE_AGENTS_ENDPOINT"]
    model = os.environ.get("AZURE_VOICE_AGENTS_MODEL", "gpt-realtime")
    agent_name = "sample-text-agent"

    credential = DefaultAzureCredential()
    # Foundry may return Brotli responses (Content-Encoding: br) that aiohttp
    # won't decode; ask only for gzip/deflate so the transport handles it.
    transport = AioHttpTransport(
        session=aiohttp.ClientSession(auto_decompress=False, headers={"Accept-Encoding": "gzip, deflate"})
    )

    async with credential, VoiceAgentsClient(
        endpoint=project_endpoint, credential=credential, transport=transport
    ) as client:
        conversation_id: Optional[str] = None
        try:
            # 1) Create the agent. `store = true` persists conversations for later reading.
            await client.voice_agents.create_voice_agent(
                name=agent_name,
                definition=VoiceAgentDefinition(
                    model_type="managed",
                    model=model,
                    instructions="You are a friendly voice assistant. Keep replies short.",
                    output_modalities=[VoiceOutputModality.TEXT, VoiceOutputModality.AUDIO],
                    store=True,
                ),
                description="Created by the azure-ai-voiceagents text conversation sample.",
                foundry_features=PREVIEW,
            )
            print(f"Created voice agent: {agent_name}")

            # 2) Publish a new version with refined instructions.
            new_version = await client.voice_agents.create_voice_agent_version(
                agent_name,
                definition=VoiceAgentDefinition(
                    model_type="managed",
                    model=model,
                    instructions="You are a helpful voice assistant. Give concise, clear answers.",
                    output_modalities=[VoiceOutputModality.TEXT, VoiceOutputModality.AUDIO],
                    store=True,
                ),
                description="Refined instructions.",
                foundry_features=PREVIEW,
            )
            print(f"Published agent version: {new_version.version}")

            # 3) Hold a realtime streaming conversation with the agent via typed turns.
            print("Starting realtime session...")
            conversation_id = await _run_text_conversation(client, agent_name)

            # 4) Read the persisted conversation back with the voice-agents client.
            if conversation_id:
                print(f"Reading persisted conversation {conversation_id}...")
                try:
                    await _read_conversation(client, agent_name, conversation_id)
                except HttpResponseError as e:
                    print(f"Could not read conversation: {e.status_code} {e.reason}")
            else:
                print("No conversation id was returned; nothing to read.")
        except HttpResponseError as e:
            print(f"Service responded with an error: {e.status_code} {e.reason}")
        finally:
            # 5) Clean up: delete the agent.
            try:
                await client.voice_agents.delete_voice_agent(agent_name, foundry_features=PREVIEW)
                print(f"Deleted voice agent: {agent_name}")
            except HttpResponseError as e:
                print(f"Could not delete agent: {e.status_code} {e.reason}")


if __name__ == "__main__":
    try:
        asyncio.run(text_conversation())
    except KeyboardInterrupt:
        print("\nInterrupted.")
