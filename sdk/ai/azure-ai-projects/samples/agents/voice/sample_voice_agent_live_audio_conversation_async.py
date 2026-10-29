# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Send a WAV recording to GPT Live, or talk through a microphone and hear
    replies through your speakers. Async lets audio send and receive together.
    Both modes use PCM16 little-endian, mono, 24-kHz audio.

    The sample prints transcripts and audio byte counts, then deletes its
    temporary agent version. Microphone mode also reports dropped capture
    frames if sending cannot keep up. Device and playback errors are raised.

USAGE:
    python sample_voice_agent_live_audio_conversation_async.py

    Settings in this file:
    - USE_MICROPHONE = False (default): send a WAV file; no audio devices needed.
    - USE_MICROPHONE = True: use a microphone and speakers. Use headphones
      to avoid feedback; press Ctrl-C to stop.
    - SAVE_AUDIO = True: save reply audio in a unique user-temporary folder.
      The path is printed. Remove the folder when finished; it contains
      conversation content, not telemetry. Saving is off by default.

    pip install "azure-ai-projects[voice]" azure-identity python-dotenv
    pip install pyaudio  # Only required for microphone mode.

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required) - Your GPT Live deployment name.
    3) FOUNDRY_VOICE_AUDIO_INPUT_PATH (required for WAV mode only) - Path to an
       actual spoken-audio WAV file: uncompressed PCM16, mono, 24000 Hz.
    4) FOUNDRY_VOICE_AGENT_NAME (optional) - Prefix for the temporary agent name.

    Uses DefaultAzureCredential; conversation persistence is disabled.
    Choose a short spoken recording. WAV mode sends raw audio in 50-ms chunks
    and adds one second of silence. It finishes after three seconds without
    active reply audio or transcript updates because Live has no speech-finished
    event. Long pauses can cut a reply short; silence alone is not a reply.
    Low-level PCM (peak <= 256) does not extend the wait, but is still counted
    and saved when requested. Live handles turn-taking without response.cancel.
