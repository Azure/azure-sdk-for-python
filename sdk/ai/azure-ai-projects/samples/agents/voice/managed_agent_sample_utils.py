# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Audio and event handling shared only by the managed prompt-agent Live samples."""

from __future__ import annotations

import asyncio
import base64
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
import time
from typing import Any, TYPE_CHECKING
import wave

from azure.ai.projects import models

from live_sample_utils import (
    RESPONSE_TIMEOUT,
    audio_settings,
    check_event,
    check_session_open,
    remaining_time,
    safe_print,
)

if TYPE_CHECKING:
    from azure.ai.projects.operations import BetaLiveConnection, LiveServerEvent
    from azure.ai.projects.aio.operations import AsyncBetaLiveConnection


SAMPLE_RATE = 24000
CHUNK_BYTES = 2400  # 50 ms of mono PCM16.
MAX_INPUT_SECONDS = 30
OUTPUT_IDLE_SECONDS = 3.0
_SILENCE = bytes(CHUNK_BYTES)

PROMPT_INSTRUCTIONS = (
    "You answer spoken questions delegated by a voice assistant. Return exactly two text sections: "
    "start with the literal marker [thinking] and a brief task status, not private reasoning; "
    "then the literal marker [commentary] and the actual answer in one short, speakable sentence. "
    "Do not use Markdown fences. Do not claim to have used tools or external sources."
)


def read_input_audio(path: Path) -> bytes:
    """Validate the entire short WAV before creating either service resource."""
    try:
        with wave.open(str(path), "rb") as recording:
            if (
                recording.getnchannels() != 1
                or recording.getsampwidth() != 2
                or recording.getframerate() != SAMPLE_RATE
                or recording.getcomptype() != "NONE"
            ):
                raise ValueError("FOUNDRY_VOICE_AUDIO_INPUT_PATH must be an uncompressed PCM16, mono, 24000 Hz WAV.")
            frames = recording.getnframes()
            if not 0 < frames <= SAMPLE_RATE * MAX_INPUT_SECONDS:
                raise ValueError(f"The input WAV must contain between one frame and {MAX_INPUT_SECONDS} seconds.")
            pcm = recording.readframes(frames + 1)
            if len(pcm) != frames * 2:
                raise ValueError("The input WAV has truncated or incomplete PCM16 frames.")
    except (wave.Error, EOFError) as exc:
        raise ValueError("FOUNDRY_VOICE_AUDIO_INPUT_PATH must be a readable PCM16 WAV file.") from exc
    if not _has_audio_activity(pcm):
        raise ValueError("The input WAV must contain audible spoken audio, not only silence.")
    return pcm


def live_definition(model: str, backend_name: str, backend_version: str) -> models.VoiceAgentLiveDefinition:
    """Pin delegation to the exact prompt-agent version created in this project."""
    return models.VoiceAgentLiveDefinition(
        model_type=models.VoiceModelType.SELF_DEPLOYED,
        model=model,
        instructions=(
            "You are a friendly voice assistant. Delegate every substantive spoken question to your backend. "
            "Do not answer from your own knowledge or give a spoken acknowledgement. "
            "Wait for backend guidance, then speak its answer in one short sentence."
        ),
        audio=audio_settings(),
        delegation=models.VoiceAgentLiveManagedAgentDelegation(agent_name=backend_name, agent_version=backend_version),
        store=False,
    )


def check_managed_session(session: models.VoiceAgentLiveSessionResource, name: str, version: str) -> None:
    """Inspect opaque session ownership metadata, not a persisted-definition DTO."""
    if not isinstance(session, models.VoiceAgentLiveSessionResource):
        raise RuntimeError("The Live session did not contain a typed session snapshot.")
    owner = session.delegation
    if (
        not isinstance(owner, Mapping)
        or owner.get("type") != "foundry_managed_agent"
        or owner.get("agent_name") != name
        or owner.get("agent_version") != version
    ):
        raise RuntimeError("The Live session did not pin the expected same-project prompt-agent version.")
    print(f"Foundry owns delegation to prompt agent {owner['agent_name']}, version {owner['agent_version']}.")


def _has_audio_activity(pcm: bytes) -> bool:
    return any(
        abs(int.from_bytes(pcm[index : index + 2], "little", signed=True)) > 256 for index in range(0, len(pcm), 2)
    )


def _checked_event(event: LiveServerEvent) -> Mapping[str, Any]:
    if event.get("type") == "error" and not isinstance(event.get("error"), Mapping):
        raise RuntimeError("Malformed Live session error event.")
    if event.get("type") == "response.event":
        nested = event.get("event")
        if not isinstance(nested, Mapping) or not isinstance(nested.get("type"), str) or not nested["type"]:
            raise RuntimeError("Malformed managed backend response.event.")
        if "response" in nested and not isinstance(nested["response"], Mapping):
            raise RuntimeError("Malformed managed backend response snapshot.")
    nested = check_event(event)
    check_session_open(event)
    return nested


