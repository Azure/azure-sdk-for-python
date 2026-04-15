# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 03 — ResponseEventStream — Beyond TextResponse.

When your handler needs to emit function calls, reasoning items, multiple
outputs, or set custom Response properties, step up from ``TextResponse``
to ``ResponseEventStream``.  Start with **convenience generators** — they
handle the event lifecycle for you.  Drop down to **builders** only when
you need fine-grained control over individual events.

This sample shows three ways to emit the same greeting — all produce the
identical SSE event sequence:

  1. **Convenience** — ``output_item_message(text)``
  2. **Streaming**  — ``aoutput_item_message(async_iterable)``
  3. **Builder**    — ``add_output_item_message()`` → ``add_text_content()``
     → ``emit_delta()`` / ``emit_done()``

Usage::

    # Start the server
    python sample_03_full_control.py

    # Send a request
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "greeting", "input": "Hi there!"}'
    # -> {"output": [{"type": "message", "content": [{"type": "output_text",
    #     "text": "Hello! You said: \"Hi there!\""}]}]}

    # Stream the response
    curl -N -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "greeting", "input": "Hi there!", "stream": true}'
    # -> event: response.created            data: {"response": {"status": "in_progress", ...}}
    # -> event: response.in_progress        data: {"response": {"status": "in_progress", ...}}
    # -> event: response.output_item.added  data: {"item": {"type": "message", ...}}
    # -> event: response.content_part.added data: {"part": {"type": "output_text", ...}}
    # -> event: response.output_text.delta  data: {"delta": "Hello! You said: ..."}
    # -> event: response.output_text.done   data: {"text": "Hello! You said: ..."}
    # -> event: response.content_part.done  data: {"part": {"type": "output_text", ...}}
    # -> event: response.output_item.done   data: {"item": {"type": "message", ...}}
    # -> event: response.completed          data: {"response": {"status": "completed", ...}}
"""

import asyncio

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
)

app = ResponsesAgentServerHost()


# ── Variant 1: Convenience ──────────────────────────────────────────────
# Use ``output_item_message(text)`` to emit a complete text message in one
# call.  The convenience generator handles all inner events for you.


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Emit a greeting using the convenience generator."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)

    # Configure Response properties BEFORE emit_created().
    stream.response.temperature = 0.7
    stream.response.max_output_tokens = 1024

    yield stream.emit_created()
    yield stream.emit_in_progress()

    # Emit a complete text message in one call.
    input_text = await context.get_input_text()
    for evt in stream.output_item_message(f'Hello! You said: "{input_text}"'):
        yield evt

    yield stream.emit_completed()


# ── Variant 2: Streaming ────────────────────────────────────────────────
# When your handler calls an LLM that produces tokens incrementally, pass
# an ``AsyncIterable[str]`` to ``aoutput_item_message()``.  Each chunk
# becomes a separate ``response.output_text.delta`` SSE event.


async def handler_streaming(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Stream tokens using the async convenience generator."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)

    yield stream.emit_created()
    yield stream.emit_in_progress()

    # Stream tokens as they arrive — each chunk becomes a delta event.
    async for evt in stream.aoutput_item_message(
        _generate_tokens(await context.get_input_text()),
    ):
        yield evt

    yield stream.emit_completed()


async def _generate_tokens(input_text: str):
    """Simulate an LLM producing tokens one at a time."""
    tokens = ["Hello! ", "You ", "said: ", f'"{input_text}"']
    for token in tokens:
        await asyncio.sleep(0.1)
        yield token


# ── Variant 3: Builder (full event control) ─────────────────────────────
# When you need to interleave non-event work between individual delta/done
# calls within a content part, or set custom properties on the output item
# before ``emit_added()``, drop down to the builder API.


async def handler_builder(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Demonstrate all builder events step by step."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)

    # Configure Response properties BEFORE emit_created().
    stream.response.temperature = 0.7
    stream.response.max_output_tokens = 1024

    yield stream.emit_created()
    yield stream.emit_in_progress()

    # Add a message output item.
    message = stream.add_output_item_message()
    yield message.emit_added()

    # Add text content to the message.
    text_part = message.add_text_content()
    yield text_part.emit_added()

    # Emit the text body — delta first, then the final "done" with full text.
    input_text = await context.get_input_text() or "Hello"
    reply = f'Hello! You said: "{input_text}"'
    yield text_part.emit_delta(reply)

    yield text_part.emit_text_done()
    yield text_part.emit_done()
    yield message.emit_done()

    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
