# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end typed conversation using the ``client.realtime`` namespace added
    on top of the generated azure-ai-projects client (see
    ``azure.ai.projects.aio.AsyncRealtime``).

      1. Generate a starter voice agent (see sample_voice_agent_generate.py),
         then publish a version with `store=True` so the conversation can be
         read back afterward.
      2. Hold a typed, multi-turn conversation: each prompt is sent as a
         ``RealtimeConversationItemMessageUser`` and the reply streams back as
         typed audio and transcript events. Blank line (or ``exit`` / ``quit``)
         ends it.
      3. Fetch the persisted conversation back by id.
      4. Delete the agent created for this sample.

    Reply audio is PCM16, mono, 24 kHz and plays through the speakers when
    ``pyaudio`` is installed; runs headless otherwise. For a hands-free mic
    conversation with barge-in, see sample_voice_agent_live_audio_conversation_async.py.

      pip install "azure-ai-projects>=2.0.0" azure-identity aiohttp pyaudio

USAGE:
    python sample_voice_agent_live_text_conversation_async.py

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - Foundry project endpoint:
       https://<account>.services.ai.azure.com/api/projects/<project>
    2) FOUNDRY_VOICE_AGENT_NAME - Optional. Name for the agent created by this
       sample. Defaults to "sample-live-text-conversation-agent-async".

    Authenticates with DefaultAzureCredential, so sign in first (e.g. `az login`).
"""

import asyncio
import os
from typing import Final, Optional

from dotenv import load_dotenv
from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    AgentKind,
    GenerateVoiceAgentRequest,
    VoiceAgentDefinition,
    RealtimeConversationItemMessageUser,
    RealtimeConversationItemMessageUserContent,
    RealtimeConversationItemType,
    RealtimeServerEventResponseAudioDelta,
    RealtimeServerEventResponseAudioTranscriptDone,
    RealtimeServerEventResponseDone,
    RealtimeServerEventSessionCreated,
    RealtimeServerEventError,
)

load_dotenv()

# Seconds to wait for the agent to finish its reply.
_RESPONSE_TIMEOUT: Final = 45

# Reply audio format: PCM16, mono, 24 kHz.
_SAMPLE_RATE: Final = 24000

try:
    import pyaudio  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional playback dependency
    pyaudio = None  # type: ignore[assignment]


class _SpeakerPlayer:
    """Play streamed PCM16 audio through the speakers with pyaudio.

    Optional: without pyaudio the player is a no-op and the sample still runs
    headless, reporting how much audio it received.
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
        """Write one decoded PCM16 chunk to the speaker.

        :param pcm: Decoded PCM16 audio bytes.
        :type pcm: bytes
        """
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
        """Total audio received, in seconds (PCM16 = 2 bytes/sample).

        :rtype: float
        """
        return self._bytes / 2 / _SAMPLE_RATE


