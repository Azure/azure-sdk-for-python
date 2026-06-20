# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 11 — Non-Streaming Upstream (call upstream, build event stream).

Demonstrates forwarding a request to an upstream OpenAI-compatible API
that returns a complete (non-streaming) response, then using the builder
API to construct output items for the client.

The handler calls the upstream without streaming, waits for the complete
response, and uses ``output_item_message`` and ``output_item_reasoning_item``
to emit ``output_item.added`` / ``output_item.done`` pairs for each item.

This pattern is useful when your handler needs to inspect or transform the
full response before streaming it to the client — for example, filtering
output items, injecting additional context, or calling multiple upstreams.

Usage::

    # Start the server (set upstream endpoint and API key)
    UPSTREAM_ENDPOINT=http://localhost:5211 OPENAI_API_KEY=your-key \
        python sample_11_non_streaming_upstream.py

    # Send a request
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "gpt-4o-mini", "input": "Say hello!"}'
    # -> {"output": [{"type": "message", "content":
    #     [{"type": "output_text", "text": "Hello! ..."}]}]}

    # Stream the response
    curl -N -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "gpt-4o-mini", "input": "Say hello!", "stream": true}'
    # -> event: response.created            data: {"response": {"status": "in_progress", ...}}
    # -> event: response.in_progress        data: {"response": {"status": "in_progress", ...}}
    # -> event: response.output_item.added  data: {"item": {"type": "message", ...}}
    # -> event: response.content_part.added data: {"part": {"type": "output_text", ...}}
    # -> event: response.output_text.delta  data: {"delta": "..."}
    # -> event: response.output_text.done   data: {"text": "..."}
    # -> event: response.content_part.done  data: {"part": {"type": "output_text", ...}}
    # -> event: response.output_item.done   data: {"item": {"type": "message", ...}}
    # -> event: response.completed          data: {"response": {"status": "completed", ...}}
"""

import asyncio
import os

import openai

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
)

app = ResponsesAgentServerHost()


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Call upstream (non-streaming), emit every output item."""
    upstream = openai.AsyncOpenAI(
        base_url=os.environ.get("UPSTREAM_ENDPOINT", "https://api.openai.com/v1"),
        api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"),
    )

    # Build the upstream request — translate every input item.
    # Both model stacks share the same JSON wire contract, so
    # serializing our Item to dict round-trips to the OpenAI SDK.
    input_items = [item.as_dict() for item in await context.get_input_items()]

    # Call upstream without streaming and get the complete response.
    result = await upstream.responses.create(
        model=request.model or "gpt-4o-mini",
        input=input_items,  # type: ignore[arg-type]
    )

    # Build a standard SSE event stream.  Seed from the request to
    # preserve metadata, conversation, and agent reference.
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    # Translate every upstream output item back into local events.
    # Use the convenience generators to emit the full lifecycle for
    # each output-item type.
    for upstream_item in result.output:
        if upstream_item.type == "message":
            # Extract text content from the message.
            output_text = ""
            for part in upstream_item.content:
                if part.type == "output_text":
                    output_text += part.text
            for event in stream.output_item_message(output_text):
                yield event
        elif upstream_item.type == "reasoning":
            # Extract reasoning summary text.
            summary = ""
            for part in upstream_item.summary:
                if part.type == "summary_text":
                    summary += part.text
            for event in stream.output_item_reasoning_item(summary):
                yield event
        # Add additional item types as needed (function_call, etc.)

    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
