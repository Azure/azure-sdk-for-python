# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 04 — Function Calling (two-turn pattern).

Demonstrates a two-turn function-calling flow:

  **Turn 1** — The handler emits a ``function_call`` output item asking the
  client to call ``get_weather`` with specific arguments.

  **Turn 2** — The client re-invokes the handler with a
  ``function_call_output`` item in the input.  The handler reads that output
  and responds with a text message.

Uses ``get_input_expanded()`` to inspect the full input array for
``function_call_output`` items.

Pattern: sync handler, function_call → function_call_output → message.

Run:
    python samples/scenarios/sample_04_function_calling.py
"""

import asyncio
import json

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    get_input_expanded,
)
from azure.ai.agentserver.responses.models import ItemType

app = ResponsesAgentServerHost()


def _find_function_call_output(request: CreateResponse) -> str | None:
    """Return the output string from the first function_call_output item, or None."""
    for item in get_input_expanded(request):
        if isinstance(item, str):
            continue
        if item.get("type") == ItemType.FUNCTION_CALL_OUTPUT:
            return item.get("content", {}).get("output")
    return None


@app.create_handler
def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Two-turn function-calling handler."""
    tool_output = _find_function_call_output(request)

    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    if tool_output is not None:
        # Turn 2: we have the tool result — produce a final text message.
        yield from stream.output_item_message(f"The weather is: {tool_output}")
    else:
        # Turn 1: ask the client to call get_weather.
        arguments = json.dumps({"location": "Seattle", "unit": "fahrenheit"})
        yield from stream.output_item_function_call(
            "get_weather", "call_weather_1", arguments
        )

    yield stream.emit_completed()


def main() -> None:
    app.run(host="127.0.0.1", port=5203)


if __name__ == "__main__":
    main()
