# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 14 — File Inputs — Receiving files from the caller.

Callers can send files in three ways: as a base64 ``data:`` URL in
``file_data``, via ``file_url``, or via ``file_id``.  This sample
registers a handler for each input method and echoes back what was received.

Usage::

    python sample_14_file_inputs.py

    # Base64 data URL input
    curl -X POST http://localhost:8088/responses?handler=base64 \
        -H "Content-Type: application/json" \
        -d '{
          "model": "files", "input": [
            {"role": "user", "content": [
              {"type": "input_file", "file_data": "data:application/pdf;base64,JVBERi0..."}
            ]}
          ]
        }'

    # URL input
    curl -X POST http://localhost:8088/responses?handler=url \
        -H "Content-Type: application/json" \
        -d '{
          "model": "files", "input": [
            {"role": "user", "content": [
              {"type": "input_file", "file_url": "https://example.com/report.pdf"}
            ]}
          ]
        }'

    # File ID input
    curl -X POST http://localhost:8088/responses?handler=fileid \
        -H "Content-Type: application/json" \
        -d '{
          "model": "files", "input": [
            {"role": "user", "content": [
              {"type": "input_file", "file_id": "/reports/summary.pdf"}
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


def _extract_files(items):
    """Extract ``input_file`` content parts from expanded input items."""
    files = []
    for item in items:
        if item.get("type") != "message":
            continue
        for content in item.get("content") or []:
            if isinstance(content, dict) and content.get("type") == "input_file":
                files.append(content)
    return files


# ── Handler 1: Base64 data URL (the registered handler) ─────────────────
# One host has exactly one ``@app.response_handler``. Handlers 2 and 3 below
# are undecorated reference implementations — swap the decorator to run them.
@app.response_handler
async def base64_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Decode inline base64 file data and report media type + size."""
    items = await context.get_input_items()
    files = _extract_files(items)

    results = []
    for f in files:
        file_data = f.get("file_data")
        if file_data and is_data_url(file_data):
            raw = try_decode_bytes(file_data)
            media = get_media_type(file_data)
            size = len(raw) if raw else 0
            results.append(f"{media or 'unknown'} ({size} bytes)")
    return TextResponse(context, request, text=f"Decoded {len(results)} file(s): {'; '.join(results)}")


# ── Handler 2: File URL ─────────────────────────────────────────────────
async def url_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Echo back the file URL received from the caller."""
    items = await context.get_input_items()
    files = _extract_files(items)

    urls = [f.get("file_url") for f in files if f.get("file_url")]
    return TextResponse(context, request, text=f"Received {len(urls)} file URL(s): {', '.join(urls)}")


# ── Handler 3: File ID ──────────────────────────────────────────────────
async def file_id_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Echo back the file_id received from the caller."""
    items = await context.get_input_items()
    files = _extract_files(items)

    file_ids = [f.get("file_id") for f in files if f.get("file_id")]
    return TextResponse(
        context,
        request,
        text=f"Received {len(file_ids)} file ID(s): {', '.join(file_ids)}",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app.build(), host="0.0.0.0", port=8088)
