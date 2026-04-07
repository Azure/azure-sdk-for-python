# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 02 — Streaming Text Deltas.

Demonstrates token-by-token streaming using an async handler and
``aoutput_item_message`` with an async iterable of string chunks.
Each chunk is emitted as a separate ``output_text.delta`` SSE event,
enabling real-time streaming to the client.

Pattern: async handler, streaming deltas via AsyncIterable[str].

Run:
    python samples/scenarios/sample_02_streaming_text_deltas.py
"""

import asyncio
from typing import Any

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
    """Stream tokens one at a time using aoutput_item_message."""
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    user_text = get_input_text(request) or "world"

    async def generate_tokens():
        tokens = ["Hello", ", ", user_text, "! ", "How ", "are ", "you?"]
        for token in tokens:
            await asyncio.sleep(0.1)
            yield token

    async for event in stream.aoutput_item_message(generate_tokens()):
        yield event
    yield stream.emit_completed()


def main() -> None:
    app.run(host="127.0.0.1", port=5201)


if __name__ == "__main__":
    main()
