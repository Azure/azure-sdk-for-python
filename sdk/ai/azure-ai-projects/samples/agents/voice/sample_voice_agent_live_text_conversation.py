# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end typed conversation using the ``client.beta.realtime`` namespace added
    on top of the generated azure-ai-projects client (see
    ``azure.ai.projects.operations.Realtime``).

      1. Create a voice agent with conversation persistence enabled
         (`store=True`) so the conversation can be read back afterward.
      2. Hold a typed, multi-turn conversation: each prompt is sent as a
         ``RealtimeConversationItemMessageUser`` and the reply streams back as
         typed audio and transcript events. Blank line (or ``exit`` / ``quit``)
         ends it.
      3. Fetch the persisted conversation back by id.
      4. Delete the agent created for this sample.

    Reply audio is PCM16, mono, 24 kHz and plays through the speakers when
    ``pyaudio`` is installed; runs headless otherwise. For a hands-free mic
    conversation with barge-in, see sample_voice_agent_live_audio_conversation_async.py
    (that sample needs concurrent send/receive so it stays async-only; see
    sample_voice_agent_live_text_conversation_async.py for the async version of
    this one).

      pip install "azure-ai-projects[voice]>=2.7.0" azure-identity pyaudio

USAGE:
    python sample_voice_agent_live_text_conversation.py

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - Foundry project endpoint:
       https://<account>.services.ai.azure.com/api/projects/<project>
    2) FOUNDRY_VOICE_MODEL - Optional. The realtime model deployment name.
       Defaults to "gpt-realtime".
    3) FOUNDRY_VOICE_AGENT_NAME - Optional. Name for the agent created by this
       sample. Defaults to "sample-live-text-conversation-agent".

    Authenticates with DefaultAzureCredential, so sign in first (e.g. `az login`).
