# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 12 — Image Generation — Returning images from a handler.

This sample demonstrates three ways to return base64-encoded image data
as an ``image_generation_call`` output item:

  1. **Convenience** — ``output_item_image_gen_call(result_b64)`` one-liner.
  2. **Streaming partials** — Use the builder to emit partial images
     between the ``generating`` and ``completed`` states.
  3. **Full control** — Manual builder lifecycle with ``emit_added()``,
     state transitions, and ``emit_done(result)``.

Usage::

    python sample_12_image_generation.py

    # Convenience handler
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "image", "input": "Draw a red square"}'

    # Streaming partials
    curl -N -X POST http://localhost:8088/responses?handler=streaming \
        -H "Content-Type: application/json" \
        -d '{"model": "image", "input": "Draw a blue circle", "stream": true}'
"""

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
)

app = ResponsesAgentServerHost()

# A tiny 1x1 red PNG pixel (base64-encoded) used as a synthetic image.
TINY_IMAGE_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGP4z8BQDwAEgAF/pooBPQAAAABJRU5ErkJggg=="


# ── Variant 1: Convenience ──────────────────────────────────────────────
@app.create("image.convenience")
async def convenience_handler(request: CreateResponse, context: ResponseContext):
    """Return an image using the convenience one-liner."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    # One call emits: added → in_progress → generating → completed → done(result)
    async for event in stream.aoutput_item_image_gen_call(TINY_IMAGE_B64):
        yield event

    yield stream.emit_completed()


# ── Variant 2: Streaming partial images ─────────────────────────────────
@app.create("image.streaming")
async def streaming_handler(request: CreateResponse, context: ResponseContext):
    """Stream partial image renders before the final result."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    ig = stream.add_output_item_image_gen_call()
    yield ig.emit_added()
    yield ig.emit_in_progress()
    yield ig.emit_generating()

    # Simulate streaming partial renders
    for i in range(3):
        yield ig.emit_partial_image(f"partial_{i}_{TINY_IMAGE_B64[:20]}")

    yield ig.emit_completed()
    yield ig.emit_done(TINY_IMAGE_B64)

    yield stream.emit_completed()


# ── Variant 3: Full control ─────────────────────────────────────────────
@app.create("image.full_control")
async def full_control_handler(request: CreateResponse, context: ResponseContext):
    """Full manual control over the image generation lifecycle."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    ig = stream.add_output_item_image_gen_call()
    yield ig.emit_added()
    yield ig.emit_in_progress()
    yield ig.emit_generating()
    yield ig.emit_completed()
    yield ig.emit_done(TINY_IMAGE_B64)

    yield stream.emit_completed()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app.build(), host="0.0.0.0", port=8088)
