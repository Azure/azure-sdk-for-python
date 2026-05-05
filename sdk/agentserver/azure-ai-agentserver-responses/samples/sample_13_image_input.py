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

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)
from azure.ai.agentserver.responses._data_url import get_media_type, is_data_url, try_decode_bytes
from azure.ai.agentserver.responses.models import ItemMessage, MessageContentInputImageContent

app = ResponsesAgentServerHost()


def _extract_images(items):
    """Extract ``MessageContentInputImageContent`` from expanded input items."""
    images = []
    for item in items:
        if not isinstance(item, ItemMessage):
            continue
        for content in item.content or []:
            if isinstance(content, MessageContentInputImageContent):
                images.append(content)
    return images


# ── Handler 1: Image URL ────────────────────────────────────────────────
@app.create("image_input.url")
async def url_handler(request: CreateResponse, context: ResponseContext):
    """Echo back the image URL received from the caller."""
    items = await context.get_input_items()
    images = _extract_images(items)

    urls = [img.image_url for img in images if img.image_url and not is_data_url(img.image_url)]
    return TextResponse(context, request, text=f"Received {len(urls)} image URL(s): {', '.join(urls)}")


# ── Handler 2: Base64 data URL ──────────────────────────────────────────
@app.create("image_input.base64")
async def base64_handler(request: CreateResponse, context: ResponseContext):
    """Decode inline base64 image data and report media type + size."""
    items = await context.get_input_items()
    images = _extract_images(items)

    results = []
    for img in images:
        if img.image_url and is_data_url(img.image_url):
            raw = try_decode_bytes(img.image_url)
            media = get_media_type(img.image_url)
            size = len(raw) if raw else 0
            results.append(f"{media or 'unknown'} ({size} bytes)")
    return TextResponse(context, request, text=f"Decoded {len(results)} image(s): {'; '.join(results)}")


# ── Handler 3: File ID ──────────────────────────────────────────────────
@app.create("image_input.file_id")
async def file_id_handler(request: CreateResponse, context: ResponseContext):
    """Echo back the file_id received from the caller."""
    items = await context.get_input_items()
    images = _extract_images(items)

    file_ids = [img.file_id for img in images if img.file_id]
    return TextResponse(context, request, text=f"Received {len(file_ids)} file ID(s): {', '.join(file_ids)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app.build(), host="0.0.0.0", port=8088)