"""

import os
import sys
import time
from typing import Final, Optional, TYPE_CHECKING

from dotenv import load_dotenv
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    RealtimeConversationItemMessageUser,
    RealtimeConversationItemMessageUserContent,
    RealtimeConversationItemType,
    RealtimeServerEventResponseAudioDelta,
    RealtimeServerEventResponseAudioTranscriptDone,
    RealtimeServerEventResponseCreated,
    RealtimeServerEventResponseDone,
    RealtimeServerEventSessionCreated,
    RealtimeServerEventError,
    VoiceAgentAudioConfig,
    VoiceAgentAudioOutputConfig,
    VoiceAgentDefinition,
    VoiceAgentTemplateGreetingConfig,
    VoiceModelType,
    VoiceOutputModality,
    VoiceType,
)

if TYPE_CHECKING:
    from azure.ai.projects.operations import RealtimeConnection


load_dotenv()


def _safe_print(text: str) -> None:
    """Print text that may contain characters the current console can't display.

    The agent's replies below are model-generated and can contain characters (curly
    quotes, em-dashes, etc.) outside some legacy, non-Unicode console encodings
    (for example when stdout is piped/redirected on Windows). Rather than crashing
    with UnicodeEncodeError, fall back to replacing just the unsupported characters;
    a real interactive UTF-8 console prints unaffected.
    """
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "ascii"
        print(text.encode(encoding, errors="replace").decode(encoding))


# Seconds to wait for the agent to finish its reply.
_RESPONSE_TIMEOUT: Final = 45

# Reply audio format: PCM16, mono, 24 kHz.
_SAMPLE_RATE: Final = 24000


def _format_size(num_bytes: int) -> str:
    """Format a byte count as a human-readable string.

    :param num_bytes: The size in bytes.
    :type num_bytes: int
    :return: A string like "12345 bytes (12.1 KB)" or "2097152 bytes (2.00 MB)".
    :rtype: str
    """
    if num_bytes < 1024:
        return f"{num_bytes} bytes"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes} bytes ({num_bytes / 1024:.1f} KB)"
    return f"{num_bytes} bytes ({num_bytes / (1024 * 1024):.2f} MB)"


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
    def bytes_received(self) -> int:
        """Total decoded PCM16 output-audio bytes received from the service.

        :rtype: int
        """
        return self._bytes

    @property
    def seconds(self) -> float:
        """Total audio received, in seconds (PCM16 = 2 bytes/sample).

        :rtype: float
        """
        return self._bytes / 2 / _SAMPLE_RATE


class _CancellationNotConfirmed(Exception):
    """Raised when a just-cancelled response's terminal event could not be confirmed within
    ``_RESPONSE_TIMEOUT``, leaving the stream in an unknown state."""


def _drain_cancelled_response(conn: "RealtimeConnection", response_id: Optional[str]) -> None:
    """Wait (bounded) for a just-cancelled response's terminal event, discarding it and any of
    its trailing content events, so the next turn's ``pump()`` doesn't mistake this stale
    completion for its own.

    :param conn: The open realtime connection.
    :param response_id: The id of the response that was just cancelled, if it was captured from
     that response's ``response.created`` event. If None, the first terminal event seen is
     accepted, since there is nothing more specific to correlate against.
    :type conn: ~azure.ai.projects.RealtimeConnection
    :type response_id: str or None
    :raises _CancellationNotConfirmed: If no matching terminal event arrives in time.
    """
    deadline = time.monotonic() + _RESPONSE_TIMEOUT
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise _CancellationNotConfirmed("Timed out waiting to confirm the cancelled response finished.")
        try:
            event = conn.recv(timeout=remaining)
        except TimeoutError as exc:
            raise _CancellationNotConfirmed("Timed out waiting to confirm the cancelled response finished.") from exc
        if isinstance(event, RealtimeServerEventResponseDone):
            if response_id is None or event.response.id == response_id:
                return
            # A stray completion for some other response id; keep draining.
        elif isinstance(event, RealtimeServerEventError):
            print(f"Session error while confirming cancellation: {event.error.message}")


def _run_text_conversation(  # pylint: disable=too-many-statements
    client: AIProjectClient, agent_name: str, has_greeting: bool
) -> Optional[str]:
    """Hold a typed, multi-turn conversation.

    :param client: The Foundry project client.
    :param agent_name: The existing voice agent name.
    :param has_greeting: Whether the agent has a configured greeting, which the service plays
     automatically as soon as the session opens (before any user turn). When True, that greeting
     is drained and displayed before the interactive loop starts.
    :type client: ~azure.ai.projects.AIProjectClient
    :type agent_name: str
    :type has_greeting: bool
    :return: The persisted conversation id, if one is created.
    :rtype: str or None
    """
    conversation_id: Optional[str] = None
    audio_delta_count = 0
    player = _SpeakerPlayer()
    played = False

    try:
        # Open the realtime session on the voice agent's dedicated route.
        with client.beta.realtime.connect(agent_name=agent_name) as conn:

            def pump() -> None:
                nonlocal conversation_id, audio_delta_count
                active_response_id: Optional[str] = None
                while True:
                    try:
                        event = conn.recv(timeout=_RESPONSE_TIMEOUT)
                    except TimeoutError:
                        print("Timed out waiting for the agent's reply.")
                        conn.response.cancel(response_id=active_response_id)
                        # Consume the cancellation's own terminal event now, before the next
                        # turn starts: otherwise a late response.done for *this* cancelled
                        # response could be mistaken by the next pump() call for its own,
                        # ending it early and silently dropping the real next reply.
                        _drain_cancelled_response(conn, active_response_id)
                        return
                    if isinstance(event, RealtimeServerEventSessionCreated):
                        # The persisted conversation id (only present when conversation
                        # persistence is enabled) is set here, not on response.done.
                        conversation_id = event.conversation_id or conversation_id
                    if isinstance(event, RealtimeServerEventResponseCreated):
                        active_response_id = event.response.id
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
                        _safe_print(f"Agent: {event.transcript}")

            if has_greeting:
                # The service sends the configured greeting as its own response cycle the
                # instant the session opens, entirely independent of any user turn. Drain and
                # display it here, before the interactive loop starts: otherwise the first
                # pump() call below (triggered by the user's own first message) could instead
                # observe this unrelated, already in-flight response.done and return early,
                # silently dropping the real reply to what the user actually typed.
                print("(agent is greeting...)")
                pump()

            print("Type a message and press Enter. Blank line (or 'exit') ends the session.")

            while True:
                prompt = input("You:  ").strip()
                if not prompt or prompt.lower() in ("exit", "quit"):
                    break

                # Send the turn and ask the agent to respond.
                conn.conversation.item.create(
                    item=RealtimeConversationItemMessageUser(
                        type=RealtimeConversationItemType.MESSAGE,
                        content=[RealtimeConversationItemMessageUserContent(type="input_text", text=prompt)],
                    )
                )
                conn.response.create()
                pump()
    except KeyboardInterrupt:
        print("\n(ending session...)")
    except _CancellationNotConfirmed:
        print("Could not confirm a cancelled response finished; ending the session.")
    finally:
        played = player.enabled
        player.close()

    detail = "played" if played else "received"
    output_bytes = player.bytes_received
    print(f"(streamed {audio_delta_count} audio chunks, {detail} {player.seconds:.2f}s of audio)")
    print(
        f"Output audio: format=PCM16, sample_rate={_SAMPLE_RATE} Hz, channels=1, "
        f"duration={player.seconds:.2f}s, size={_format_size(output_bytes)}"
    )
    if not played:
        print("(install pyaudio to hear the reply: pip install pyaudio)")
    return conversation_id


def _read_conversation(client: AIProjectClient, agent_name: str, conversation_id: str) -> None:
    """Read the persisted conversation back over the read-only conversation API.

    :param client: The Foundry project client.
    :param agent_name: The voice agent name.
    :param conversation_id: The persisted conversation id.
    :type client: ~azure.ai.projects.AIProjectClient
    :type agent_name: str
    :type conversation_id: str
    """
    conversations = client.beta.agent_endpoint_conversations

    conversation = conversations.get(agent_name, conversation_id)
    print(f"Conversation {conversation.id}: status={conversation.status}, created_at={conversation.created_at}")

    print("Items (transcript):")
    for item in conversations.list_items(agent_name, conversation_id):
        role = item.get("role") or item.get("type")
        # Audio turns expose ``transcript``; text turns expose ``text``.
        parts = [(part.get("transcript") or part.get("text") or "").strip() for part in (item.get("content") or [])]
        transcript = " ".join(p for p in parts if p)
        print(f"  - {role} id={item.get('id')}")
        if transcript:
            _safe_print(f"      {transcript}")


def text_conversation() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ.get("FOUNDRY_VOICE_MODEL") or "gpt-realtime"
    agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or "sample-live-text-conversation-agent"

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        try:
            # 1) Create a voice agent with conversation persistence enabled (`store=True`) so the
            #    session's conversation can be fetched back by id afterward.
            definition = VoiceAgentDefinition(
                model_type=VoiceModelType.MANAGED,
                model=model,
                instructions="You are a friendly voice assistant. Keep replies short and natural.",
                audio=VoiceAgentAudioConfig(
                    output=VoiceAgentAudioOutputConfig(voice="en-US-AvaNeural", voice_type=VoiceType.AZURE_STANDARD),
                ),
                output_modalities=[VoiceOutputModality.AUDIO],
                greeting=VoiceAgentTemplateGreetingConfig(text="Hi, I'm here to help. What can I do for you?"),
                store=True,
            )
            project_client.agents.create_version(
                agent_name=agent_name,
                definition=definition,
            )

            # 2) Hold the realtime conversation against the freshly created agent.
            print(f"Starting realtime session with agent: {agent_name}")
            conversation_id = _run_text_conversation(project_client, agent_name, has_greeting=True)

            # 3) Fetch the persisted conversation back by id.
            if conversation_id:
                print(f"Reading persisted conversation {conversation_id}...")
                try:
                    _read_conversation(project_client, agent_name, conversation_id)
                except HttpResponseError as e:
                    print(f"Could not read conversation: {e.status_code} {e.reason}")
                # To fetch this session's audio afterward, use
                # `project_client.beta.agent_endpoint_conversations`:
                #   - get_audio(agent_name, conversation_id) for the merged
                #     whole-call stereo recording's metadata, then
                #     download_audio(agent_name, conversation_id) to stream
                #     the WAV bytes.
                #   - get_item_audio(agent_name, conversation_id, item_id) for a
                #     single turn's audio metadata, then
                #     download_item_audio(agent_name, conversation_id, item_id)
                #     to stream that turn's bytes.
                # See sample_voice_agent_read_conversation_audio.py for a full example.
            else:
                print("No conversation id was returned; nothing to read.")
        except HttpResponseError as e:
            print(f"Service responded with an error: {e.status_code} {e.reason}")
        finally:
            # 4) Clean up the agent created for this sample.
            project_client.agents.delete(agent_name=agent_name)
            print(f"Deleted voice agent: {agent_name}")


if __name__ == "__main__":
    try:
        text_conversation()
    except KeyboardInterrupt:
        print("\nInterrupted.")