async def _run_text_conversation(client: AIProjectClient, agent_name: str) -> Optional[str]:
    """Hold a typed, multi-turn conversation.

    :param client: The Foundry project client.
    :param agent_name: The existing voice agent name.
    :type client: ~azure.ai.projects.aio.AIProjectClient
    :type agent_name: str
    :return: The persisted conversation id, if one is created.
    :rtype: str or None
    """
    conversation_id: Optional[str] = None
    audio_delta_count = 0
    player = _SpeakerPlayer()

    try:
        # Open the realtime session on the voice agent's dedicated route.
        async with client.realtime.connect(agent_name=agent_name) as conn:
            print("Type a message and press Enter. Blank line (or 'exit') ends the session.")

            async def pump() -> None:
                nonlocal conversation_id, audio_delta_count
                async for event in conn:
                    if isinstance(event, RealtimeServerEventSessionCreated):
                        # The persisted conversation id (only present when conversation
                        # persistence is enabled) is set here, not on response.done.
                        conversation_id = event.conversation_id or conversation_id
                    if isinstance(event, RealtimeServerEventResponseDone):
                        return
                    if isinstance(event, RealtimeServerEventError):
                        print(f"Session error: {event.error.message}")
                        return
                    if isinstance(event, RealtimeServerEventResponseAudioDelta):
                        # Each delta is a decoded PCM16 chunk; play it.
                        audio_delta_count += 1
                        player.play(event.delta)
                    elif isinstance(event, RealtimeServerEventResponseAudioTranscriptDone):
                        print(f"Agent: {event.transcript}")

            while True:
                # input() blocks, so read it off the loop in a worker thread.
                prompt = (await asyncio.to_thread(input, "You:  ")).strip()
                if not prompt or prompt.lower() in ("exit", "quit"):
                    break

                # Send the turn and ask the agent to respond.
                await conn.conversation.item.create(
                    item=RealtimeConversationItemMessageUser(
                        type=RealtimeConversationItemType.MESSAGE,
                        content=[RealtimeConversationItemMessageUserContent(type="input_text", text=prompt)],
                    )
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


async def _read_conversation(client: AIProjectClient, agent_name: str, conversation_id: str) -> None:
    """Read the persisted conversation back over the read-only conversation API.

    :param client: The Foundry project client.
    :param agent_name: The voice agent name.
    :param conversation_id: The persisted conversation id.
    :type client: ~azure.ai.projects.aio.AIProjectClient
    :type agent_name: str
    :type conversation_id: str
    """
    conversations = client.beta.agent_endpoint_conversations

    conversation = await conversations.get_agent_conversation(agent_name, conversation_id)
    print(f"Conversation {conversation.id}: status={conversation.status}, created_at={conversation.created_at}")

    print("Items (transcript):")
    async for item in conversations.list_agent_conversation_items(agent_name, conversation_id):
        role = item.get("role") or item.get("type")
        # Audio turns expose ``transcript``; text turns expose ``text``.
        parts = [(part.get("transcript") or part.get("text") or "").strip() for part in (item.get("content") or [])]
        transcript = " ".join(p for p in parts if p)
        print(f"  - {role} id={item.get('id')}")
        if transcript:
            print(f"      {transcript}")


async def text_conversation() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or "sample-live-text-conversation-agent-async"

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        try:
            # 1) Generate a starter voice agent (see sample_voice_agent_generate.py).
            generated = await project_client.agents.generate_agent(
                GenerateVoiceAgentRequest(kind=AgentKind.VOICE, name=agent_name)
            )
            definition = generated.versions.latest.definition  # type: ignore[attr-defined]

            # 2) Publish a new version with conversation persistence enabled (`store=True`) so the
            #    session's conversation can be fetched back by id afterward.
            await project_client.agents.create_version(
                agent_name=agent_name,
                definition=VoiceAgentDefinition(
                    model_type=definition.model_type,  # type: ignore[attr-defined]
                    model=definition.model,  # type: ignore[attr-defined]
                    instructions=definition.instructions,  # type: ignore[attr-defined]
                    store=True,
                ),
            )

            # 3) Hold the realtime conversation against the freshly created agent.
            print(f"Starting realtime session with agent: {agent_name}")
            conversation_id = await _run_text_conversation(project_client, agent_name)

            # 4) Fetch the persisted conversation back by id.
            if conversation_id:
                print(f"Reading persisted conversation {conversation_id}...")
                try:
                    await _read_conversation(project_client, agent_name, conversation_id)
                except HttpResponseError as e:
                    print(f"Could not read conversation: {e.status_code} {e.reason}")
                # To fetch this session's audio afterward, use
                # `project_client.beta.agent_endpoint_conversations`:
                #   - get_agent_conversation_audio(agent_name, conversation_id) for the merged
                #     whole-call stereo recording's metadata, then
                #     get_agent_conversation_audio_content(agent_name, conversation_id) to stream
                #     the WAV bytes.
                #   - get_agent_conversation_item_audio(agent_name, conversation_id, item_id) for a
                #     single turn's audio metadata, then
                #     get_agent_conversation_item_audio_content(agent_name, conversation_id, item_id)
                #     to stream that turn's bytes.
                # See sample_voice_agent_read_conversation_audio.py for a full example.
            else:
                print("No conversation id was returned; nothing to read.")
        except HttpResponseError as e:
            print(f"Service responded with an error: {e.status_code} {e.reason}")
        finally:
            # 5) Clean up the agent created for this sample.
            await project_client.agents.delete(agent_name=agent_name)
            print(f"Deleted voice agent: {agent_name}")


if __name__ == "__main__":
    try:
        asyncio.run(text_conversation())
    except KeyboardInterrupt:
        print("\nInterrupted.")
