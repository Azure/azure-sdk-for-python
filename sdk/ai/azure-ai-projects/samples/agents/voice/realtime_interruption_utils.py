# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared interruption and recording helpers for the Realtime samples."""

from __future__ import annotations

import array
import asyncio
import base64
from dataclasses import dataclass
import io
import sys
import time
from typing import Any, Mapping, TYPE_CHECKING
import wave

from azure.ai.projects import models
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

if TYPE_CHECKING:
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
    from azure.ai.projects.operations import BetaRealtimeConnection
    from azure.ai.projects.aio.operations import AsyncBetaRealtimeConnection


TURN_TIMEOUT = 45.0
RECORDING_TIMEOUT = 90.0
_MIN_AUDIO_BYTES = 9600


def interruption_definition(model: str) -> models.VoiceAgentDefinition:
    """Configure a stored PCM16 session without requiring audio devices."""
    return models.VoiceAgentDefinition(
        model_type=models.VoiceModelType.MANAGED,
        model=model,
        instructions="Follow the user's request. Speak clearly and continue until interrupted.",
        audio=models.VoiceAgentAudioConfig(
            output=models.VoiceAgentAudioOutputConfig(
                voice="en-US-AvaNeural",
                voice_type=models.VoiceType.AZURE_STANDARD,
                format=models.RealtimeAudioFormatsAudioPcm(rate=24000),
            )
        ),
        output_modalities=[models.VoiceOutputModality.AUDIO],
        store=True,
    )


def _remaining(deadline: float, description: str) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError(f"Timed out waiting for {description}.")
    return remaining


@dataclass
class InterruptedTurn:
    """Track one response without confusing received audio with heard audio."""

    conversation_id: str = ""
    response_id: str = ""
    item_id: str = ""
    stored_item_id: str = ""
    received_audio_bytes: int = 0
    speech_received: bool = False
    interruption_requested: bool = False
    cancelled: bool = False
    truncated: bool = False

    @property
    def ready_to_interrupt(self) -> bool:
        return (
            not self.interruption_requested
            and bool(self.item_id)
            and self.speech_received
            and self.received_audio_bytes >= _MIN_AUDIO_BYTES
        )

    def consume(self, event: Mapping[str, Any]) -> None:
        event_type = event.get("type")
        if event_type == "error":
            error = event.get("error") or {}
            raise RuntimeError(f"Realtime interruption failed: {error.get('code')}: {error.get('message')}")
        if event_type == "session.created":
            self.conversation_id = event.get("conversation_id") or ""
            if not self.conversation_id:
                raise RuntimeError("The session did not provide a stored conversation ID.")
        elif event_type == "response.created":
            response = event.get("response") or {}
            if not self.response_id:
                self.response_id = response.get("id") or ""
                if not self.response_id:
                    raise RuntimeError("The response did not provide an ID.")
        elif (
            event_type in ("response.audio.delta", "response.output_audio.delta")
            and event.get("response_id") == self.response_id
        ):
            item_id = event.get("item_id")
            if not isinstance(item_id, str) or not item_id:
                raise RuntimeError("An audio delta did not provide an item ID.")
            if self.item_id and item_id != self.item_id:
                raise RuntimeError("The response unexpectedly produced more than one audio item.")
            self.item_id = item_id
            pcm = base64.b64decode(event["delta"], validate=True)
            if len(pcm) % 2:
                raise ValueError("The service returned a partial PCM16 sample.")
            self.received_audio_bytes += len(pcm)
            self.speech_received |= any(
                abs(int.from_bytes(pcm[index : index + 2], "little", signed=True)) > 256
                for index in range(0, len(pcm), 2)
            )
        elif event_type == "response.done":
            response = event.get("response") or {}
            if response.get("id") == self.response_id:
                if not self.interruption_requested or response.get("status") != "cancelled":
                    raise RuntimeError("The response ended without confirming the requested cancellation.")
                self.cancelled = True
        elif event_type == "conversation.item.truncated" and event.get("item_id") == self.item_id:
            if not self.interruption_requested or event.get("audio_end_ms") != 0:
                raise RuntimeError("The service did not confirm truncation to the requested playback position.")
            self.truncated = True


