# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 10 — Streaming Upstream (forward to OpenAI-compatible server).

Demonstrates how to forward a request to an upstream OpenAI-compatible API
that returns streaming Server-Sent Events, translating each upstream
chunk into local response events.

For this sample, the upstream is simulated with a simple async generator.
In production, you would replace ``mock_upstream_stream`` with a real
``openai.AsyncOpenAI().chat.completions.create(stream=True)`` call.

Pattern: async handler, upstream streaming via AsyncIterable[str].

Run:
    python samples/scenarios/sample_10_streaming_upstream.py
"""

import asyncio
from typing import Any, AsyncIterator

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    get_input_text,
)

app = ResponsesAgentServerHost()


async def mock_upstream_stream(prompt: str) -> AsyncIterator[str]:
    """Simulate an upstream LLM that streams tokens."""
    tokens = [f"Upstream says: ", "Hello", ", ", prompt, "!"]
    for token in tokens:
        await asyncio.sleep(0.01)
        yield token


@app.create_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: Any,
):
    """Forward to upstream, stream tokens back as deltas."""
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    user_text = get_input_text(request) or "world"
    upstream_tokens = mock_upstream_stream(user_text)

    async for event in stream.aoutput_item_message(upstream_tokens):
        yield event

    yield stream.emit_completed()


def main() -> None:
    app.run(host="127.0.0.1", port=5209)


if __name__ == "__main__":
    main()
