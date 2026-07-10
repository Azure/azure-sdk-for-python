# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 16 — Structured Outputs — Returning arbitrary structured JSON.

Return structured JSON data as a ``structured_outputs`` output item.
This sample demonstrates two approaches:

  1. **Convenience** — ``output_item_structured_outputs(data)``
  2. **Full control** — ``add_output_item_structured_outputs()`` builder

Usage::

    python sample_16_structured_outputs.py

    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "analysis", "input": "Analyze the product reviews"}'
"""

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
)
from azure.ai.agentserver.responses.models._generated import StructuredOutputsOutputItem

app = ResponsesAgentServerHost()


# ── Variant 1: Convenience ──────────────────────────────────────────────
@app.create("structured.convenience")
async def convenience_handler(request: CreateResponse, context: ResponseContext):
    """Return structured analysis results using the convenience method."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    result = {
        "sentiment": "positive",
        "confidence": 0.95,
        "topics": ["product-quality", "customer-service"],
        "files": [
            {
                "name": "report.pdf",
                "url": "https://storage.example.com/files/report.pdf",
                "media_type": "application/pdf",
            },
        ],
    }

    async for event in stream.aoutput_item_structured_outputs(result):
        yield event

    yield stream.emit_completed()


# ── Variant 2: Full control ─────────────────────────────────────────────
@app.create("structured.full_control")
async def full_control_handler(request: CreateResponse, context: ResponseContext):
    """Return structured data using the builder for manual lifecycle control."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    builder = stream.add_output_item_structured_outputs()
    item = StructuredOutputsOutputItem(id=builder.item_id, output={"status": "ok", "count": 42})
    yield builder.emit_added(item)
    yield builder.emit_done(item)

    yield stream.emit_completed()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app.build(), host="0.0.0.0", port=8088)