_PROMPT = {
    "type": "message",
    "role": "user",
    "content": [
        {
            "type": "input_text",
            "text": "Count slowly from one through fifty, saying every number aloud. Do not summarize the sequence.",
        }
    ],
}


def interrupt_reply(connection: BetaRealtimeConnection, turn: InterruptedTurn) -> None:
    """Cancel a speaking response and report that none of its audio was played."""
    deadline = time.monotonic() + TURN_TIMEOUT
    while not turn.conversation_id:
        turn.consume(connection.recv(timeout=_remaining(deadline, "session.created")))
    connection.conversation.item.create(item=_PROMPT)
    connection.response.create()
    while not (turn.cancelled and turn.truncated):
        turn.consume(connection.recv(timeout=_remaining(deadline, "response cancellation and item truncation")))
        if turn.ready_to_interrupt:
            turn.interruption_requested = True
            connection.response.cancel(response_id=turn.response_id)
            # This headless example played no samples. A real player must report its actual playback position.
            connection.conversation.item.truncate(item_id=turn.item_id, content_index=0, audio_end_ms=0)


async def interrupt_reply_async(connection: AsyncBetaRealtimeConnection, turn: InterruptedTurn) -> None:
    """Asynchronously cancel a speaking response without using audio devices."""
    deadline = time.monotonic() + TURN_TIMEOUT
    while not turn.conversation_id:
        timeout = _remaining(deadline, "session.created")
        turn.consume(await asyncio.wait_for(connection.recv(), timeout))
    await connection.conversation.item.create(item=_PROMPT)
    await connection.response.create()
    while not (turn.cancelled and turn.truncated):
        timeout = _remaining(deadline, "response cancellation and item truncation")
        turn.consume(await asyncio.wait_for(connection.recv(), timeout))
        if turn.ready_to_interrupt:
            turn.interruption_requested = True
            await connection.response.cancel(response_id=turn.response_id)
            await connection.conversation.item.truncate(item_id=turn.item_id, content_index=0, audio_end_ms=0)


def validate_generated_audio(metadata: models.VoiceGeneratedAudioItem, content: bytes, turn: InterruptedTurn) -> None:
    """Require a real, non-silent WAV belonging to the interrupted response."""
    if (
        metadata.conversation_id != turn.conversation_id
        or not turn.stored_item_id
        or metadata.item_id != turn.stored_item_id
        or metadata.role != "agent"
        or metadata.format != "wav"
        or metadata.codec != "pcm16"
        or metadata.sample_rate != 24000
        or metadata.channels != 1
        or metadata.duration_ms is None
        or metadata.duration_ms.total_seconds() <= 0
        or metadata.blob_uri is not None
    ):
        raise ValueError("Expected Foundry-managed PCM16 generated audio for the interrupted item.")
    if content[:4] != b"RIFF" or content[8:12] != b"WAVE":
        raise ValueError("The generated audio download is not a WAV file.")
    with wave.open(io.BytesIO(content), "rb") as recording:
        frames = recording.getnframes()
        pcm = recording.readframes(frames)
        if (
            recording.getcomptype() != "NONE"
            or recording.getsampwidth() != 2
            or recording.getframerate() != metadata.sample_rate
            or recording.getnchannels() != metadata.channels
            or frames <= 0
            or len(pcm) != frames * 2
            or abs(frames / metadata.sample_rate - metadata.duration_ms.total_seconds()) > 0.01
        ):
            raise ValueError("The generated WAV does not match its audio metadata.")
    samples = array.array("h", pcm)
    if sys.byteorder != "little":
        samples.byteswap()
    if not any(abs(sample) > 256 for sample in samples):
        raise ValueError("The generated recording contains no non-silent agent speech.")


