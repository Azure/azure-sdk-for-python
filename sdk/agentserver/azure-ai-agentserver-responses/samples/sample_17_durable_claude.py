# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 17 — Durable Claude (stateful conversation via Claude Agent SDK).

Wraps the **Claude Agent SDK** (``claude-agent-sdk``) in a steerable
durable response handler.  The Claude SDK is the upstream framework
that owns conversational durability — this handler is the bridge.

Recovery model:

- The Claude session UUID is stamped into ``durability.metadata`` as
  ``claude_session_id`` so each turn (and each recovered attempt within
  a turn) resumes the same session.
- A ``last_processed_input_item_id`` watermark records which user input
  item we most-recently sent to Claude. On a recovered entry, if the
  watermark already points at the current turn's input, we DO NOT call
  ``client.query`` again — that would put a duplicate user message in
  the session JSONL. Instead we just consume ``client.receive_response``.
- On a steered cancellation that fires *before* this handler did any
  work (pre-entry), we still send the user input to Claude so the
  message is preserved in the conversation history — otherwise the
  newer turn that supersedes us would lose context.
- On crash recovery, we never *fork* the Claude session. Forking would
  create a fresh branch and abandon any progress in the original session
  that hadn't yet committed. We simply resume the same session.

Limitations (honest about what crash recovery cannot do for Claude):

- The Claude SDK does not checkpoint within an assistant response.
  If we crash mid-stream, the partial assistant text written so far is
  lost — Claude commits the assistant message to the session JSONL only
  on natural completion of ``receive_response``. On recovery, the
  resumed session sees the user's message but no assistant reply yet.
  Whether ``receive_response`` then returns continuation, returns an
  empty stream, or errors is upstream-SDK-defined and not verified
  here. For workflows where within-turn progress matters, decompose
  the work into multiple smaller queries (see ``sample_19`` for the
  per-phase pattern) or use a framework with native node-level
  checkpointing (see ``sample_21``).

Requirements::

    pip install claude-agent-sdk
    # Node.js available on PATH (the Claude Code CLI is a bundled JS binary).

Usage::

    export ANTHROPIC_API_KEY="sk-ant-..."
    python sample_17_durable_claude.py

    curl -N -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "claude", "input": "Explain quantum entanglement",
             "stream": true, "store": true, "background": true}'

    # Steer with a follow-up
    curl -N -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "claude", "input": "Now explain it for a 5-year-old",
             "stream": true, "store": true, "background": true,
             "previous_response_id": "<id>"}'

    # Simulate mid-stream shutdown
    SIMULATE_SHUTDOWN_MS=1500 python sample_17_durable_claude.py
"""

import asyncio
import os
import uuid

from claude_agent_sdk import (  # type: ignore[import-untyped]
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
)

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


def _claude_options_for(durability) -> ClaudeAgentOptions:
    """Build SDK options that resume the existing session or open a new one."""
    existing = durability.metadata.get("claude_session_id")
    if existing:
        return ClaudeAgentOptions(resume=existing)
    new_id = str(uuid.uuid4())
    durability.metadata["claude_session_id"] = new_id
    return ClaudeAgentOptions(session_id=new_id)


async def _send_input_if_unprocessed(
    client: ClaudeSDKClient,
    context: ResponseContext,
    durability,
) -> None:
    """Send this turn's input to Claude unless we already did on a prior attempt.

    Uses ``last_processed_input_item_id`` as the watermark. Updates the
    watermark BEFORE the streaming receive loop so a crash inside the
    receive loop doesn't cause a re-send on the next attempt.
    """
    input_items = await context.get_input_items()
    last_input_item_id = getattr(input_items[-1], "id", None) if input_items else None
    if last_input_item_id is None:
        return
    if durability.metadata.get("last_processed_input_item_id") == last_input_item_id:
        return  # already sent on a prior attempt; let receive_response handle it

    input_text = await context.get_input_text()
    await client.query(input_text)
    durability.metadata["last_processed_input_item_id"] = last_input_item_id


def _build_resumption_response(
    context: ResponseContext, request: CreateResponse
) -> ResponseObject:
    """Empty resumption response.

    Partial token output from a crashed mid-stream attempt cannot be
    byte-matched against a non-deterministic LLM's re-attempt, so we
    discard it and let the client redraw on the reset ``response.in_progress``.
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
    """Steerable Claude Agent SDK conversation."""
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
    # On a STEERED pre-entry we still send the user's input to Claude so
    # the message is preserved in the conversation history — otherwise
    # the newer turn that superseded us would lose context for what the
    # user said. For other cancellation reasons (client cancel, shutdown)
    # we just return; no input preservation is appropriate.
    if cancellation_signal.is_set():
        if context.cancellation_reason == CancellationReason.STEERED:
            sdk_options = _claude_options_for(durability)
            async with ClaudeSDKClient(options=sdk_options) as client:
                await _send_input_if_unprocessed(client, context, durability)
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

    sdk_options = _claude_options_for(durability)
    accumulated = ""

    async with ClaudeSDKClient(options=sdk_options) as client:
        # Watermarked send — skipped on recovery if input was already sent.
        await _send_input_if_unprocessed(client, context, durability)

        async def _watch_cancel() -> None:
            await cancellation_signal.wait()
            await client.interrupt()

        cancel_watcher = asyncio.create_task(_watch_cancel())
        try:
            async for msg in client.receive_response():
                if cancellation_signal.is_set():
                    break
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            accumulated += block.text
                            yield text.emit_delta(block.text)
                elif isinstance(msg, ResultMessage):
                    sdk_session_id = getattr(msg, "session_id", None)
                    if isinstance(sdk_session_id, str) and sdk_session_id:
                        durability.metadata["claude_session_id"] = sdk_session_id
        finally:
            if not cancel_watcher.done():
                cancel_watcher.cancel()

    # Always close builders so the persisted event stream is well-formed.
    yield text.emit_text_done(accumulated.strip())
    yield text.emit_done()
    yield message.emit_done()

    if shutdown_timer and not shutdown_timer.done():
        shutdown_timer.cancel()

    # Mid-stream shutdown: return without terminal so the framework
    # re-invokes us; the recovery branch above resumes the same session
    # and skips re-sending the input via the watermark.
    if context.cancellation_reason == CancellationReason.SHUTTING_DOWN:
        return

    yield stream.emit_completed()


async def _simulate_shutdown(cancellation_signal: asyncio.Event, context: ResponseContext) -> None:
    """Fire a SHUTTING_DOWN signal after a delay (local testing only)."""
    await asyncio.sleep(_SIMULATE_SHUTDOWN_MS / 1000.0)
    if not cancellation_signal.is_set():
        context.cancellation_reason = CancellationReason.SHUTTING_DOWN
        cancellation_signal.set()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
