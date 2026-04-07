# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 11 — Non-Streaming Upstream (forward to upstream, emit items).

Demonstrates forwarding a request to an upstream OpenAI-compatible API
that returns a complete (non-streaming) response, then emitting the
upstream output text as local response events using the ``openai`` SDK.

Pattern: async handler, upstream non-streaming, output_item_message.

Run:
    UPSTREAM_ENDPOINT=http://localhost:5211 OPENAI_API_KEY=your-key \
        python samples/scenarios/sample_11_non_streaming_upstream.py
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
    """Call upstream (non-streaming), emit result as a message item."""
    upstream = openai.AsyncOpenAI(
        base_url=os.environ.get("UPSTREAM_ENDPOINT", "https://api.openai.com/v1"),
        api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"),
    )

    user_text = get_input_text(request) or "hello"

    result = await upstream.responses.create(
        model=request.model or "gpt-4o-mini",
        input=user_text,
    )

    # Extract output text from the upstream response
    output_text = ""
    for item in result.output:
        if item.type == "message":
            for part in item.content:
                if part.type == "output_text":
                    output_text += part.text

    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    for event in stream.output_item_message(output_text):
        yield event

    yield stream.emit_completed()


def main() -> None:
    app.run(host="127.0.0.1", port=5210)


if __name__ == "__main__":
    main()
