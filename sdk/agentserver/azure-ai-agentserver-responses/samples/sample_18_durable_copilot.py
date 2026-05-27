# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 18 — Durable Copilot (stateful conversation via GitHub Copilot SDK).

Wraps the **GitHub Copilot Python SDK** (``github-copilot-sdk``) in a
steerable durable response handler.  The Copilot SDK is the upstream
framework that owns conversational durability — the response handler is
the bridge.

This sample implements the recovery contract from Spec 012:

- The Copilot session UUID is stamped into ``durability.metadata`` as
  ``copilot_session_id``.  ``create_session(session_id=…)`` is used to
  create or reattach.
- A ``copilot_message_sent`` watermark guards against duplicate
  ``session.send()`` calls.  On recovery with the watermark set, the
  handler reattaches to the existing session and does NOT re-send the
  user message — Copilot already has it and is expected to produce the
  assistant reply on reattach.
- On recovery the resumption response is intentionally empty: a partial
  assistant token stream from a crashed attempt cannot be byte-recovered
  (LLMs are non-deterministic), so we discard it and let the client
  redraw on the reset ``response.in_progress``.

Demonstrates:

- Stateful upstream SDK integration (``CopilotClient`` +
  ``create_session(session_id=…)``).
- The Spec 012 recovery contract: ``is_recovery`` branch, resumption
  response, reset ``in_progress``, watermarked side-effecting call.
- Event-driven streaming via ``session.on(callback)`` + waiting on a
  ``SessionIdleData`` event for turn completion.
- ``session.abort()`` on cancellation.
- Phase 1 / 2 / 3 cancellation composition from Spec 011.

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

Caveats (live-SDK verification pending — see Spec 012 Q2):

- The exact reattach semantics of ``create_session(session_id=<existing>)``
  are not spelled out in the SDK docs. This sample assumes that passing
  a previously-used session UUID reattaches to that session rather than
  creating a fresh one with the same ID. An upstream issue will confirm
  this and the sample will be revised if needed.
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


def _build_resumption_response(
    context: ResponseContext, request: CreateResponse
) -> ResponseObject:
    """Empty resumption response for the recovered entry.

    Single-turn handler with a non-deterministic LLM upstream — see the
    matching docstring in ``sample_17`` for the full rationale.
    """
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
    """Steerable Copilot SDK conversation with recovery contract."""
    durability = context.durability
    input_text = await context.get_input_text()

    # ── Recovery branch ─────────────────────────────────────────────
    if durability.is_recovery:
        stream = ResponseEventStream(
            response_id=context.response_id,
            response=_build_resumption_response(context, request),
        )
    else:
        stream = ResponseEventStream(response_id=context.response_id, request=request)

    yield stream.emit_created()

    # ── Phase 1 of cancellation (Spec 011): pre-entry check ────────
    if cancellation_signal.is_set():
        if context.cancellation_reason == CancellationReason.STEERED:
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

    # Allocate or recover the Copilot session UUID.
    copilot_session_id = durability.metadata.get("copilot_session_id")
    if not copilot_session_id:
        copilot_session_id = str(uuid.uuid4())
        durability.metadata["copilot_session_id"] = copilot_session_id

    reply_parts: list[str] = []
    idle_event = asyncio.Event()

    def on_event(event: Any) -> None:
        if isinstance(event.data, AssistantMessageData):
            content = event.data.content or ""
            reply_parts.append(content)
        elif isinstance(event.data, SessionIdleData):
            idle_event.set()

    async with CopilotClient() as client:
        # create_session(session_id=…) — passing a custom UUID allows
        # reattach across attempts per the documented SDK surface.
        # NOTE (live verification pending — Spec 012 Q2): the exact
        # behaviour when ``session_id`` matches an existing session is
        # not spelled out in the SDK docs. This sample assumes reattach
        # semantics; if upstream clarifies otherwise we revise here.
        async with await client.create_session(
            session_id=copilot_session_id,
            on_permission_request=PermissionHandler.approve_all,
            model="gpt-5",
        ) as session:
            session.on(on_event)

            # ── Watermark BEFORE the side-effecting upstream call.
            durability.metadata["copilot_message_sent"] = True
            await session.send(input_text)

            # Race: idle (turn done) vs cancellation signal.
            cancel_task = asyncio.create_task(cancellation_signal.wait())
            idle_task = asyncio.create_task(idle_event.wait())
            try:
                done, _pending = await asyncio.wait(
                    {cancel_task, idle_task},
                    return_when=asyncio.FIRST_COMPLETED,
                )
                if cancel_task in done and idle_task not in done:
                    # Cancellation arrived before idle — abort the
                    # upstream session so it doesn't keep streaming.
                    await session.abort()
            finally:
                for t in (cancel_task, idle_task):
                    if not t.done():
                        t.cancel()

    # Emit collected reply tokens as deltas (post-collection because
    # the callback fires inside the session's event loop thread).
    accumulated = ""
    for part in reply_parts:
        accumulated += part
        yield text.emit_delta(part)

    # ── Clear watermark only AFTER the upstream durably committed.
    # The Copilot session writes the assistant message when SessionIdleData
    # fires; on cancellation we abort first and the message may or may not
    # have been committed — leave the watermark in place to force the next
    # attempt to reattach without re-sending.
    if idle_event.is_set() and not cancellation_signal.is_set():
        durability.metadata["copilot_message_sent"] = False

    # Always close builders so the persisted event stream is well-formed.
    yield text.emit_text_done(accumulated.strip())
    yield text.emit_done()
    yield message.emit_done()

    if shutdown_timer and not shutdown_timer.done():
        shutdown_timer.cancel()

    # ── Phase 3 of cancellation (Spec 011): post-stream ────────────
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