@dataclass
class ManagedReply:
    """Observed backend completion and actual frontend audio are separate conditions."""

    last_activity: float
    delegations: dict[str, bool] = field(default_factory=dict)
    audio_bytes: int = 0
    audio_chunks: int = 0
    input_transcript: str = ""
    output_transcript: str = ""
    _audio_after_delegation: bool = False
    _transcript_after_delegation: bool = False

    def observe(self, event: LiveServerEvent, now: float) -> None:
        nested = _checked_event(event)
        if isinstance(event, models.LiveServerEventLiveDelegationCreated):
            delegation = event.delegation
            if (
                not isinstance(delegation, models.VoiceAgentLiveDelegationItem)
                or delegation.target != "foundry_managed_agent"
                or not delegation.id
            ):
                raise RuntimeError("Expected a Foundry-owned managed-agent delegation, not client-owned work.")
            if delegation.id not in self.delegations:
                self.delegations[delegation.id] = False
                self._audio_after_delegation = False
                self._transcript_after_delegation = False
            self.last_activity = now
            target = getattr(delegation.target, "value", delegation.target)
            print(f"Delegation {delegation.id}: target={target}; Foundry handles the result.")
        elif nested:
            delegation_id = event.get("delegation_id")
            if delegation_id not in self.delegations:
                raise RuntimeError("A backend event was not correlated with an observed managed delegation.")
            if nested["type"] == "response.completed":
                response = nested.get("response")
                if not isinstance(response, Mapping) or response.get("status") != "completed":
                    raise RuntimeError("Malformed managed backend completion: expected status=completed.")
                self.delegations[delegation_id] = True
                print(f"Backend completed delegation {delegation_id}; still waiting for frontend speech.")
            self.last_activity = now
        elif isinstance(event, models.LiveOutputAudioDelta):
            pcm = base64.b64decode(event.delta, validate=True)
            if len(pcm) % 2:
                raise ValueError("The service returned an incomplete PCM16 sample.")
            if self.delegations:
                self.audio_bytes += len(pcm)
                self.audio_chunks += 1
                if _has_audio_activity(pcm):
                    self._audio_after_delegation = True
                    self.last_activity = now
        elif isinstance(event, models.LiveServerEventLiveInputTranscriptDelta):
            self.input_transcript += event.delta
        elif isinstance(event, models.LiveServerEventLiveOutputTranscriptDelta) and self.delegations:
            self.output_transcript += event.delta
            if event.delta.strip():
                self._transcript_after_delegation = True
                self.last_activity = now

    def ready(self, now: float) -> bool:
        return (
            bool(self.delegations)
            and all(self.delegations.values())
            and self._audio_after_delegation
            and self._transcript_after_delegation
            and now - self.last_activity >= OUTPUT_IDLE_SECONDS
        )


def stream_managed_audio(connection: BetaLiveConnection, pcm: bytes) -> ManagedReply:
    """Interleave paced audio sends and bounded receives on the synchronous socket."""
    started = time.monotonic()
    deadline = started + len(pcm) / (2 * SAMPLE_RATE) + RESPONSE_TIMEOUT
    ready_after = None
    next_send = started
    position = 0
    output = ManagedReply(last_activity=started)
    while True:
        remaining_time(deadline, "managed backend completion and nonempty Live audio/transcript")
        now = time.monotonic()
        if ready_after is not None and now >= ready_after and output.ready(now):
            return output
        if now >= next_send:
            chunk = pcm[position : position + CHUNK_BYTES] if position < len(pcm) else _SILENCE
            connection.session.input_audio.append(audio=chunk)
            position = min(position + len(chunk), len(pcm))
            next_send = time.monotonic() + len(chunk) / (2 * SAMPLE_RATE)
            if ready_after is None and position == len(pcm):
                ready_after = next_send + 1.0
        # Silence keeps the Live media clock advancing while Foundry runs the backend.
        timeout = min(remaining_time(deadline, "managed Live events"), max(0.001, next_send - time.monotonic()))
        try:
            event = connection.recv(timeout=timeout)
        except TimeoutError:
            continue
        output.observe(event, time.monotonic())


async def stream_managed_audio_async(connection: AsyncBetaLiveConnection, pcm: bytes) -> ManagedReply:
    """Use the same media clock and completion conditions without blocking the event loop."""
    started = time.monotonic()
    deadline = started + len(pcm) / (2 * SAMPLE_RATE) + RESPONSE_TIMEOUT
    ready_after = None
    next_send = started
    position = 0
    output = ManagedReply(last_activity=started)
    while True:
        remaining_time(deadline, "managed backend completion and nonempty Live audio/transcript")
        now = time.monotonic()
        if ready_after is not None and now >= ready_after and output.ready(now):
            return output
        if now >= next_send:
            chunk = pcm[position : position + CHUNK_BYTES] if position < len(pcm) else _SILENCE
            await asyncio.wait_for(
                connection.session.input_audio.append(audio=chunk),
                timeout=remaining_time(deadline, "managed Live input audio"),
            )
            position = min(position + len(chunk), len(pcm))
            next_send = time.monotonic() + len(chunk) / (2 * SAMPLE_RATE)
            if ready_after is None and position == len(pcm):
                ready_after = next_send + 1.0
        timeout = min(remaining_time(deadline, "managed Live events"), max(0.001, next_send - time.monotonic()))
        try:
            event = await asyncio.wait_for(connection.recv(), timeout=timeout)
        except asyncio.TimeoutError:
            continue
        output.observe(event, time.monotonic())


def print_reply(output: ManagedReply, input_bytes: int) -> None:
    safe_print(f"Input transcript: {output.input_transcript.strip() or '(not emitted by the service)'}")
    safe_print(f"Output transcript: {output.output_transcript.strip()}")
    print(f"Sent {input_bytes} recorded PCM16 bytes, plus paced silence while waiting.")
    print(f"Received {output.audio_bytes} PCM16 bytes in {output.audio_chunks} chunks after managed delegation.")
    print(
        f"Frontend audio and transcript were idle for {OUTPUT_IDLE_SECONDS:g}s. "
        "This is a bounded end-of-reply heuristic, not a playback-complete event; long pauses can cut off speech."
    )
