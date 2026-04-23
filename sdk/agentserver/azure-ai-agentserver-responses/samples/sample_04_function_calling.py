# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 04 — Function Calling (two-turn pattern).

Demonstrates a two-turn function-calling flow:

  **Turn 1** — The handler emits a ``function_call`` output item asking the
  client to call ``get_weather`` with specific arguments.

  **Turn 2** — The client re-invokes the handler with a
  ``function_call_output`` item in the input.  The handler reads that output
  and responds with a text message.

The handler is shown first using convenience generators, then with full
builder control.

Usage::

    # Start the server
    python sample_04_function_calling.py

    # Turn 1 — triggers a function call
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "test", "input": "What is the weather in Seattle?"}'
    # -> {"output": [{"type": "function_call", "name": "get_weather",
    #     "call_id": "call_weather_1", "arguments": "{\"location\": \"Seattle\", ...}"}]}

    # Turn 2 — submit function output, receive text
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "test", "input": [{"type": "function_call_output",
             "call_id": "call_weather_1", "output": "72F and sunny"}]}'
    # -> {"output": [{"type": "message", "content": [{"type": "output_text",
    #     "text": "The weather is: 72F and sunny"}]}]}
"""

from __future__ import annotations

import asyncio
import json

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
)
from azure.ai.agentserver.responses.models import FunctionCallOutputItemParam

app = ResponsesAgentServerHost()


async def _find_function_call_output(context: ResponseContext) -> str | None:
    """Return the output string from the first function_call_output item, or None."""
    for item in await context.get_input_items():
        if isinstance(item, FunctionCallOutputItemParam):
            output = item.output
            if isinstance(output, str):
                return output
    return None


# ── Variant 1: Convenience ──────────────────────────────────────────────
# Use ``output_item_function_call()`` and ``output_item_message()`` to emit
# complete output items in one call each.


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Two-turn function-calling handler using convenience generators."""
    tool_output = await _find_function_call_output(context)

    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    if tool_output is not None:
        # Turn 2: we have the tool result — produce a final text message.
        async for event in stream.aoutput_item_message(f"The weather is: {tool_output}"):
            yield event
    else:
        # Turn 1: ask the client to call get_weather.
        arguments = json.dumps({"location": "Seattle", "unit": "fahrenheit"})
        async for event in stream.aoutput_item_function_call("get_weather", "call_weather_1", arguments):
            yield event

    yield stream.emit_completed()


# ── Variant 2: Builder (full event control) ─────────────────────────────
# When you need to set custom properties on the function call item before
# ``emit_added()``, or interleave non-event work between builder calls,
# use the builder API.


async def handler_builder(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Two-turn function-calling handler using the builder API."""
    tool_output = await _find_function_call_output(context)

    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    if tool_output is not None:
        # Turn 2: function output received — return the weather as text.
        message = stream.add_output_item_message()
        yield message.emit_added()

        text_part = message.add_text_content()
        yield text_part.emit_added()

        reply = f"The weather is: {tool_output}"
        yield text_part.emit_delta(reply)
        yield text_part.emit_text_done()
        yield text_part.emit_done()
        yield message.emit_done()
    else:
        # Turn 1: emit a function call for "get_weather".
        arguments = json.dumps({"location": "Seattle", "unit": "fahrenheit"})
        fc = stream.add_output_item_function_call(name="get_weather", call_id="call_weather_1")
        yield fc.emit_added()
        yield fc.emit_arguments_delta(arguments)
        yield fc.emit_arguments_done(arguments)
        yield fc.emit_done()

    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
