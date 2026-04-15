# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 10 — Streaming Upstream (forward to OpenAI-compatible server).

Demonstrates how to forward a request to an upstream OpenAI-compatible API
that returns streaming Server-Sent Events, translating each upstream
chunk into local response events using the ``openai`` Python SDK.

The handler **owns the response lifecycle** — it constructs its own
``response.created``, ``response.in_progress``, and terminal events — while
translating upstream **content events** (output items, text deltas,
function-call arguments, reasoning, tool calls) and yielding them directly.
Both model stacks share the same JSON wire contract, so content events
round-trip with full fidelity.

This is **not** a transparent proxy.  The sample showcases type
compatibility between the two model stacks.  In practice you would add
orchestration logic — filtering outputs, injecting items, calling multiple
upstreams, or transforming content — between the upstream call and the
``yield``.

Usage::

    # Start the server (set upstream endpoint and API key)
    UPSTREAM_ENDPOINT=http://localhost:5211 OPENAI_API_KEY=your-key \
        python sample_10_streaming_upstream.py

    # Send a streaming request
    curl -N -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "gpt-4o-mini", "input": "Say hello!", "stream": true}'
    # -> event: response.created            data: {"response": {"status": "in_progress", ...}}
    # -> event: response.in_progress        data: {"response": {"status": "in_progress", ...}}
    # -> event: response.output_item.added  data: {"item": {"type": "message", ...}}
    # -> event: response.content_part.added data: {"part": {"type": "output_text", ...}}
    # -> event: response.output_text.delta  data: {"delta": "..."}
    # -> ...                                     (more deltas)
    # -> event: response.output_text.done   data: {"text": "..."}
    # -> event: response.output_item.done   data: {"item": {"type": "message", ...}}
    # -> event: response.completed          data: {"response": {"status": "completed", ...}}
"""

import asyncio
import os
from typing import Any, cast

import openai
import openai.types.responses.response_stream_event

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
)

app = ResponsesAgentServerHost()

upstream = openai.AsyncOpenAI(
    base_url=os.environ.get("UPSTREAM_ENDPOINT", "https://api.openai.com/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"),
)


def _build_response_snapshot(request: CreateResponse, context: ResponseContext) -> dict[str, Any]:
    """Construct a response snapshot dict from request + context."""
    snapshot: dict[str, Any] = {
        "id": context.response_id,
        "object": "response",
        "status": "in_progress",
        "model": request.model or "",
        "output": [],
    }
    if request.metadata is not None:
        snapshot["metadata"] = request.metadata
    if request.background is not None:
        snapshot["background"] = request.background
    if request.previous_response_id is not None:
        snapshot["previous_response_id"] = request.previous_response_id
    # Normalize conversation to ConversationReference form.
    conv = request.conversation
    if isinstance(conv, str):
        snapshot["conversation"] = {"id": conv}
    elif isinstance(conv, dict) and conv.get("id"):
        snapshot["conversation"] = {"id": conv["id"]}
    return snapshot


def my_function_tool(x: int) -> int:
    return x * 2


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Forward to upstream with streaming, translate content events back."""

    # Build the upstream request — translate every input item.
    # Both model stacks share the same JSON wire contract, so
    # serializing our Item to dict round-trips to the OpenAI SDK.
    input_items = [item.as_dict() for item in await context.get_input_items()]

    # This handler owns the response lifecycle — construct the
    # response snapshot directly instead of forwarding the upstream's.
    # Seeding from the request preserves metadata, conversation, model.
    snapshot = _build_response_snapshot(request, context)

    # Lifecycle events nest the response snapshot under "response"
    # — matching the SSE wire format.
    yield {"type": "response.created", "response": snapshot}
    yield {"type": "response.in_progress", "response": snapshot}

    # Stream from the upstream.  Translate content events (output
    # items, deltas, etc.) and yield them directly.  Skip upstream
    # lifecycle events — we own the response envelope.
    output_items: list[dict[str, Any]] = []
    upstream_failed = False

    async with await upstream.responses.create(
        model=request.model or "gpt-4o-mini",
        input=input_items,  # type: ignore[arg-type]
        stream=True,
    ) as upstream_stream:
        upstream_stream = cast(
            openai.AsyncStream[openai.types.responses.response_stream_event.ResponseStreamEvent], upstream_stream
        )
        async for event in upstream_stream:
            # Skip lifecycle events — we own the response envelope.
            if event.type in ("response.created", "response.in_progress"):
                continue

            if event.type == "response.completed":
                break

            if event.type == "response.failed":
                upstream_failed = True
                break

            # Do any custom orchestration or manipulation of the event stream here.
            # In this example, we filter out reasoning text events as being too
            # noisy.
            if event.type.startswith("response.reasoning_text"):
                continue

            # Translate the upstream event to a dict via the openai SDK.
            evt = event.model_dump()

            # Clear upstream response_id on output items so the
            # orchestrator's auto-stamp fills in this server's ID.
            if event.type == "response.output_item.added":
                evt.get("item", {}).pop("response_id", None)
            elif event.type == "response.output_item.done":
                item = evt.get("item", {})
                item.pop("response_id", None)
                output_items.append(item)

            yield evt

    # Emit terminal event — the handler decides the outcome.
    if upstream_failed:
        snapshot["status"] = "failed"
        snapshot["error"] = {"code": "server_error", "message": "Upstream request failed"}
        yield {"type": "response.failed", "response": snapshot}
    else:
        snapshot["status"] = "completed"
        snapshot["output"] = output_items
        yield {"type": "response.completed", "response": snapshot}


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
