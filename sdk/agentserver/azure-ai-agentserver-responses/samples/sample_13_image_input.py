# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 13 — Image Input — Receiving images from the caller.

Callers can send images in three ways: via URL, as a base64 ``data:`` URL
embedded in the ``image_url`` field, or via ``file_id``.  This sample
registers a handler for each input method and echoes back what was received.

The ``data_url`` utility module provides helpers for decoding inline
base64 image data.

Usage::

    python sample_13_image_input.py

    # URL input
    curl -X POST http://localhost:8088/responses?handler=url \
        -H "Content-Type: application/json" \
        -d '{
          "model": "img", "input": [
            {"role": "user", "content": [
              {"type": "input_image", "image_url": "https://example.com/photo.png"}
            ]}
          ]
        }'

    # Base64 data URL input
    curl -X POST http://localhost:8088/responses?handler=base64 \
        -H "Content-Type: application/json" \
        -d '{
          "model": "img", "input": [
            {"role": "user", "content": [
              {"type": "input_image", "image_url": "data:image/png;base64,iVBORw0KGgo..."}
            ]}
          ]
        }'

    # File ID input
    curl -X POST http://localhost:8088/responses?handler=fileid \
        -H "Content-Type: application/json" \
        -d '{
          "model": "img", "input": [
            {"role": "user", "content": [
              {"type": "input_image", "file_id": "/images/photo.png"}
            ]}
          ]
        }'
"""

import asyncio

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)
from azure.ai.agentserver.responses._data_url import (
    get_media_type,
    is_data_url,
    try_decode_bytes,
)

app = ResponsesAgentServerHost()


def _extract_images(items):
    """Extract ``input_image`` content parts from expanded input items."""
    images = []
    for item in items:
        if item.get("type") != "message":
            continue
        for content in item.get("content") or []:
            if isinstance(content, dict) and content.get("type") == "input_image":
                images.append(content)
    return images


# ── Handler 1: Image URL (the registered handler) ───────────────────────
# One host has exactly one ``@app.response_handler``. Handlers 2 and 3 below
# are undecorated reference implementations — swap the decorator to run them.
@app.response_handler
async def url_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Echo back the image URL received from the caller."""
    items = await context.get_input_items()
    images = _extract_images(items)

    urls = [img.get("image_url") for img in images if img.get("image_url") and not is_data_url(img["image_url"])]
    return TextResponse(context, request, text=f"Received {len(urls)} image URL(s): {', '.join(urls)}")


# ── Handler 2: Base64 data URL ──────────────────────────────────────────
async def base64_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Decode inline base64 image data and report media type + size."""
    items = await context.get_input_items()
    images = _extract_images(items)

    results = []
    for img in images:
        image_url = img.get("image_url")
        if image_url and is_data_url(image_url):
            raw = try_decode_bytes(image_url)
            media = get_media_type(image_url)
            size = len(raw) if raw else 0
            results.append(f"{media or 'unknown'} ({size} bytes)")
    return TextResponse(context, request, text=f"Decoded {len(results)} image(s): {'; '.join(results)}")


# ── Handler 3: File ID ──────────────────────────────────────────────────
async def file_id_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Echo back the file_id received from the caller."""
    items = await context.get_input_items()
    images = _extract_images(items)

    file_ids = [img.get("file_id") for img in images if img.get("file_id")]
    return TextResponse(
        context,
        request,
        text=f"Received {len(file_ids)} file ID(s): {', '.join(file_ids)}",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app.build(), host="0.0.0.0", port=8088)
