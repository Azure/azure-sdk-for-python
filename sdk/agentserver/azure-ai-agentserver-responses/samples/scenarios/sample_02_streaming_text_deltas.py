# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 02 — Streaming Text Deltas.

Demonstrates token-by-token streaming using ``TextResponse`` with
``create_text_stream``.  Each chunk yielded by the async generator is
emitted as a separate ``output_text.delta`` SSE event, enabling
real-time streaming to the client.

``TextResponse`` handles the full SSE lifecycle automatically.

Pattern: TextResponse with create_text_stream (AsyncIterable[str]).

Run:
    python samples/scenarios/sample_02_streaming_text_deltas.py
"""

import asyncio

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
    get_input_text,
)

app = ResponsesAgentServerHost()


@app.create_handler
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Stream tokens one at a time using TextResponse."""
    user_text = get_input_text(request) or "world"

    async def generate_tokens():
        tokens = ["Hello", ", ", user_text, "! ", "How ", "are ", "you?"]
        for token in tokens:
            await asyncio.sleep(0.1)
            yield token

    return TextResponse(
        context,
        request,
        create_text_stream=generate_tokens,
    )


def main() -> None:
    app.run(host="127.0.0.1", port=5201)


if __name__ == "__main__":
    main()
