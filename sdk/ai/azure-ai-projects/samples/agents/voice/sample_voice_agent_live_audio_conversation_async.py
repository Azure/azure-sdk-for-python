# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end hands-free, bidirectional voice conversation against an
    existing voice agent, using the ``client.realtime`` namespace added on top
    of the generated azure-ai-projects client (see
    ``azure.ai.projects.aio.AsyncRealtime``). This mirrors the ergonomics of
    the OpenAI Python realtime client.

      1. Stream live mic audio and let the agent's server-side VAD detect your
         turns: your speech is transcribed, the agent replies through the
         speakers, and talking over it barges in.
      2. Read the persisted conversation back (requires the agent to have been
         created with `store=True`; see sample_voice_agent_basic.py).

    Capture and playback use non-blocking pyaudio callbacks; reply audio is
    sequence-numbered so a barge-in can skip whatever is still queued. The
    agent owns turn detection and noise suppression server-side. Use a headset
    to avoid echo.

    Mic audio is sent as base64 PCM16; the reply arrives as typed
    ``response.output_audio.*`` events, decoded to PCM16, mono, 24 kHz.
    Requires ``aiohttp`` and ``pyaudio``.

      pip install "azure-ai-projects>=2.0.0" azure-identity aiohttp pyaudio

USAGE:
    python sample_voice_agent_live_audio_conversation_async.py

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - Foundry project endpoint:
       https://<account>.services.ai.azure.com/api/projects/<project>
    2) FOUNDRY_VOICE_AGENT_NAME (required) - name of an existing voice agent to
       converse with (created with `store=True` to persist conversations; see
       sample_voice_agent_basic.py).

    Runs until you press Ctrl-C. Authenticates with DefaultAzureCredential, so
    sign in first (e.g. `az login`).
