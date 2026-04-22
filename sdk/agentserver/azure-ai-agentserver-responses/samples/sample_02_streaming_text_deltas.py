# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 02 — Token-by-Token Streaming.

Demonstrates token-by-token streaming using ``TextResponse`` with
``text``.  Each chunk yielded by the async generator is
emitted as a separate ``output_text.delta`` SSE event, enabling
real-time token-by-token streaming to the client.

The ``configure`` callback sets ``Response.temperature`` on the response
envelope before ``response.created`` is emitted.

Usage::

    # Start the server
    python sample_02_streaming_text_deltas.py

    # Stream token-by-token deltas
    curl -N -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "streaming", "input": "world", "stream": true}'
    # -> event: response.created            data: {"response": {"status": "in_progress", ...}}
    # -> event: response.in_progress        data: {"response": {"status": "in_progress", ...}}
    # -> event: response.output_item.added  data: {"item": {"type": "message", ...}}
    # -> event: response.content_part.added data: {"part": {"type": "output_text", ...}}
    # -> event: response.output_text.delta  data: {"delta": "Hello"}
    # -> event: response.output_text.delta  data: {"delta": ", "}
    # -> event: response.output_text.delta  data: {"delta": "world"}
    # -> event: response.output_text.delta  data: {"delta": "! "}
    # -> event: response.output_text.delta  data: {"delta": "How "}
    # -> event: response.output_text.delta  data: {"delta": "are "}
    # -> event: response.output_text.delta  data: {"delta": "you?"}
    # -> event: response.output_text.done   data: {"text": "Hello, world! How are you?"}
    # -> event: response.content_part.done  data: {"part": {"type": "output_text", ...}}
    # -> event: response.output_item.done   data: {"item": {"type": "message", ...}}
    # -> event: response.completed          data: {"response": {"status": "completed", ...}}
"""

import asyncio

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)

app = ResponsesAgentServerHost()


@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Stream tokens one at a time using TextResponse."""
    user_text = await context.get_input_text() or "world"

    async def generate_tokens():
        tokens = ["Hello", ", ", user_text, "! ", "How ", "are ", "you?"]
        for token in tokens:
            await asyncio.sleep(0.1)
            yield token

    return TextResponse(
        context,
        request,
        configure=lambda response: setattr(response, "temperature", 0.7),
        text=generate_tokens(),
    )


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