"""

from __future__ import annotations

import asyncio
import base64
import concurrent.futures
from contextlib import ExitStack
from dataclasses import dataclass
import os
from pathlib import Path
import queue
from tempfile import mkdtemp
import time
from typing import Any, Optional, TYPE_CHECKING
import wave

from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects import models

from live_sample_utils import (
    audio_settings,
    check_event,
    check_session_open,
    close_session_async,
    remaining_time,
    safe_print,
    sample_agent_name,
    wait_for_event_async,
)

if TYPE_CHECKING:
    from azure.ai.projects.aio.operations import AsyncBetaLiveConnection


USE_MICROPHONE = False
SAVE_AUDIO = False

_SAMPLE_RATE = 24000
_CHUNK_FRAMES = 1200
_OUTPUT_IDLE_SECONDS = 3.0
_SILENCE_PEAK_THRESHOLD = 256


@dataclass
class _AudioOutput:
    num_bytes: int = 0
    chunks: int = 0
    input_transcript: str = ""
    output_transcript: str = ""
    has_audio_activity: bool = False


def _microphone_backend() -> Any:
    try:
        import pyaudio
    except ImportError as exc:
        raise RuntimeError("Microphone mode requires PyAudio. Install it with: pip install pyaudio") from exc
    return pyaudio


class _MicrophoneAudio:
    """Bounded, nonblocking microphone capture and PCM speaker playback."""

    def __init__(self, connection: AsyncBetaLiveConnection, backend: Any) -> None:
        self._connection = connection
        self._backend = backend
        self._audio = backend.PyAudio()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._input_stream: Any = None
        self._output_stream: Any = None
        self._pending_send: Optional[concurrent.futures.Future[None]] = None
        self._capture_error: Optional[BaseException] = None
        self._capture_active = False
        self._playback_queue: queue.Queue[bytes] = queue.Queue(maxsize=200)
        self._playback_remaining = b""
        self.input_bytes = 0
        self.output_bytes = 0
        self.dropped_frames = 0

    async def _append_input_audio(self, pcm: bytes) -> None:
        await self._connection.session.input_audio.append(audio=pcm)
        self.input_bytes += len(pcm)

    def _capture_callback(self, pcm: bytes, _frame_count: int, _time_info: Any, status: int) -> tuple[None, int]:
        if not self._capture_active:
            return None, self._backend.paAbort
        if status:
            self._capture_error = RuntimeError(f"Microphone callback reported audio status {status}.")
            return None, self._backend.paAbort
        if self._pending_send is not None:
            if not self._pending_send.done():
                self.dropped_frames += 1
                return None, self._backend.paContinue
            if self._pending_send.cancelled():
                self._capture_error = RuntimeError("The microphone audio send was cancelled.")
                return None, self._backend.paAbort
            failure = self._pending_send.exception()
            if failure is not None:
                self._capture_error = failure
                return None, self._backend.paAbort
        assert self._loop is not None
        self._pending_send = asyncio.run_coroutine_threadsafe(self._append_input_audio(pcm), self._loop)
        return None, self._backend.paContinue

    def _playback_callback(self, _pcm: Any, frame_count: int, _time_info: Any, status: int) -> tuple[bytes, int]:
        wanted = frame_count * 2
        if status:
            self._capture_error = RuntimeError(f"Speaker callback reported audio status {status}.")
            return bytes(wanted), self._backend.paAbort
        output = self._playback_remaining[:wanted]
        self._playback_remaining = self._playback_remaining[wanted:]
        while len(output) < wanted:
            try:
                chunk = self._playback_queue.get_nowait()
            except queue.Empty:
                output += bytes(wanted - len(output))
                break
            take = wanted - len(output)
            output += chunk[:take]
            self._playback_remaining = chunk[take:]
        return output, self._backend.paContinue

    def start(self) -> None:
        audio = self._audio
        if audio is None:
            raise RuntimeError("Cannot restart closed microphone audio devices.")
        self._loop = asyncio.get_running_loop()
        self._output_stream = audio.open(
            format=self._backend.paInt16,
            channels=1,
            rate=_SAMPLE_RATE,
            output=True,
            frames_per_buffer=_CHUNK_FRAMES,
            stream_callback=self._playback_callback,
            start=False,
        )
        self._input_stream = audio.open(
            format=self._backend.paInt16,
            channels=1,
            rate=_SAMPLE_RATE,
            input=True,
            frames_per_buffer=_CHUNK_FRAMES,
            stream_callback=self._capture_callback,
            start=False,
        )
        self._capture_active = True
        self._output_stream.start_stream()
        self._input_stream.start_stream()

    def check_capture_error(self) -> None:
        if self._capture_error is not None:
            raise self._capture_error
        if self._pending_send is not None and self._pending_send.done():
            self._pending_send.result()

    def enqueue_audio(self, pcm: bytes) -> None:
        if len(pcm) % 2:
            raise ValueError("The service returned an incomplete PCM16 sample.")
        self.output_bytes += len(pcm)
        try:
            self._playback_queue.put_nowait(pcm)
        except queue.Full as exc:
            raise RuntimeError("Speaker playback fell behind; the audio buffer is full.") from exc

    async def stop(self) -> None:
        self._capture_active = False
        try:
            try:
                if self._input_stream is not None:
                    stream, self._input_stream = self._input_stream, None
                    try:
                        stream.stop_stream()
                    finally:
                        stream.close()
            finally:
                if self._pending_send is not None:
                    pending, self._pending_send = self._pending_send, None
                    if pending.cancelled():
                        raise RuntimeError("The microphone audio send was cancelled.")
                    await asyncio.wrap_future(pending)
        finally:
            try:
                if self._output_stream is not None:
                    stream, self._output_stream = self._output_stream, None
                    try:
                        stream.stop_stream()
                    finally:
                        stream.close()
            finally:
                if self._audio is not None:
                    audio, self._audio = self._audio, None
                    audio.terminate()


async def _stream_microphone(
    connection: AsyncBetaLiveConnection, backend: Any, output_file: Optional[wave.Wave_write]
) -> bool:
    audio = _MicrophoneAudio(connection, backend)
    last_role = ""
    try:
        audio.start()
        print("Speak now -- GPT Live replies through your speakers. Use headphones to avoid feedback.")
        print("Press Ctrl-C to stop the microphone, close the session, and clean up.")
        while True:
            audio.check_capture_error()
            try:
                event = await asyncio.wait_for(connection.recv(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            check_event(event)
            if event.get("type") == "session.closed":
                reason = event.get("reason")
                if reason not in ("close_requested", "expired", "remote_hangup"):
                    raise RuntimeError(f"Live session ended unexpectedly: {reason}")
                print(f"\nSession closed: {reason}")
                return True
            if isinstance(event, models.LiveOutputAudioDelta):
                pcm = base64.b64decode(event.delta, validate=True)
                audio.enqueue_audio(pcm)
                if output_file is not None:
                    output_file.writeframesraw(pcm)
            elif isinstance(
                event, (models.LiveServerEventLiveInputTranscriptDelta, models.LiveServerEventLiveOutputTranscriptDelta)
            ):
                role = "You" if isinstance(event, models.LiveServerEventLiveInputTranscriptDelta) else "Agent"
                if role != last_role:
                    safe_print(f"\n{role}: ", end="")
                    last_role = role
                safe_print(event.delta, end="")
            elif isinstance(event, models.LiveServerEventLiveDelegationCreated):
                if event.delegation.target == "client":
                    await connection.session.commentary.append(
                        content="This sample cannot look up external information. Briefly acknowledge the spoken request.",
                        delegation_id=event.delegation.id,
                    )
    finally:
        try:
            await audio.stop()
        finally:
            print(
                f"\nInput audio: {audio.input_bytes} bytes ({audio.input_bytes / 1048576:.2f} MiB), "
                f"PCM16, 24000 Hz, mono, {audio.input_bytes / 48000:.2f}s."
            )
            print(
                f"Output audio: {audio.output_bytes} bytes ({audio.output_bytes / 1048576:.2f} MiB), "
                f"PCM16, 24000 Hz, mono, {audio.output_bytes / 48000:.2f}s."
            )
            print(f"Total audio transferred: {audio.input_bytes + audio.output_bytes} bytes.")
            if audio.dropped_frames:
                print(f"Dropped {audio.dropped_frames} microphone frame(s) while a previous send was in flight.")


def _has_audio_activity(pcm: bytes) -> bool:
    return any(
        abs(int.from_bytes(pcm[offset : offset + 2], "little", signed=True)) > _SILENCE_PEAK_THRESHOLD
        for offset in range(0, len(pcm), 2)
    )


def _validate_recording(recording: wave.Wave_read) -> None:
    if (
        recording.getnchannels() != 1
        or recording.getsampwidth() != 2
        or recording.getframerate() != _SAMPLE_RATE
        or recording.getcomptype() != "NONE"
    ):
        raise ValueError("FOUNDRY_VOICE_AUDIO_INPUT_PATH must be an uncompressed PCM16, mono, 24000 Hz WAV file.")
    if recording.getnframes() == 0:
        raise ValueError("The input WAV contains no audio frames.")


async def _send_audio(connection: AsyncBetaLiveConnection, recording: wave.Wave_read, finished: asyncio.Event) -> int:
    num_bytes = 0
    while chunk := recording.readframes(_CHUNK_FRAMES):
        await connection.session.input_audio.append(audio=chunk)
        num_bytes += len(chunk)
        await asyncio.sleep(len(chunk) / (2 * _SAMPLE_RATE))
    if num_bytes == 0:
        raise RuntimeError("No recorded audio frames were sent.")
    # Trailing silence lets the model finish the recorded speech turn.
    for _ in range(_SAMPLE_RATE // _CHUNK_FRAMES):
        silence = b"\x00\x00" * _CHUNK_FRAMES
        await connection.session.input_audio.append(audio=silence)
        num_bytes += len(silence)
        await asyncio.sleep(_CHUNK_FRAMES / _SAMPLE_RATE)
    finished.set()
    return num_bytes


async def _receive_audio(
    connection: AsyncBetaLiveConnection,
    finished: asyncio.Event,
    timeout: float,
    output_file: Optional[wave.Wave_write],
) -> _AudioOutput:
    output = _AudioOutput()
    deadline = time.monotonic() + timeout
    last_content = time.monotonic()
    while True:
        if finished.is_set() and output.has_audio_activity and time.monotonic() - last_content >= _OUTPUT_IDLE_SECONDS:
            return output
        remaining = remaining_time(deadline, "GPT Live reply audio")
        try:
            event = await asyncio.wait_for(connection.recv(), timeout=min(remaining, 1.0))
        except asyncio.TimeoutError:
            continue
        check_event(event)
        check_session_open(event)
        if isinstance(event, models.LiveOutputAudioDelta):
            pcm = base64.b64decode(event.delta, validate=True)
            if len(pcm) % 2:
                raise ValueError("The service returned an incomplete PCM16 sample.")
            output.num_bytes += len(pcm)
            output.chunks += 1
            if output_file is not None:
                output_file.writeframesraw(pcm)
            if _has_audio_activity(pcm):
                output.has_audio_activity = True
                last_content = time.monotonic()
        elif isinstance(event, models.LiveServerEventLiveInputTranscriptDelta):
            output.input_transcript += event.delta
        elif isinstance(event, models.LiveServerEventLiveOutputTranscriptDelta):
            output.output_transcript += event.delta
            if event.delta.strip():
                last_content = time.monotonic()
        elif isinstance(event, models.LiveServerEventLiveDelegationCreated):
            if event.delegation.target == "client":
                await connection.session.commentary.append(
                    content="This sample cannot look up external information. Briefly acknowledge the recorded request.",
                    delegation_id=event.delegation.id,
                )
                print("Replied to a client-owned delegation with associated commentary.")


async def _stream_recording(
    connection: AsyncBetaLiveConnection, recording: wave.Wave_read, output_file: Optional[wave.Wave_write]
) -> None:
    finished = asyncio.Event()
    timeout = recording.getnframes() / _SAMPLE_RATE + 60
    sender = asyncio.create_task(_send_audio(connection, recording, finished))
    receiver = asyncio.create_task(_receive_audio(connection, finished, timeout, output_file))
    try:
        input_bytes, output = await asyncio.wait_for(asyncio.gather(sender, receiver), timeout=timeout)
    except asyncio.TimeoutError as exc:
        raise TimeoutError("Timed out streaming the recording or waiting for nonempty GPT Live reply audio.") from exc
    finally:
        # Live has no response.cancel. Cancel local work and then request session.close.
        for task in (sender, receiver):
            if not task.done():
                task.cancel()
        await asyncio.gather(sender, receiver, return_exceptions=True)
    if input_bytes <= 0 or output.num_bytes <= 0 or not output.has_audio_activity:
        raise RuntimeError("A successful conversation requires nonzero input and non-silent reply audio.")
    for label, transcript in (("Input", output.input_transcript), ("Output", output.output_transcript)):
        if transcript and not transcript.strip():
            raise RuntimeError(f"{label} transcript events contained no usable text.")
        safe_print(f"{label} transcript: {transcript.strip() or '(not emitted by the service)'}")
    print(f"Sent {input_bytes} PCM16 bytes, including 48000 bytes of trailing silence.")
    print(f"Received {output.num_bytes} PCM16 bytes in {output.chunks} chunks ({output.num_bytes / 48000:.2f}s).")


async def _run_audio_conversation(
    project_client: AIProjectClient,
    agent_name: str,
    agent_version: str,
    recording: Optional[wave.Wave_read],
    output_file: Optional[wave.Wave_write],
    *,
    audio_backend: Any = None,
) -> None:
    if recording is None and audio_backend is None:
        raise ValueError("Microphone mode requires an audio backend.")
    session_closed = False
    cancelled = False
    async with project_client.beta.voice_agents.live.connect(
        agent_name=agent_name, agent_version=agent_version, store=False
    ) as connection:
        try:
            await wait_for_event_async(connection, "session.started")
            if recording is None:
                try:
                    session_closed = await _stream_microphone(connection, audio_backend, output_file)
                except asyncio.CancelledError:
                    print("\n(ending microphone conversation...)")
                    cancelled = True
            else:
                print("Live session started; sending the recording and receiving audio concurrently.")
                await _stream_recording(connection, recording, output_file)
        finally:
            if not session_closed:
                await close_session_async(connection)
    if cancelled:
        raise asyncio.CancelledError


async def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_VOICE_AGENT_MODEL"]
    backend = _microphone_backend() if USE_MICROPHONE else None
    input_path = None if USE_MICROPHONE else Path(os.environ["FOUNDRY_VOICE_AUDIO_INPUT_PATH"])
    output_path: Optional[Path] = None
    agent_name = sample_agent_name("audio")

    with ExitStack() as files:
        recording = files.enter_context(wave.open(str(input_path), "rb")) if input_path is not None else None
        if recording is not None:
            _validate_recording(recording)
        output_file: Optional[wave.Wave_write] = None
        if SAVE_AUDIO:
            output_directory = Path(mkdtemp(prefix="voice-agent-live-audio-"))
            output_path = output_directory / "reply.wav"
            print(f"Audio output directory: {output_directory}")
            output_stream = files.enter_context(output_path.open("xb"))
            output_file = files.enter_context(wave.open(output_stream, "wb"))
            output_file.setnchannels(1)
            output_file.setsampwidth(2)
            output_file.setframerate(_SAMPLE_RATE)
        async with (
            DefaultAzureCredential() as credential,
            AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
        ):
            created_version = None
            try:
                created_version = await project_client.agents.create_version(
                    agent_name=agent_name,
                    definition=models.VoiceAgentLiveDefinition(
                        model=model,
                        instructions=(
                            "You are a friendly voice assistant. Briefly answer the user's speech. "
                            "Keep replies to one short sentence. Delegate external lookups to the client."
                        ),
                        audio=audio_settings(),
                        delegation=models.LiveClientDelegationParam(),
                        store=False,
                    ),
                )
                if USE_MICROPHONE:
                    await _run_audio_conversation(
                        project_client, agent_name, created_version.version, None, output_file, audio_backend=backend
                    )
                else:
                    await _run_audio_conversation(
                        project_client, agent_name, created_version.version, recording, output_file
                    )
            finally:
                if created_version is not None:
                    await project_client.agents.delete_version(
                        agent_name=agent_name, agent_version=created_version.version
                    )
                    print(f"Deleted sample agent version: {created_version.version}")
    if output_path:
        print(f"Saved actual returned PCM16 WAV audio: {output_path} (not telemetry).")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
