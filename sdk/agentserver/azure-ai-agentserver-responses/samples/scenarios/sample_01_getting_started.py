# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 01 — Getting Started (echo handler).

Simplest possible handler: reads the user's input text and echoes it back
as a single non-streaming message.

Pattern: sync handler, non-streaming text response.

Run:
    python samples/scenarios/sample_01_getting_started.py
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


@app.create_handler
def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Echo the user's input back as a single message."""
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    input_text = get_input_text(request)
    yield from stream.output_item_message(f"Echo: {input_text}")
    yield stream.emit_completed()


def main() -> None:
    app.run(host="127.0.0.1", port=5200)


if __name__ == "__main__":
    main()
