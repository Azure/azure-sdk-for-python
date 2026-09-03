# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end hands-free, bidirectional voice conversation using the
    ``client.realtime`` namespace added on top of the generated
    azure-ai-projects client (see ``azure.ai.projects.aio.AsyncRealtime``).
    This mirrors the ergonomics of the OpenAI Python realtime client.

      1. Generate a starter voice agent (see sample_voice_agent_generate.py),
         then publish a version with `store=True` so the conversation can be
         read back afterward.
      2. Stream live mic audio and let the agent's server-side VAD detect your
         turns: your speech is transcribed, the agent replies through the
         speakers, and talking over it barges in.
      3. Fetch the persisted conversation back by id.
      4. Delete the agent created for this sample.

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
    2) FOUNDRY_VOICE_AGENT_NAME - Optional. Name for the agent created by this
       sample. Defaults to "sample-live-audio-conversation-agent-async".

    Runs until you press Ctrl-C. Authenticates with DefaultAzureCredential, so
    sign in first (e.g. `az login`).
"""

import asyncio
import concurrent.futures
import os
import queue
from typing import Any, Final, Optional

from dotenv import load_dotenv
from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential

# AsyncRealtimeConnection is re-exported dynamically via aio/_patch.py's `__all__`; pylint's
# static import resolution cannot trace that, but the symbol is valid (verified by Pyright/mypy).
from azure.ai.projects.aio import AsyncRealtimeConnection, AIProjectClient  # pylint: disable=no-name-in-module
from azure.ai.projects.models import (
    AgentKind,
    GenerateVoiceAgentRequest,
    VoiceAgentDefinition,
    RealtimeServerEventConversationItemInputAudioTranscriptionCompleted,
    RealtimeServerEventInputAudioBufferSpeechStarted,
    RealtimeServerEventResponseAudioDelta,
    RealtimeServerEventResponseAudioTranscriptDone,
    RealtimeServerEventResponseCreated,
    RealtimeServerEventResponseDone,
    RealtimeServerEventSessionCreated,
    RealtimeServerEventError,
)

load_dotenv()

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

        # Bounds capture backpressure to a single in-flight send (see start_capture).
        self._pending_send: "Optional[concurrent.futures.Future[None]]" = None
        self._dropped_frames = 0

        self._input_stream = None
        self._output_stream = None

    # -- capture -----------------------------------------------------------

    def start_capture(self) -> None:
        """Start streaming microphone audio to the service via a callback."""
        if self._input_stream is not None:
            return
        self._loop = asyncio.get_running_loop()

        def _capture_callback(in_data, _frame_count, _time_info, _status):
            # Runs on a pyaudio thread: hand the frame to the event loop to append. Each call
            # schedules a coroutine on the loop via a thread-safe handoff; if sending falls
            # behind real-time capture (for example, network backpressure on the WebSocket),
            # unconditionally scheduling a new one every callback would let pending sends
            # accumulate without bound. Instead, only keep at most one in flight and drop
            # (skip sending) this frame if the previous send hasn't completed yet.
            assert self._loop is not None
            if self._pending_send is not None and not self._pending_send.done():
                self._dropped_frames += 1
                return (None, pyaudio.paContinue)
            self._pending_send = asyncio.run_coroutine_threadsafe(
                self._conn.input_audio_buffer.append(audio=in_data), self._loop
            )
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
        # The sequence number the currently-buffered `remaining` bytes were dequeued from, so a
        # barge-in that lands *between* callback invocations can still discard them below.
        remaining_seq = -1

        def _playback_callback(_in_data, frame_count, _time_info, _status):
            nonlocal remaining, remaining_seq
            if remaining and remaining_seq < self._playback_base:
                remaining = b""  # a barge-in advanced the base since this chunk was dequeued

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
                    # end-of-stream marker: pad up to the exact frame size pyaudio asked for
                    # instead of returning a short buffer, which would corrupt playback on close.
                    out = out + bytes(wanted - len(out))
                    break
                if seq < self._playback_base:
                    remaining = b""  # skipped by a barge-in
                    continue
                take = wanted - len(out)
                out = out + data[:take]
                remaining = data[take:]
                remaining_seq = seq

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
            if self._dropped_frames:
                print(f"(dropped {self._dropped_frames} mic frame(s) while a send was still in flight)")
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
    response_active = False

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
                if isinstance(event, RealtimeServerEventSessionCreated):
                    # The persisted conversation id (only present when conversation
                    # persistence is enabled) is set here, not on response.done.
                    conversation_id = event.conversation_id or conversation_id
                elif isinstance(event, RealtimeServerEventInputAudioBufferSpeechStarted):
                    # speech_started fires for every user turn, including the very first one,
                    # when no response is active yet. Only cancel (barge-in) if a response is
                    # actually in flight; canceling with none active is a service error.
                    if response_active:
                        await conn.response.cancel()
                        ap.skip_pending_audio()
                        print("(listening...)")
                elif isinstance(event, RealtimeServerEventConversationItemInputAudioTranscriptionCompleted):
                    print(f"You:  {event.transcript.strip()}")
                elif isinstance(event, RealtimeServerEventError):
                    # Non-fatal errors are reported; a fatal one closes the socket.
                    print(f"Session error: {event.error.message}")
                elif isinstance(event, RealtimeServerEventResponseCreated):
                    response_active = True
                elif isinstance(event, RealtimeServerEventResponseAudioDelta):
                    # Each delta is a decoded PCM16 chunk; queue it.
                    ap.queue_audio(event.delta)
                elif isinstance(event, RealtimeServerEventResponseAudioTranscriptDone):
                    print(f"Agent: {event.transcript}")
                elif isinstance(event, RealtimeServerEventResponseDone):
                    response_active = False
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


async def audio_conversation() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or "sample-live-audio-conversation-agent-async"

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

            # 3) Hold a live microphone conversation with the freshly created agent.
            print(f"Starting realtime session with agent: {agent_name}")
            conversation_id = await _run_audio_conversation(project_client, agent_name)

            # 4) Fetch the persisted conversation back by id.
            if conversation_id:
                print(f"Reading persisted conversation {conversation_id!r}...")
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
        asyncio.run(audio_conversation())
    except KeyboardInterrupt:
        print("\nInterrupted.")
