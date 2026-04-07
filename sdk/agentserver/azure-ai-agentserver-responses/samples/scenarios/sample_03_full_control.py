# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 03 — Full Control (low-level builder API).

Shows how to use the low-level builder API for maximum control over every
SSE event emitted.  Instead of the one-shot convenience methods like
``output_item_message()``, this sample uses:

  - ``add_output_item_message()``  → returns an ``OutputItemMessageBuilder``
  - ``builder.add_text_content()`` → returns a ``TextContentBuilder``
  - Individual ``emit_added()``, ``emit_delta()``, ``emit_done()`` calls

Also demonstrates setting custom properties on ``stream.response`` before
emitting lifecycle events.

Pattern: explicit builder usage, response property customization.

Run:
    python samples/scenarios/sample_03_full_control.py
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
    """Demonstrate all builder events step by step."""
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)

    # Customise the response envelope before emitting lifecycle events.
    stream.response.model = request.model or "custom-model"
    if request.metadata:
        stream.response.metadata = request.metadata

    yield stream.emit_created()
    yield stream.emit_in_progress()

    # --- Build a message output item manually ---
    message = stream.add_output_item_message()
    yield message.emit_added()

    # Add a text content part with explicit delta control.
    text_part = message.add_text_content()
    yield text_part.emit_added()

    input_text = get_input_text(request) or "Hello"
    words = input_text.split()
    for i, word in enumerate(words):
        delta = word if i == 0 else f" {word}"
        yield text_part.emit_delta(delta)

    yield text_part.emit_done()
    yield message.emit_content_done(text_part)
    yield message.emit_done()

    yield stream.emit_completed()


def main() -> None:
    app.run(host="127.0.0.1", port=5202)


if __name__ == "__main__":
    main()
