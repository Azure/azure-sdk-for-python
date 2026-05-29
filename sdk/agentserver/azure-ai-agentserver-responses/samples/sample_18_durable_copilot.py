# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 18 — Durable Copilot (stateful conversation via GitHub Copilot SDK).

Wraps the **GitHub Copilot Python SDK** (``github-copilot-sdk``) in a
steerable durable response handler.  The Copilot SDK is the upstream
framework that owns conversational durability — this handler is the
bridge.

Recovery model:

- The Copilot session id is the framework-computed
  ``context.conversation_chain_id`` — a deterministic, crash-stable
  identifier shared by every turn in the same conversation. No
  per-handler allocation, no metadata round-trip on first use.
  The fresh-entry path uses ``client.create_session(session_id=…)``;
  the recovery and follow-up steerable-turn path uses
  ``client.resume_session(session_id, …)`` — the SDK's documented
  reattach API.
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

Streaming model (live deltas + recovery replay):

- The Copilot SDK emits incremental tokens via
  ``AssistantMessageDeltaData`` events as the model generates the
  response. The handler forwards each event's ``delta_content`` as an
  ``output_text.delta`` SSE event the moment it arrives, so clients see
  characters appear live rather than in one batched dump at the end of
  the turn. ``AssistantMessageData`` (the assembled-final-message event
  delivered once generation completes) is used only as a fallback for
  the rare case the SDK emits the final message without any prior
  deltas.
- On crash recovery, when the handler re-enters with
  ``entry_mode == "recovered"``, it first reads the upstream session's
  persisted assistant content for the current user turn via
  ``session.get_messages()`` and emits the accumulated text as a single
  ``output_text.delta`` event. The recovered client therefore sees:
  ``response.in_progress`` (with zero output items) → one delta with the
  accumulated text → live deltas continuing from where the upstream
  Copilot session is. This is a deliberate simplification — the
  original per-token delta sequence isn't preserved; we collapse the
  pre-crash deltas into a single replay chunk and then resume live
  streaming.

Limitations:

- The Copilot SDK does not checkpoint within an assistant response. If
  Copilot finished a partial reply before the crash, we replay that
  partial text on recovery; whether the upstream session continues to
  emit more deltas after we re-attach depends on the Copilot SDK's
  resume semantics. For workflows where strict per-token continuity
  matters, decompose into smaller queries (see ``sample_19``) or use a
  framework with native node-level checkpointing (see ``sample_21``).
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
from typing import Any

