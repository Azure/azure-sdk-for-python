# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 17 — Durable Claude (stateful conversation via Claude Agent SDK).

Wraps the **Claude Agent SDK** (``claude-agent-sdk``) in a steerable
durable response handler.  The Claude SDK is the upstream framework
that owns conversational durability — this handler is the bridge.

Recovery model:

- The Claude session UUID is stamped into ``context.durable_metadata`` as
  ``claude_session_id`` so each turn (and each recovered attempt within
  a turn) resumes the same session.
- Before sending the user's input, the handler reads the session's
  persisted message history via
  ``claude_agent_sdk.get_session_messages``. If the LAST message in
  that history is a user message whose text equals this turn's input,
  the handler skips ``client.query`` — Claude already has the message
  from a prior attempt and only owes us the assistant reply. Otherwise
  the handler sends.
- This means the **upstream session JSONL is the source of truth** for
  "did I already send this turn". No handler-managed metadata
  watermark, no flush ordering between metadata writes and SDK calls,
  no race window between persistence and side effect.
- On a steered cancellation that fires *before* this handler did any
  work (pre-entry), we still send the user input to Claude so the
  message is preserved in the conversation history — otherwise the
  newer turn that supersedes us would lose context.
- On crash recovery, we never *fork* the Claude session. Forking would
  create a fresh branch and abandon any progress in the original
  session that hadn't yet committed. We simply resume the same session.

Known limitation: if a prior turn's user input was identical to this
turn's input AND that prior turn completed normally, the detection
heuristic ("last message is user with matching text") cannot distinguish
the recovered mid-turn case from the legitimate repeat. The handler
will skip in this rare case and the new turn will not be sent to
Claude. For typical conversational use this is rare; for workflows
where this might happen, decompose into smaller queries or pass an
explicit disambiguator at the application level.

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
    SessionMessage,
    TextBlock,
    get_session_messages,
)

from azure.ai.agentserver.responses import (
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


def _claude_options_for(context) -> ClaudeAgentOptions:
    """Build SDK options that resume the existing session or open a new one."""
    existing = context.durable_metadata.get("claude_session_id")
    if existing:
        return ClaudeAgentOptions(resume=existing)
    new_id = str(uuid.uuid4())
    context.durable_metadata["claude_session_id"] = new_id
    return ClaudeAgentOptions(session_id=new_id)


def _extract_user_text(session_message: SessionMessage) -> str | None:
    """Extract text content from a Claude SessionMessage if it's a user message."""
    if session_message.type != "user":
        return None
    msg = session_message.message
    if not isinstance(msg, dict):
        return None
    content = msg.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts) if parts else None
    return None


async def _send_input_if_not_in_session(
    client: ClaudeSDKClient,
    session_id: str,
    context: ResponseContext,
) -> None:
    """Send this turn's input to Claude unless it is already in the session.

    Detection rule: if the LAST message in the persisted session JSONL is a
    user message whose text equals this turn's input, we have already sent
    it on a prior attempt that didn't complete its assistant reply — skip
    the send and let ``receive_response`` deliver whatever continuation
    the SDK has. Otherwise, send.

    The upstream session is the source of truth here — no handler-managed
    watermark, no metadata flush ordering. The detection is deterministic
    for the realistic crash window (within an in-flight turn). The one
    edge case is when a prior turn legitimately completed AND the user's
    NEW input happens to be identical to the prior input; the heuristic
    cannot distinguish that from a recovered mid-turn and will skip. For
    typical conversational use this is rare; document it if it matters.
    """
    input_text = await context.get_input_text()

    # Source of truth: the upstream's persisted session JSONL.
    try:
        history = get_session_messages(session_id) or []
    except Exception:  # pylint: disable=broad-exception-caught
        # Session has no prior messages on disk yet (fresh session).
        history = []

    if history:
        last_user_text = _extract_user_text(history[-1])
        if last_user_text == input_text:
            # Already in the session — skip the query, let receive_response
            # surface whatever assistant content is queued.
            return

    await client.query(input_text)


def _build_resumption_response(context: ResponseContext, request: CreateResponse) -> ResponseObject:
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
    # ── Recovery branch ─────────────────────────────────────────────
    if context.is_recovery:
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
        if cancellation_signal.is_set() and not context.client_cancelled and not context.shutdown.is_set():
            sdk_options = _claude_options_for(context)
            session_id = context.durable_metadata["claude_session_id"]
            async with ClaudeSDKClient(options=sdk_options) as client:
                await _send_input_if_not_in_session(client, session_id, context)
            yield stream.emit_completed()
        return

    yield stream.emit_in_progress()

    shutdown_timer: asyncio.Task | None = None
    if _SIMULATE_SHUTDOWN_MS > 0:
        shutdown_timer = asyncio.create_task(_simulate_shutdown(context))

    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()

    sdk_options = _claude_options_for(context)
    session_id = context.durable_metadata["claude_session_id"]
    accumulated = ""

    async with ClaudeSDKClient(options=sdk_options) as client:
        # Upstream-history-gated send: skipped on recovery when Claude's
        # session JSONL already has our user message as its tail.
        await _send_input_if_not_in_session(client, session_id, context)

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
                        context.durable_metadata["claude_session_id"] = sdk_session_id
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
    if context.shutdown.is_set():
        return

    yield stream.emit_completed()


async def _simulate_shutdown(context: ResponseContext) -> None:
    """Fire a SHUTTING_DOWN signal after a delay (local testing only)."""
    await asyncio.sleep(_SIMULATE_SHUTDOWN_MS / 1000.0)
    context.shutdown.set()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
