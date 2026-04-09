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

Uses ``get_input_expanded()`` to inspect the full input array for
``function_call_output`` items.

Pattern: ResponseEventStream, convenience → builder, function_call flow.

Run:
    python samples/scenarios/sample_04_function_calling.py
"""

from __future__ import annotations

import asyncio
import json

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    get_input_expanded,
)
from azure.ai.agentserver.responses.models import FunctionCallOutputItemParam

app = ResponsesAgentServerHost()


def _find_function_call_output(request: CreateResponse) -> str | None:
    """Return the output string from the first function_call_output item, or None."""
    for item in get_input_expanded(request):
        if isinstance(item, FunctionCallOutputItemParam):
            output = item.output
            if isinstance(output, str):
                return output
    return None


# ── Variant 1: Convenience ──────────────────────────────────────────────
# Use ``output_item_function_call()`` and ``output_item_message()`` to emit
# complete output items in one call each.


@app.create_handler
def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Two-turn function-calling handler using convenience generators."""
    tool_output = _find_function_call_output(request)

    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    if tool_output is not None:
        # Turn 2: we have the tool result — produce a final text message.
        yield from stream.output_item_message(f"The weather is: {tool_output}")
    else:
        # Turn 1: ask the client to call get_weather.
        arguments = json.dumps({"location": "Seattle", "unit": "fahrenheit"})
        yield from stream.output_item_function_call("get_weather", "call_weather_1", arguments)

    yield stream.emit_completed()


# ── Variant 2: Builder (full event control) ─────────────────────────────
# When you need to set custom properties on the function call item before
# ``emit_added()``, or interleave non-event work between builder calls,
# use the builder API.


def handler_builder(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Two-turn function-calling handler using the builder API."""
    tool_output = _find_function_call_output(request)

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
        yield text_part.emit_done()
        yield message.emit_content_done(text_part)
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
    app.run(host="127.0.0.1", port=5203)


if __name__ == "__main__":
    main()
