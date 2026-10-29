# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared lifecycle and event helpers for the GPT Live samples in this folder."""

from __future__ import annotations

import asyncio
from contextlib import contextmanager, suppress
import os
from pathlib import Path
import sys
import time
from typing import Any, BinaryIO, Iterator, Mapping, Optional, Sequence, TYPE_CHECKING
from uuid import uuid4

from azure.ai.projects import models

if TYPE_CHECKING:
    from azure.ai.projects.operations import BetaLiveConnection, LiveServerEvent
    from azure.ai.projects.aio.operations import AsyncBetaLiveConnection


RESPONSE_TIMEOUT = 60.0
CLOSE_TIMEOUT = 10.0


def sample_agent_name(scenario: str) -> str:
    """Choose a unique agent name so cleanup affects only this run."""
    prefix = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or f"sample-live-{scenario}"
    return f"{prefix}-{uuid4().hex[:8]}"


def text_conversation_prompts(prompts: Optional[Sequence[str]]) -> list[str]:
    """Use one default message, or validate the supplied list of messages."""
    if prompts is None:
        return ["Why is Seattle known for rain? Answer in one short sentence."]
    if isinstance(prompts, str):
        raise ValueError("Pass prompts as a sequence of strings, not one string.")
    result = list(prompts)
    if not result or any(not isinstance(prompt, str) or not prompt.strip() for prompt in result):
        raise ValueError("Provide at least one nonblank text prompt.")
    return result


def audio_settings() -> models.LiveInitialSessionAudioParam:
    """Use the same PCM16, mono, 24 kHz format in both directions."""
    return models.LiveInitialSessionAudioParam(
        format=models.LiveSessionAudioFormatPCMParam(rate=24000),
        output=models.LiveInitialSessionAudioOutputParam(voice="marin"),
    )


def safe_print(text: str, *, end: str = "\n") -> None:
    """Display model text even on a console with a legacy encoding."""
    encoding = sys.stdout.encoding or "utf-8"
    print(text.encode(encoding, errors="replace").decode(encoding), end=end, flush=True)


@contextmanager
def recording_output(path: Path) -> Iterator[BinaryIO]:
    """Save a recording without overwriting a file; remove failed or empty downloads.

    :param path: Explicit destination that must not already exist.
    :type path: pathlib.Path
    :return: A writable binary stream for the downloaded audio.
    :rtype: ~typing.Iterator[~typing.BinaryIO]
    """
    output = path.open("xb")
    completed = False
    try:
        with output:
            yield output
            if output.tell() == 0:
                raise RuntimeError("The audio download returned no bytes.")
        completed = True
    finally:
        if not completed:
            path.unlink()
    print(f"Saved recording: {path}")


def remaining_time(deadline: float, operation: str) -> float:
    """Return the time left, or raise when the deadline expires."""
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError(f"Timed out waiting for {operation}.")
    return remaining


def check_event(event: LiveServerEvent) -> Mapping[str, Any]:
    """Raise service errors and read events from the Responses backend."""
    if event.get("type") == "error":
        error = event.get("error") or {}
        raise RuntimeError(f"Live session error: {error.get('code')}: {error.get('message')}")

    if isinstance(event, models.LiveServerEventLiveResponseEvent):
        nested: Mapping[str, Any] = event.event
    elif event.get("type") == "response.event":
        nested = event["event"]
    else:
        return {}

    response = nested.get("response") or {}
    status = response.get("status")
    if nested.get("type") in ("error", "response.failed", "response.incomplete", "response.cancelled") or status in (
        "failed",
        "incomplete",
        "cancelled",
    ):
        detail = nested.get("error") or response.get("error") or response.get("incomplete_details")
        raise RuntimeError(f"Responses backend {nested.get('type')}: {detail or status or 'unknown error'}")
    return nested


def check_session_open(event: LiveServerEvent) -> None:
    """Raise if the session closes before the requested work finishes."""
    if event.get("type") == "session.closed":
        raise RuntimeError(f"Live session closed before the workflow completed: {event.get('reason')}")


def wait_for_event(
    connection: BetaLiveConnection, event_type: str, timeout: float = RESPONSE_TIMEOUT
) -> LiveServerEvent:
    """Wait for a specific event, with a timeout."""
    deadline = time.monotonic() + timeout
    while True:
        try:
            event = connection.recv(timeout=remaining_time(deadline, event_type))
        except TimeoutError as exc:
            raise TimeoutError(f"Timed out waiting for {event_type}.") from exc
        check_event(event)
        if event.get("type") == event_type:
            return event
        check_session_open(event)


