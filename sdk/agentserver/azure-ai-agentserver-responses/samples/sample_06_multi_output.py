# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 06 — Multi-Output — Math Problem Solver with Reasoning.

Builds a math problem solver that shows its work.  The agent emits a
**reasoning** item (the thought process) followed by a **message** item
(the final answer).  This demonstrates streaming multiple output types in
a single response — first using convenience generators, then with full
builder control.

Usage::

    # Start the server
    python sample_06_multi_output.py

    # Send a math question
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "math", "input": "What is 6 times 7?"}'
    # -> {"output": [{"type": "reasoning", ...},
    #     {"type": "message", "content": [{"type": "output_text",
    #      "text": "The answer is 42. Here's how: 6 × 7 = 42. ..."}]}]}

    # Stream to see reasoning + answer arrive in sequence
    curl -N -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "math", "input": "What is 6 times 7?", "stream": true}'
    # -> event: response.created            data: {"response": {"status": "in_progress", ...}}
    # -> event: response.in_progress        data: {"response": {"status": "in_progress", ...}}
    # -> event: response.output_item.added  data: {"item": {"type": "reasoning", ...}}
    # -> event: response.output_item.done   data: {"item": {"type": "reasoning", ...}}
    # -> event: response.output_item.added  data: {"item": {"type": "message", ...}}
    # -> event: response.content_part.added data: {"part": {"type": "output_text", ...}}
    # -> event: response.output_text.delta  data: {"delta": "The answer is 42. ..."}
    # -> event: response.output_text.done   data: {"text": "The answer is 42. ..."}
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
# Use ``output_item_reasoning_item()`` and ``output_item_message()`` to
# emit complete output items with one call each.


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Emit reasoning and answer using convenience generators."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    question = await context.get_input_text() or "What is 6 times 7?"

    yield stream.emit_created()
    yield stream.emit_in_progress()

    # Output item 0: Reasoning — show the thought process.
    thought = (
        f'The user asked: "{question}". '
        "I need to identify the mathematical operation, "
        "compute the result, and explain the steps."
    )
    for evt in stream.output_item_reasoning_item(thought):
        yield evt

    # Output item 1: Message — the final answer.
    answer = "The answer is 42. Here's how: 6 × 7 = 42. The multiplication of 6 and 7 gives 42."
    for evt in stream.output_item_message(answer):
        yield evt

    yield stream.emit_completed()


# ── Variant 2: Builder (full event control) ─────────────────────────────
# When you need multiple summary parts in a single reasoning item, set
# custom properties on output items before ``emit_added()``, or interleave
# non-event work between builder calls, use the builder API.


async def handler_builder(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Emit reasoning and answer using the builder API."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    question = await context.get_input_text() or "What is 6 times 7?"

    yield stream.emit_created()
    yield stream.emit_in_progress()

    # Output item 0: Reasoning — show the thought process.
    reasoning = stream.add_output_item_reasoning_item()
    yield reasoning.emit_added()

    summary = reasoning.add_summary_part()
    yield summary.emit_added()

    thought = (
        f'The user asked: "{question}". '
        "I need to identify the mathematical operation, "
        "compute the result, and explain the steps."
    )
    yield summary.emit_text_delta(thought)
    yield summary.emit_text_done(thought)
    yield summary.emit_done()

    yield reasoning.emit_done()

    # Output item 1: Message — the final answer.
    message = stream.add_output_item_message()
    yield message.emit_added()

    text_part = message.add_text_content()
    yield text_part.emit_added()

    answer = "The answer is 42. Here's how: 6 × 7 = 42. The multiplication of 6 and 7 gives 42."
    yield text_part.emit_delta(answer)
    yield text_part.emit_text_done()
    yield text_part.emit_done()
    yield message.emit_done()

    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