def _recording_pending(exc: HttpResponseError) -> bool:
    return isinstance(exc, ResourceNotFoundError) or (
        exc.status_code == 409 and getattr(exc.error, "code", None) == "recording_not_ready"
    )


def _stored_audio_item(items: list[Mapping[str, Any]], response_id: str) -> str | None:
    candidates = [
        item
        for item in items
        if item.get("type") == "message" and item.get("role") == "assistant" and item.get("response_id") == response_id
    ]
    if not candidates:
        return None
    if len(candidates) != 1:
        raise RuntimeError("The interrupted response did not map to exactly one stored assistant item.")
    identifier = candidates[0].get("id")
    if not isinstance(identifier, str) or not identifier:
        raise RuntimeError("The stored assistant item did not provide its REST resource ID.")
    return identifier


def wait_for_generated_audio(
    client: AIProjectClient, agent_name: str, turn: InterruptedTurn
) -> tuple[models.VoiceGeneratedAudioItem, bytes]:
    """Wait for durable interruption artifacts before reading them once in a test."""
    deadline = time.monotonic() + RECORDING_TIMEOUT
    conversations = client.voice_agents.conversations
    while time.monotonic() < deadline:
        try:
            conversation = conversations.get(agent_name, turn.conversation_id)
            if conversation.status == "failed":
                raise RuntimeError("The interrupted conversation failed to persist.")
            if conversation.status == "completed":
                # Persisted REST item IDs differ from the native WebSocket item IDs.
                stored_item_id = _stored_audio_item(
                    list(conversations.list_items(agent_name, turn.conversation_id)), turn.response_id
                )
                if stored_item_id is not None:
                    turn.stored_item_id = stored_item_id
                    metadata = conversations.get_generated_audio_item(
                        agent_name, turn.conversation_id, turn.stored_item_id
                    )
                    content = b"".join(
                        conversations.download_generated_audio_item(
                            agent_name, turn.conversation_id, turn.stored_item_id
                        )
                    )
                    validate_generated_audio(metadata, content, turn)
                    return metadata, content
        except HttpResponseError as exc:
            if not _recording_pending(exc):
                raise
        time.sleep(min(1.0, _remaining(deadline, "stored generated audio")))
    raise TimeoutError("The interrupted response did not produce persisted generated audio before the deadline.")


async def wait_for_generated_audio_async(
    client: AsyncAIProjectClient, agent_name: str, turn: InterruptedTurn
) -> tuple[models.VoiceGeneratedAudioItem, bytes]:
    """Wait asynchronously for durable generated audio; never treat a 404 as success."""
    deadline = time.monotonic() + RECORDING_TIMEOUT
    conversations = client.voice_agents.conversations
    while time.monotonic() < deadline:
        try:
            conversation = await conversations.get(agent_name, turn.conversation_id)
            if conversation.status == "failed":
                raise RuntimeError("The interrupted conversation failed to persist.")
            if conversation.status == "completed":
                stored_item_id = _stored_audio_item(
                    [item async for item in conversations.list_items(agent_name, turn.conversation_id)],
                    turn.response_id,
                )
                if stored_item_id is not None:
                    turn.stored_item_id = stored_item_id
                    metadata = await conversations.get_generated_audio_item(
                        agent_name, turn.conversation_id, turn.stored_item_id
                    )
                    content = b"".join(
                        [
                            chunk
                            async for chunk in await conversations.download_generated_audio_item(
                                agent_name, turn.conversation_id, turn.stored_item_id
                            )
                        ]
                    )
                    validate_generated_audio(metadata, content, turn)
                    return metadata, content
        except HttpResponseError as exc:
            if not _recording_pending(exc):
                raise
        await asyncio.sleep(min(1.0, _remaining(deadline, "stored generated audio")))
    raise TimeoutError("The interrupted response did not produce persisted generated audio before the deadline.")
