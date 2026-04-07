# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 06 — Multi-Output (reasoning + message).

Produces two output items in a single response:

  1. A **reasoning item** with a summary of the agent's internal thinking.
  2. A **message** with the final answer presented to the user.

This mirrors the pattern used by reasoning-capable models (o1, o3, etc.)
that expose a chain-of-thought before the answer.

Pattern: sync handler, reasoning item followed by text message.

Run:
    python samples/scenarios/sample_06_multi_output.py
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
    """Emit a reasoning item and then a message."""
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    input_text = get_input_text(request) or "What is 2+2?"

    # Output 1: reasoning (chain-of-thought)
    yield from stream.output_item_reasoning_item(
        f"Let me think about: \"{input_text}\"..."
    )

    # Output 2: final answer
    yield from stream.output_item_message(
        f"After careful thought, here is my answer to: \"{input_text}\""
    )

    yield stream.emit_completed()


def main() -> None:
    app.run(host="127.0.0.1", port=5205)


if __name__ == "__main__":
    main()
