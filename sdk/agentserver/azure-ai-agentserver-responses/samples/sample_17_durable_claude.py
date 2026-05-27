# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 17 — Durable Claude (steerable stateful conversation via Claude Agent SDK).

Wraps the **Claude Agent SDK** (``claude-agent-sdk``) in a steerable durable
response handler.  The SDK is stateful: pass ``session_id`` on the first turn
and ``resume`` on subsequent turns so Claude retains the full conversation
history without any external store.

Demonstrates:
- Claude Agent SDK integration (``ClaudeSDKClient`` + ``ClaudeAgentOptions``)
- Stateful session via ``session_id`` / ``resume`` (no manual history store)
- ``steerable_conversations=True`` for multi-turn steering
- Three-phase cancellation pattern (pre-entry / mid-stream / post-stream)
- Mid-stream interrupt via ``client.interrupt()``
- Shutdown recovery: return without terminal event → framework re-invokes
  on restart; Claude session resumes from where it left off.
- Simulating shutdown locally for testing

Requirements::

    pip install claude-agent-sdk

Usage::

    export ANTHROPIC_API_KEY="sk-ant-..."
    python sample_17_durable_claude.py

    # Turn 1
    curl -N -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "claude", "input": "Explain quantum entanglement", "stream": true, "store": true, "background": true}'

    # Steer (turn 2 supersedes turn 1)
    curl -N -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "claude", "input": "Actually explain it for a 5-year-old", "stream": true, "store": true, "background": true, "previous_response_id": "<id>"}'

    # Simulate shutdown (set SIMULATE_SHUTDOWN_MS=2000 to trigger after 2s)
    SIMULATE_SHUTDOWN_MS=2000 python sample_17_durable_claude.py
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
    """Build SDK options for this attempt.

    - Fresh session, never seen: ``session_id=<new uuid>``.
    - Returning to an existing session, no in-flight query: ``resume=…``.
    - Recovery with a known in-flight query: ``resume=…, fork_session=True``
      branches from the prior state so the dangling user message in the
      original session is left alone and our turn moves forward in a
      clean fork.
    """
    existing = durability.metadata.get("claude_session_id")
    in_flight = bool(durability.metadata.get("claude_query_in_flight"))

    if existing and in_flight and durability.is_recovery:
        return ClaudeAgentOptions(resume=existing, fork_session=True)
    if existing:
        return ClaudeAgentOptions(resume=existing)
    new_id = str(uuid.uuid4())
    durability.metadata["claude_session_id"] = new_id
    return ClaudeAgentOptions(session_id=new_id)


def _build_resumption_response(
    context: ResponseContext, request: CreateResponse
) -> ResponseObject:
    """Empty resumption response for the recovered entry.

    Partial token output from a crashed mid-stream attempt cannot be
    byte-matched against a re-attempted stream of a non-deterministic
    LLM, so we discard the partial item and let the client redraw on
    the reset ``response.in_progress``. The fresh stream we produce
    below replaces it.
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
    """Steerable Claude Agent SDK conversation with recovery contract."""
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

    sdk_options = _claude_options_for(durability)
    accumulated = ""

    async with ClaudeSDKClient(options=sdk_options) as client:
        # ── Watermark BEFORE the side-effecting upstream call (Spec 012 FR-014).
        # On recovery the fork above gives us a clean session, so it is
        # safe to re-issue query() — the dangling user message stays in
        # the original (non-fork) session and is no longer ours.
        durability.metadata["claude_query_in_flight"] = True
        await client.query(input_text)

        # Background task: wire cancellation_signal -> client.interrupt().
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
                    # Capture the (possibly forked) session_id so the
                    # next turn / recovery resumes the right one.
                    sdk_session_id = getattr(msg, "session_id", None)
                    if isinstance(sdk_session_id, str) and sdk_session_id:
                        durability.metadata["claude_session_id"] = sdk_session_id
        finally:
            if not cancel_watcher.done():
                cancel_watcher.cancel()

    # ── Clear watermark only AFTER the upstream durably committed.
    # The Claude SDK writes the completed assistant message to the
    # session JSONL when receive_response() ends naturally.
    if not cancellation_signal.is_set():
        durability.metadata["claude_query_in_flight"] = False

    # Always close builders so the persisted event stream is well-formed.
    yield text.emit_text_done(accumulated.strip())
    yield text.emit_done()
    yield message.emit_done()

    if shutdown_timer and not shutdown_timer.done():
        shutdown_timer.cancel()

    # ── Phase 3 of cancellation (Spec 011): post-stream ────────────
    # Shutdown mid-stream: return without terminal so the framework
    # re-invokes us; the recovery branch above re-streams from a fresh
    # fork of the Claude session.
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