async def wait_for_event_async(
    connection: AsyncBetaLiveConnection, event_type: str, timeout: float = RESPONSE_TIMEOUT
) -> LiveServerEvent:
    """Wait asynchronously for a specific event, with a timeout."""
    deadline = time.monotonic() + timeout
    while True:
        try:
            remaining = remaining_time(deadline, event_type)
            event = await asyncio.wait_for(connection.recv(), timeout=remaining)
        except (asyncio.TimeoutError, TimeoutError) as exc:
            raise TimeoutError(f"Timed out waiting for {event_type}.") from exc
        check_event(event)
        if event.get("type") == event_type:
            return event
        check_session_open(event)


def close_session(connection: BetaLiveConnection) -> None:
    """Close the session without hiding an error already being handled."""
    if sys.exc_info()[0] is not None:
        with suppress(Exception):
            connection.session.close()
        return
    connection.session.close()
    event = wait_for_event(connection, "session.closed", timeout=CLOSE_TIMEOUT)
    if event.get("reason") != "close_requested":
        raise RuntimeError(f"Live session did not close normally: {event.get('reason')}")
    print("Session closed: close_requested")


async def close_session_async(connection: AsyncBetaLiveConnection) -> None:
    """End the session before closing its WebSocket."""
    if sys.exc_info()[0] is not None:
        with suppress(Exception):
            await asyncio.wait_for(connection.session.close(), timeout=CLOSE_TIMEOUT)
        return
    deadline = time.monotonic() + CLOSE_TIMEOUT
    try:
        remaining = remaining_time(deadline, "session.close")
        await asyncio.wait_for(connection.session.close(), timeout=remaining)
        event = await wait_for_event_async(
            connection, "session.closed", timeout=remaining_time(deadline, "session.closed")
        )
    except (asyncio.TimeoutError, TimeoutError) as exc:
        raise TimeoutError("Timed out closing the GPT Live session.") from exc
    if event.get("reason") != "close_requested":
        raise RuntimeError(f"Live session did not close normally: {event.get('reason')}")
    print("Session closed: close_requested")


def _collect_response_event(
    event: LiveServerEvent,
    text_parts: dict[tuple[str, int], str],
    calls: dict[str, Mapping[str, Any]],
) -> bool:
    nested = check_event(event)
    check_session_open(event)
    event_type = nested.get("type")
    if event_type in ("response.output_text.delta", "response.output_text.done"):
        key = (nested["item_id"], nested["content_index"])
        if event_type == "response.output_text.delta":
            text_parts[key] = text_parts.get(key, "") + nested["delta"]
        else:
            text_parts[key] = nested["text"]
    elif event_type == "response.output_item.done":
        item = nested["item"]
        if item.get("type") == "function_call":
            # Argument events identify item_id; the complete item supplies the tool-result call_id.
            call_id = item.get("call_id")
            if not isinstance(call_id, str) or not call_id:
                raise RuntimeError("The completed Responses function_call item omitted a usable call_id.")
            calls[call_id] = item
    return event_type == "response.completed"


def receive_response(
    connection: BetaLiveConnection, timeout: float = RESPONSE_TIMEOUT
) -> tuple[str, list[Mapping[str, Any]]]:
    """Wait for a backend reply and return its text and completed tool calls."""
    deadline = time.monotonic() + timeout
    text_parts: dict[tuple[str, int], str] = {}
    calls: dict[str, Mapping[str, Any]] = {}
    while True:
        try:
            event = connection.recv(timeout=remaining_time(deadline, "the Responses backend"))
        except TimeoutError as exc:
            raise TimeoutError("Timed out waiting for the Responses backend to complete.") from exc
        if _collect_response_event(event, text_parts, calls):
            # Text and tool results arrive before response.completed.
            return "".join(text_parts.values()).strip(), list(calls.values())


async def receive_response_async(
    connection: AsyncBetaLiveConnection, timeout: float = RESPONSE_TIMEOUT
) -> tuple[str, list[Mapping[str, Any]]]:
    """Wait asynchronously for a backend reply and its completed tool calls."""
    deadline = time.monotonic() + timeout
    text_parts: dict[tuple[str, int], str] = {}
    calls: dict[str, Mapping[str, Any]] = {}
    while True:
        try:
            remaining = remaining_time(deadline, "the Responses backend")
            event = await asyncio.wait_for(connection.recv(), timeout=remaining)
        except (asyncio.TimeoutError, TimeoutError) as exc:
            raise TimeoutError("Timed out waiting for the Responses backend to complete.") from exc
        if _collect_response_event(event, text_parts, calls):
            return "".join(text_parts.values()).strip(), list(calls.values())
