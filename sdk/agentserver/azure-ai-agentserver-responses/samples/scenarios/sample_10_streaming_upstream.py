# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 10 — Streaming Upstream (forward to OpenAI-compatible server).

Demonstrates how to forward a request to an upstream OpenAI-compatible API
that returns streaming Server-Sent Events, translating each upstream
chunk into local response events using the ``openai`` Python SDK.

The handler creates an ``openai.AsyncOpenAI`` client pointed at an upstream
Responses API endpoint, calls it with ``stream=True``, and maps the
upstream streaming events into local builder-API events.

Pattern: async handler, upstream streaming via openai SDK.

Run:
    UPSTREAM_ENDPOINT=http://localhost:5211 OPENAI_API_KEY=your-key \
        python samples/scenarios/sample_10_streaming_upstream.py
"""

import os
from typing import Any

import openai

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    get_input_text,
)

app = ResponsesAgentServerHost()


@app.create_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: Any,
):
    """Forward to upstream with streaming, translate deltas back."""
    upstream = openai.AsyncOpenAI(
        base_url=os.environ.get("UPSTREAM_ENDPOINT", "https://api.openai.com/v1"),
        api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"),
    )

    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()

    user_text = get_input_text(request) or "hello"
    full_text: list[str] = []

    async with await upstream.responses.create(
        model=request.model or "gpt-4o-mini",
        input=user_text,
        stream=True,
    ) as upstream_stream:
        async for event in upstream_stream:
            if event.type == "response.output_text.delta":
                full_text.append(event.delta)
                yield text.emit_delta(event.delta)

    result_text = "".join(full_text)
    yield text.emit_done(result_text)
    yield message.emit_content_done(text)
    yield message.emit_done()
    yield stream.emit_completed()


def main() -> None:
    app.run(host="127.0.0.1", port=5209)


if __name__ == "__main__":
    main()
