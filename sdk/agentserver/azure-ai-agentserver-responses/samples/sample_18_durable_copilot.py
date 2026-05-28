# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 18 — Durable Copilot (stateful conversation via GitHub Copilot SDK).

Wraps the **GitHub Copilot Python SDK** (``github-copilot-sdk``) in a
steerable durable response handler.  The Copilot SDK is the upstream
framework that owns conversational durability — this handler is the
bridge.

Recovery model:

- The Copilot session UUID is stamped into ``durability.metadata`` as
  ``copilot_session_id`` so each turn (and each recovered attempt
  within a turn) reattaches to the same session via
  ``client.create_session(session_id=…)``.
- A ``last_processed_input_item_id`` watermark records which user input
  item we most-recently sent to Copilot. On a recovered entry, if the
  watermark already points at the current turn's input, we DO NOT call
  ``session.send`` again — that would put a duplicate user message in
  Copilot's session history.
- On a steered cancellation that fires pre-entry, we still send the
  user input to Copilot so the message is preserved in the conversation
  history — otherwise the newer turn that supersedes us would lose
  context.
- On crash recovery, we never start a fresh session. Recovery always
  reattaches to the existing session.

Limitations (honest about what crash recovery cannot do for Copilot):

- Like Claude, the Copilot SDK does not checkpoint within an assistant
  response. If we crash mid-stream, the partial reply written so far is
  lost. For workflows where within-turn progress matters, decompose
  into smaller queries (see ``sample_19``) or use a framework with
  native node-level checkpointing (see ``sample_21``).
- The exact behaviour of ``create_session(session_id=<existing>)`` is
  not spelled out in the SDK docs. This sample assumes reattach. An
  upstream issue will confirm; the sample may need revision.

Requirements::

    pip install github-copilot-sdk
    # GitHub Copilot CLI installed and authenticated.

Usage::

    python sample_18_durable_copilot.py

    curl -N -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "copilot", "input": "Write a Python fibonacci function",
             "stream": true, "store": true, "background": true}'

    # Steer with a follow-up
    curl -N -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "copilot", "input": "Make it iterative instead",
             "stream": true, "store": true, "background": true,
             "previous_response_id": "<id>"}'

    # Simulate mid-stream shutdown
    SIMULATE_SHUTDOWN_MS=1500 python sample_18_durable_copilot.py
