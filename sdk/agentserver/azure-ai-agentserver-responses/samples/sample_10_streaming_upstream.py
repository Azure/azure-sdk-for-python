# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 10 — Transforming Upstream Proxy.

Shows how to proxy an upstream OpenAI-compatible API while *transforming*
the response stream.  This is not a transparent relay — the handler
injects a system-context prefix, redacts text matching a blocklist, and
appends a word-count annotation after each message.

The pattern is useful whenever you need an LLM but want to post-process
its output: content filtering, citation injection, guardrails, or
multi-model fan-out with result merging.

Both the Responses protocol and the OpenAI SDK share the same SSE wire
format, so content events (deltas, output items) round-trip with full
fidelity — only the parts you touch are changed.

Usage::

    UPSTREAM_ENDPOINT=http://localhost:5211 OPENAI_API_KEY=your-key \
        python sample_10_streaming_upstream.py

    curl -N -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "gpt-4o-mini", "input": "Say hello!", "stream": true}'
"""

import asyncio
import os
import re

import openai

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    ResponseEventStream,
    get_input_expanded,
)

app = ResponsesAgentServerHost()

# Words to redact from upstream output (case-insensitive).
REDACT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(CONFIDENTIAL)\b", re.IGNORECASE),
]

SYSTEM_PREFIX = "[via proxy] "


def _redact(text: str) -> str:
    """Replace blocklisted words with [REDACTED]."""
    for pattern in REDACT_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


@app.create_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Forward to upstream, transform text deltas, annotate output."""
    upstream = openai.AsyncOpenAI(
        base_url=os.environ.get("UPSTREAM_ENDPOINT", "https://api.openai.com/v1"),
        api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"),
    )

    input_items = [item.as_dict() for item in get_input_expanded(request)]

    # Use ResponseEventStream for lifecycle events — no manual snapshots.
    stream = ResponseEventStream(
        response_id=context.response_id,
        model=request.model,
    )
    yield stream.emit_created()
    yield stream.emit_in_progress()

    # Track accumulated text so we can annotate at the end.
    accumulated_text: list[str] = []
    first_delta = True

    async with await upstream.responses.create(
        model=request.model or "gpt-4o-mini",
        input=input_items,  # type: ignore[arg-type]
        stream=True,
    ) as upstream_stream:
        async for event in upstream_stream:
            # Skip upstream lifecycle — we own the response envelope.
            if event.type in (
                "response.created",
                "response.in_progress",
                "response.completed",
            ):
                continue

            if event.type == "response.failed":
                yield stream.emit_failed(
                    error_code="upstream_error",
                    error_message="Upstream request failed",
                )
                return

            evt = event.model_dump()

            # --- Transform: inject prefix into the first text delta ---
            if event.type == "response.output_text.delta":
                delta = _redact(evt.get("delta", ""))
                if first_delta:
                    delta = SYSTEM_PREFIX + delta
                    first_delta = False
                evt["delta"] = delta
                accumulated_text.append(delta)

            # --- Transform: redact completed text ---
            elif event.type == "response.output_text.done":
                evt["text"] = _redact(evt.get("text", ""))

            # Clear upstream response_id so the orchestrator stamps ours.
            if event.type in ("response.output_item.added", "response.output_item.done"):
                evt.get("item", {}).pop("response_id", None)

            yield evt

    # --- Annotate: append word count as a second output item ---
    full_text = "".join(accumulated_text)
    word_count = len(full_text.split())
    annotation = f"\n\n---\n📊 {word_count} words"

    msg = stream.add_output_item_message()
    yield msg.emit_added()
    part = msg.add_text_content()
    yield part.emit_added()
    yield part.emit_delta(annotation)
    yield part.emit_done()
    yield msg.emit_content_done(part)
    yield msg.emit_done()

    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