from copilot import CopilotClient  # type: ignore[import-untyped]
from copilot.generated.session_events import (  # type: ignore[import-untyped]
    AssistantMessageData,
    AssistantMessageDeltaData,
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

# Allow operators / tests to pick the Copilot model via env var. Default is
# a small, low-cost model that is generally available; operators with access
# to a specific model can override at deploy time.
_COPILOT_MODEL = os.environ.get("COPILOT_MODEL", "gpt-5-mini")


async def _open_session(
    client: Any,
    session_id: str,
    durability,
) -> Any:
    """Open the Copilot session — ``resume_session`` if it pre-existed.

    On a fresh turn we use ``create_session``; on crash recovery and on every
    subsequent steerable turn we use ``resume_session``, the SDK's explicit
    reattach API. ``durability.is_recovery`` is True only when we are being
    re-entered after a crash; ``durability.entry_mode == "resumed"`` is True
    for steerable follow-up turns. Both routes reattach.

    Both paths pass ``streaming=True`` so the SDK emits
    ``AssistantMessageDeltaData`` events with incremental ``delta_content``
    as the model generates the response — without this the SDK only delivers
    the final ``AssistantMessageData`` event once generation completes, and
    the SSE client sees the whole answer in a single delta dump instead of
    live characters.
    """
    if durability.is_recovery or durability.entry_mode == "resumed":
        return await client.resume_session(
            session_id,
            on_permission_request=PermissionHandler.approve_all,
            model=_COPILOT_MODEL,
            streaming=True,
        )
    return await client.create_session(
        session_id=session_id,
        on_permission_request=PermissionHandler.approve_all,
        model=_COPILOT_MODEL,
        streaming=True,
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


async def _gather_accumulated_assistant_text(
    session: Any, user_input_text: str
) -> str:
    """Return the upstream assistant content already emitted for this turn.

    Used on crash recovery to surface whatever Copilot had already sent
    before the crash as a single replay delta. Looks for the last
    ``UserMessageData`` event whose content matches ``user_input_text``
    and concatenates every ``AssistantMessageData`` event that follows
    it in the session's persisted event log.

    :param session: An open Copilot session (post-``resume_session``).
    :type session: Any
    :param user_input_text: The current turn's user input text.
    :type user_input_text: str
    :returns: Concatenated assistant content, or an empty string if the
        upstream session has not produced any assistant content for
        this turn yet.
    :rtype: str
    """
    try:
        events = await session.get_messages()
    except Exception:  # pylint: disable=broad-exception-caught
        return ""

    # Find the index of the last UserMessageData event whose content
    # matches the current turn's input.
    last_user_index: int | None = None
    for i, ev in enumerate(events):
        data = getattr(ev, "data", None)
        if isinstance(data, UserMessageData):
            content = getattr(data, "content", None)
            if isinstance(content, str) and content == user_input_text:
                last_user_index = i

    if last_user_index is None:
        return ""

    # Concatenate all AssistantMessageData content emitted after that
    # user message.
    parts: list[str] = []
    for ev in events[last_user_index + 1 :]:
        data = getattr(ev, "data", None)
        if isinstance(data, AssistantMessageData):
            content = getattr(data, "content", None)
            if isinstance(content, str):
                parts.append(content)
    return "".join(parts)


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
            session_id = context.conversation_chain_id
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

    session_id = context.conversation_chain_id

    # ── Live delta streaming via asyncio.Queue ──────────────────────
    # Copilot's SDK emits incremental tokens via ``AssistantMessageDeltaData``
    # events as the model generates the response. We push each delta's
    # ``delta_content`` into a queue and forward it as an
    # ``output_text.delta`` SSE event the moment it arrives, so clients
    # see characters appear live rather than in a single batched dump.
    # ``AssistantMessageData`` is the FINAL assembled message (delivered
    # once the response is complete); we ignore it on the delta path —
    # the deltas have already accumulated to the same content — but use
    # it as a fallback if the SDK emits the assembled message WITHOUT
    # prior deltas (older versions / certain Copilot models).
    _IDLE = object()
    delta_queue: asyncio.Queue[Any] = asyncio.Queue()
    _saw_delta = False

    def on_event(event: Any) -> None:
        nonlocal _saw_delta
        data = getattr(event, "data", None)
        if isinstance(data, AssistantMessageDeltaData):
            chunk = getattr(data, "delta_content", None) or ""
            if chunk:
                _saw_delta = True
                delta_queue.put_nowait(chunk)
        elif isinstance(data, AssistantMessageData):
            # Fallback: if the SDK delivered the full message without
            # any prior deltas, forward it as a single delta so the
            # client still receives the content.
            if not _saw_delta:
                content = getattr(data, "content", None) or ""
                if content:
                    delta_queue.put_nowait(content)
        elif isinstance(data, SessionIdleData):
            delta_queue.put_nowait(_IDLE)

    accumulated = ""

    async with CopilotClient() as client:
        # Reattach on recovery (resume_session), create on fresh (create_session).
        async with await _open_session(client, session_id, durability) as session:
            session.on(on_event)

            # ── Recovery replay ─────────────────────────────────────
            # On crash recovery / steerable reattach, the upstream
            # session may already hold some accumulated assistant text
            # for the current user turn (a partial or complete prior
            # response). Emit it as a single delta so the recovered
            # client sees the work that was already done before the
            # crash. Live deltas continue from here.
            if durability.entry_mode in ("recovered", "resumed"):
                user_input_text = await context.get_input_text()
                replay = await _gather_accumulated_assistant_text(
                    session, user_input_text
                )
                if replay:
                    accumulated += replay
                    yield text.emit_delta(replay)

            # Upstream-history-gated send: skipped when Copilot's
            # persisted event log already has our user message as its
            # most recent user event.
            sent_this_attempt = await _send_input_if_not_in_session(session, context)

            # Drain live events. If we sent input this attempt, wait
            # for idle indefinitely (Copilot is generating). If we
            # didn't send (recovery + already-in-session), the upstream
            # session may still emit a few residual events on attach —
            # poll with a short bounded timeout, then exit cleanly.
            wait_timeout = None if sent_this_attempt else 2.0
            while True:
                if cancellation_signal.is_set():
                    await session.abort()
                    break
                try:
                    chunk = await asyncio.wait_for(
                        delta_queue.get(),
                        timeout=wait_timeout,
                    )
                except asyncio.TimeoutError:
                    # No new events within the recovery polling window;
                    # presume the upstream is idle and exit.
                    break
                if chunk is _IDLE:
                    break
                accumulated += chunk
                yield text.emit_delta(chunk)

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