"""

import asyncio
import os
import uuid
from typing import Any

from copilot import CopilotClient  # type: ignore[import-untyped]
from copilot.generated.session_events import (  # type: ignore[import-untyped]
    AssistantMessageData,
    SessionIdleData,
)
from copilot.session import PermissionHandler  # type: ignore[import-untyped]

from azure.ai.agentserver.responses import (
    CancellationReason,
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)
from azure.ai.agentserver.responses.models._generated import ResponseObject

options = ResponsesServerOptions(
    durable_background=True,
    steerable_conversations=True,
)
app = ResponsesAgentServerHost(options=options)

_SIMULATE_SHUTDOWN_MS = int(os.environ.get("SIMULATE_SHUTDOWN_MS", "0"))


def _ensure_copilot_session_id(durability) -> str:
    """Return the persistent Copilot session UUID, allocating on first use."""
    existing = durability.metadata.get("copilot_session_id")
    if existing:
        return existing
    new_id = str(uuid.uuid4())
    durability.metadata["copilot_session_id"] = new_id
    return new_id


async def _send_input_if_unprocessed(
    session: Any,
    context: ResponseContext,
    durability,
) -> bool:
    """Send the user's input to Copilot unless we already did on a prior attempt.

    Returns True if a send happened on this call; False otherwise.

    Uses ``last_processed_input_item_id`` as the watermark. The watermark
    is written AND explicitly flushed BEFORE the upstream ``session.send``
    so a crash between flush and send still recovers cleanly: the
    recovered attempt sees the persisted watermark and skips re-sending.
    The trade-off is that a crash in this tiny window will leave Copilot
    without this turn's user message, but that is preferable to silently
    duplicating the user message in session history on recovery.

    Without the explicit ``flush()`` the watermark write only reaches the
    task store at the next 5-second auto-flush or the next lifecycle
    transition — a crash within that window would lose the watermark and
    cause the recovered attempt to issue ``session.send`` a second time.
    """
    input_items = await context.get_input_items()
    last_input_item_id = getattr(input_items[-1], "id", None) if input_items else None
    if last_input_item_id is None:
        return False
    if durability.metadata.get("last_processed_input_item_id") == last_input_item_id:
        return False

    input_text = await context.get_input_text()
    durability.metadata["last_processed_input_item_id"] = last_input_item_id
    await durability.metadata.flush()
    await session.send(input_text)
    return True


def _build_resumption_response(
    context: ResponseContext, request: CreateResponse
) -> ResponseObject:
    """Empty resumption response — see ``sample_17`` for full rationale."""
    return ResponseObject(
        {
            "id": context.response_id,
            "object": "response",
            "status": "in_progress",
            "output": [],
            "model": request.model,
        }
    )


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Steerable Copilot SDK conversation."""
    durability = context.durability

    # ── Recovery branch ─────────────────────────────────────────────
    if durability.is_recovery:
        stream = ResponseEventStream(
            response_id=context.response_id,
            response=_build_resumption_response(context, request),
        )
    else:
        stream = ResponseEventStream(response_id=context.response_id, request=request)

    yield stream.emit_created()

    # ── Pre-entry cancellation check ───────────────────────────────
    # On a STEERED pre-entry we still send the user's input to Copilot so
    # it is preserved in conversation history. For other cancellation
    # reasons we just return without touching the SDK.
    if cancellation_signal.is_set():
        if context.cancellation_reason == CancellationReason.STEERED:
            session_id = _ensure_copilot_session_id(durability)
            async with CopilotClient() as client:
                async with await client.create_session(
                    session_id=session_id,
                    on_permission_request=PermissionHandler.approve_all,
                    model="gpt-5",
                ) as session:
                    await _send_input_if_unprocessed(session, context, durability)
            yield stream.emit_completed()
        return

    yield stream.emit_in_progress()

    shutdown_timer: asyncio.Task | None = None
    if _SIMULATE_SHUTDOWN_MS > 0:
        shutdown_timer = asyncio.create_task(_simulate_shutdown(cancellation_signal, context))

    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()

    session_id = _ensure_copilot_session_id(durability)
    reply_parts: list[str] = []
    idle_event = asyncio.Event()

    def on_event(event: Any) -> None:
        if isinstance(event.data, AssistantMessageData):
            content = event.data.content or ""
            reply_parts.append(content)
        elif isinstance(event.data, SessionIdleData):
            idle_event.set()

    async with CopilotClient() as client:
        # Reattach to (or create) the named session. Reattach semantics
        # are upstream-SDK-defined; see the docstring caveat.
        async with await client.create_session(
            session_id=session_id,
            on_permission_request=PermissionHandler.approve_all,
            model="gpt-5",
        ) as session:
            session.on(on_event)

            # Watermark-gated send — skipped on recovery if input was
            # already delivered to Copilot.
            sent_this_attempt = await _send_input_if_unprocessed(session, context, durability)

            # Only wait for idle if we actually sent something this attempt.
            # On recovery-skip we have nothing to wait for; the session
            # reattach has already given us whatever events the SDK
            # chose to deliver synchronously.
            if sent_this_attempt:
                cancel_task = asyncio.create_task(cancellation_signal.wait())
                idle_task = asyncio.create_task(idle_event.wait())
                try:
                    done, _pending = await asyncio.wait(
                        {cancel_task, idle_task},
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    if cancel_task in done and idle_task not in done:
                        await session.abort()
                finally:
                    for t in (cancel_task, idle_task):
                        if not t.done():
                            t.cancel()

    accumulated = ""
    for part in reply_parts:
        accumulated += part
        yield text.emit_delta(part)

    yield text.emit_text_done(accumulated.strip())
    yield text.emit_done()
    yield message.emit_done()

    if shutdown_timer and not shutdown_timer.done():
        shutdown_timer.cancel()

    # Mid-stream shutdown: return without terminal so the framework
    # re-invokes us; the recovery branch reattaches the same session
    # and the watermark prevents re-sending the input.
    if context.cancellation_reason == CancellationReason.SHUTTING_DOWN:
        return

    yield stream.emit_completed()


async def _simulate_shutdown(cancellation_signal: asyncio.Event, context: ResponseContext) -> None:
    """Fire SHUTTING_DOWN after a delay (local testing only)."""
    await asyncio.sleep(_SIMULATE_SHUTDOWN_MS / 1000.0)
    if not cancellation_signal.is_set():
        context.cancellation_reason = CancellationReason.SHUTTING_DOWN
        cancellation_signal.set()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()

import asyncio
