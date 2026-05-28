# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 18 — Durable Copilot (stateful conversation via GitHub Copilot SDK).

Wraps the **GitHub Copilot Python SDK** (``github-copilot-sdk``) in a
steerable durable response handler.  The Copilot SDK is the upstream
framework that owns conversational durability — this handler is the
bridge.

Recovery model:

- The Copilot session UUID is stamped into ``durability.metadata`` as
  ``copilot_session_id``. The fresh-entry path uses
  ``client.create_session(session_id=…)``; the recovery and follow-up
  steerable-turn path uses ``client.resume_session(session_id, …)`` —
  the SDK's documented reattach API.
- Before sending the user's input, the handler reads the session's
  persisted event history via ``session.get_messages()``, scans for
  ``UserMessageData`` events, and skips ``session.send`` if the most
  recent user message's content equals this turn's input. The
  **upstream session event log is the source of truth** for "did I
  already send this turn". No handler-managed metadata watermark, no
  metadata flush ordering, no race between persistence and side effect.
- On a steered cancellation that fires pre-entry, we still send the
  user input to Copilot so the message is preserved in the
  conversation history — otherwise the newer turn that supersedes us
  would lose context.
- On crash recovery, we never start a fresh session. Recovery always
  reattaches via ``resume_session``.

Limitations:

- Like Claude, the Copilot SDK does not checkpoint within an assistant
  response. If we crash mid-stream the partial reply written so far is
  lost. For workflows where within-turn progress matters, decompose
  into smaller queries (see ``sample_19``) or use a framework with
  native node-level checkpointing (see ``sample_21``).
- If a prior turn's user input was identical to this turn's input AND
  that prior turn completed normally, the "last user matches input"
  heuristic will incorrectly skip the send. Rare in normal use; for
  workflows where this matters, decompose or disambiguate at the
  application level.

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
    UserMessageData,
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


async def _open_session(
    client: Any,
    session_id: str,
    durability,
) -> Any:
    """Open the Copilot session — ``resume_session`` if it pre-existed.

    On a fresh-allocated session id we use ``create_session``. On any
    subsequent attempt (including recovery and steerable follow-up turns)
    we use ``resume_session``, the SDK's explicit reattach API. The
    sentinel for "pre-existed" is whether the id existed in metadata
    when this attempt started — if it did, we are reattaching.
    """
    # If this attempt allocated the id (i.e. it wasn't in metadata before
    # ``_ensure_copilot_session_id`` ran), use create_session. Otherwise,
    # resume_session. We detect this by storing a "newly allocated" marker
    # transiently in metadata. Simpler check: if the id appears in the
    # in-memory metadata AND we already allocated it on a prior attempt,
    # there will have been a lifecycle-flush — recovery enters with the
    # id already persisted. So: durability.is_recovery == True implies
    # reattach; otherwise we just created it this attempt.
    if durability.is_recovery:
        return await client.resume_session(
            session_id,
            on_permission_request=PermissionHandler.approve_all,
            model="gpt-5",
        )
    return await client.create_session(
        session_id=session_id,
        on_permission_request=PermissionHandler.approve_all,
        model="gpt-5",
    )


async def _send_input_if_not_in_session(
    session: Any,
    context: ResponseContext,
) -> bool:
    """Send this turn's input to Copilot unless it is already in the session.

    Returns True if a send happened on this call; False otherwise.

    Detection rule: list the session's persisted event history via
    ``session.get_messages()``, scan for ``UserMessageData`` payloads,
    and skip the send if the most recent user message's content equals
    this turn's input. The upstream session is the source of truth —
    no handler-managed watermark, no metadata flush ordering.

    See ``sample_17``'s ``_send_input_if_not_in_session`` docstring for
    the full discussion of why this is deterministic for the realistic
    crash window and what the (rare) "user repeats themselves" edge
    case looks like.
    """
    input_text = await context.get_input_text()

    try:
        events = await session.get_messages()
    except Exception:  # pylint: disable=broad-exception-caught
        events = []

    # Find the most recent user-message event.
    last_user_text: str | None = None
    for ev in reversed(events):
        data = getattr(ev, "data", None)
        if isinstance(data, UserMessageData):
            content = getattr(data, "content", None)
            if isinstance(content, str):
                last_user_text = content
            break

    if last_user_text == input_text:
        return False  # already in the session — skip

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
                async with await _open_session(client, session_id, durability) as session:
                    await _send_input_if_not_in_session(session, context)
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
        # Reattach on recovery (resume_session), create on fresh (create_session).
        async with await _open_session(client, session_id, durability) as session:
            session.on(on_event)

            # Upstream-history-gated send: skipped when Copilot's persisted
            # event log already has our user message as its most recent user event.
            sent_this_attempt = await _send_input_if_not_in_session(session, context)

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
    # re-invokes us; the recovery branch reattaches the same session via
    # resume_session and the upstream-history check prevents re-sending.
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