"""

import asyncio
import os
import queue
from typing import Any, Final, Optional

from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential

# AsyncRealtimeConnection is re-exported dynamically via aio/_patch.py's `__all__`; pylint's
# static import resolution cannot trace that, but the symbol is valid (verified by Pyright/mypy).
from azure.ai.projects.aio import AsyncRealtimeConnection, AIProjectClient  # pylint: disable=no-name-in-module
from azure.ai.projects.models import (
    VoiceAgentServerEventConversationItemInputAudioTranscriptionCompleted,
    VoiceAgentServerEventInputAudioBufferSpeechStarted,
    VoiceAgentServerEventResponseAudioDelta,
    VoiceAgentServerEventResponseAudioTranscriptDone,
    VoiceAgentServerEventResponseDone,
    RealtimeServerEventError,
)

# Audio is streamed both ways as PCM16, mono, 24 kHz.
_SAMPLE_RATE: Final = 24000

# pyaudio callback buffer size (~50 ms of PCM16 audio per callback).
_CHUNK_SAMPLES: Final = 1200

try:
    import pyaudio  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - required audio dependency
    pyaudio: Any = None  # type: ignore[no-redef]


class _AudioProcessor:  # pylint: disable=too-many-instance-attributes
    """Real-time mic capture and speaker playback via non-blocking pyaudio callbacks.

    * Capture appends each raw PCM16 frame to the input buffer (the realtime
      client base64-encodes it).
    * Playback pulls sequence-numbered PCM16 from a queue, always returning the
      exact sample count pyaudio asked for (a wrong size corrupts audio).
    * ``skip_pending_audio`` bumps a base sequence number so audio queued before
      a barge-in is dropped, stopping playback the instant the user speaks.
    """

    def __init__(self, connection: "AsyncRealtimeConnection") -> None:
        self._conn = connection
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._audio = pyaudio.PyAudio()

        # Playback with sequence numbers for interrupt handling.
        self._playback_queue: "queue.Queue[tuple[int, Optional[bytes]]]" = queue.Queue()
        self._playback_base = 0
        self._next_seq = 0
        self._bytes = 0

        self._input_stream = None
        self._output_stream = None

    # -- capture -----------------------------------------------------------

    def start_capture(self) -> None:
        """Start streaming microphone audio to the service via a callback."""
        if self._input_stream is not None:
            return
        self._loop = asyncio.get_running_loop()

        def _capture_callback(in_data, _frame_count, _time_info, _status):
            # Runs on a pyaudio thread: hand the frame to the event loop to append.
            assert self._loop is not None
            asyncio.run_coroutine_threadsafe(self._conn.input_audio_buffer.append(audio=in_data), self._loop)
            return (None, pyaudio.paContinue)

        self._input_stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=_SAMPLE_RATE,
            input=True,
            frames_per_buffer=_CHUNK_SAMPLES,
            stream_callback=_capture_callback,
        )

    # -- playback ------------------------------------------------------------

    def start_playback(self) -> None:
        """Initialize the speaker playback callback."""
        if self._output_stream is not None:
            return
        remaining = b""

        def _playback_callback(_in_data, frame_count, _time_info, _status):
            nonlocal remaining
            wanted = frame_count * pyaudio.get_sample_size(pyaudio.paInt16)
            out = remaining[:wanted]
            remaining = remaining[wanted:]

            while len(out) < wanted:
                try:
                    seq, data = self._playback_queue.get_nowait()
                except queue.Empty:
                    out = out + bytes(wanted - len(out))  # pad with silence
                    continue
                if not data:
                    break  # end-of-stream marker
                if seq < self._playback_base:
                    remaining = b""  # skipped by a barge-in
                    continue
                take = wanted - len(out)
                out = out + data[:take]
                remaining = data[take:]

            return (out, pyaudio.paContinue)

        self._output_stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=_SAMPLE_RATE,
            output=True,
            frames_per_buffer=_CHUNK_SAMPLES,
            stream_callback=_playback_callback,
        )

    def _next_seq_num(self) -> int:
        seq = self._next_seq
        self._next_seq += 1
        return seq

    def queue_audio(self, pcm: bytes) -> None:
        """Queue one decoded PCM16 chunk of the agent's reply for playback.

        :param pcm: Decoded PCM16 audio bytes.
        :type pcm: bytes
        """
        self._bytes += len(pcm)
        self._playback_queue.put((self._next_seq_num(), pcm))

    def skip_pending_audio(self) -> None:
        """Drop audio still queued for playback (used on barge-in)."""
        self._playback_base = self._next_seq_num()

    def shutdown(self) -> None:
        """Stop capture and playback and release the audio device."""
        if self._input_stream is not None:
            self._input_stream.stop_stream()
            self._input_stream.close()
            self._input_stream = None
        if self._output_stream is not None:
            self.skip_pending_audio()
            self._playback_queue.put((self._next_seq_num(), None))
            self._output_stream.stop_stream()
            self._output_stream.close()
            self._output_stream = None
        self._audio.terminate()

    @property
    def seconds(self) -> float:
        """Total reply audio received, in seconds (PCM16 = 2 bytes/sample).

        :rtype: float
        """
        return self._bytes / 2 / _SAMPLE_RATE


async def _run_audio_conversation(client: AIProjectClient, agent_name: str) -> Optional[str]:
    """Hold a live, hands-free conversation with barge-in.

    :param client: The Foundry project client.
    :param agent_name: The existing voice agent name.
    :type client: ~azure.ai.projects.aio.AIProjectClient
    :type agent_name: str
    :return: The persisted conversation id, if one is created.
    :rtype: str or None
    """
    if pyaudio is None:
        print("This sample needs pyaudio for audio: pip install pyaudio")
        return None

    conversation_id: Optional[str] = None

    # Open the realtime session on the voice agent's dedicated route.
    async with client.realtime.connect(agent_name=agent_name) as conn:
        # A voice agent owns its model, instructions, voice, turn detection, and
        # noise suppression server-side, so this client sends no ``session.update``.
        ap = _AudioProcessor(conn)
        ap.start_playback()
        ap.start_capture()

        print("Speak now -- the agent replies after you pause.")
        print("(talk over the agent to interrupt it; press Ctrl-C to end the session)")

        try:
            async for event in conn:
                if isinstance(event, VoiceAgentServerEventInputAudioBufferSpeechStarted):
                    # Barge-in: stop the active response and drop whatever reply
                    # audio is still queued locally. The service only supports
                    # output_audio_buffer.clear in avatar mode.
                    await conn.response.cancel()
                    ap.skip_pending_audio()
                    print("(listening...)")
                elif isinstance(event, VoiceAgentServerEventConversationItemInputAudioTranscriptionCompleted):
                    print(f"You:  {event.transcript.strip()}")
                elif isinstance(event, RealtimeServerEventError):
                    # Non-fatal errors are reported; a fatal one closes the socket.
                    print(f"Session error: {event.error.message}")
                elif isinstance(event, VoiceAgentServerEventResponseAudioDelta):
                    # Each delta is a decoded PCM16 chunk; queue it.
                    ap.queue_audio(event.delta)
                elif isinstance(event, VoiceAgentServerEventResponseAudioTranscriptDone):
                    print(f"Agent: {event.transcript}")
                elif isinstance(event, VoiceAgentServerEventResponseDone):
                    conversation_id = event.response.conversation_id or conversation_id
        except (KeyboardInterrupt, asyncio.CancelledError):
            # Ctrl-C ends the session; read back whatever was persisted so far.
            print("\n(ending session...)")
        finally:
            print(f"(received {ap.seconds:.2f}s of reply audio this session)")
            ap.shutdown()

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
    conversations = client.agent_endpoint_conversations

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


async def audio_conversation() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ["FOUNDRY_VOICE_AGENT_NAME"]

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        try:
            # 1) Hold a live microphone conversation with the existing agent.
            print(f"Starting realtime session with agent: {agent_name}")
            conversation_id = await _run_audio_conversation(project_client, agent_name)

            # 2) Read the persisted conversation back.
            if conversation_id:
                print(f"Reading persisted conversation {conversation_id!r}...")
                try:
                    await _read_conversation(project_client, agent_name, conversation_id)
                except HttpResponseError as e:
                    print(f"Could not read conversation: {e.status_code} {e.reason}")
            else:
                print("No conversation id was returned; nothing to read.")
        except HttpResponseError as e:
            print(f"Service responded with an error: {e.status_code} {e.reason}")


if __name__ == "__main__":
    try:
        asyncio.run(audio_conversation())
    except KeyboardInterrupt:
        print("\nInterrupted.")
