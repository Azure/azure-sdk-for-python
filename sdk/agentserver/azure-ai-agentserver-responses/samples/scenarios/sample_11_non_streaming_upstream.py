# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 11 — Non-Streaming Upstream (forward to upstream, emit items).

Demonstrates forwarding a request to an upstream API that returns a
complete (non-streaming) response, then emitting the upstream output
items as local response events.

For this sample, the upstream call is simulated. In production,
you would call ``openai.AsyncOpenAI().chat.completions.create()``
(without ``stream=True``) and convert the response.

Pattern: sync handler, upstream non-streaming, output_item_message.

Run:
    python samples/scenarios/sample_11_non_streaming_upstream.py
"""

import asyncio

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    get_input_text,
)


app = ResponsesAgentServerHost()


def mock_upstream_call(prompt: str) -> str:
    """Simulate an upstream LLM that returns a complete response."""
    return f"Upstream non-streaming reply to: {prompt}"


@app.create_handler
def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Call upstream (non-streaming), emit result as a message item."""
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    user_text = get_input_text(request) or "world"
    upstream_reply = mock_upstream_call(user_text)

    yield from stream.output_item_message(upstream_reply)
    yield stream.emit_completed()


def main() -> None:
    app.run(host="127.0.0.1", port=5210)


if __name__ == "__main__":
    main()
