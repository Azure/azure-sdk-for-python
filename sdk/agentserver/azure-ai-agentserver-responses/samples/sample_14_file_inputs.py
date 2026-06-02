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

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)
from azure.ai.agentserver.responses._data_url import get_media_type, is_data_url, try_decode_bytes
from azure.ai.agentserver.responses.models import ItemMessage, MessageContentInputFileContent

app = ResponsesAgentServerHost()


def _extract_files(items):
    """Extract ``MessageContentInputFileContent`` from expanded input items."""
    files = []
    for item in items:
        if not isinstance(item, ItemMessage):
            continue
        for content in item.content or []:
            if isinstance(content, MessageContentInputFileContent):
                files.append(content)
    return files


# ── Handler 1: Base64 data URL ──────────────────────────────────────────
@app.create("file_input.base64")
async def base64_handler(request: CreateResponse, context: ResponseContext):
    """Decode inline base64 file data and report media type + size."""
    items = await context.get_input_items()
    files = _extract_files(items)

    results = []
    for f in files:
        if f.file_data and is_data_url(f.file_data):
            raw = try_decode_bytes(f.file_data)
            media = get_media_type(f.file_data)
            size = len(raw) if raw else 0
            results.append(f"{media or 'unknown'} ({size} bytes)")
    return TextResponse(context, request, text=f"Decoded {len(results)} file(s): {'; '.join(results)}")


# ── Handler 2: File URL ─────────────────────────────────────────────────
@app.create("file_input.url")
async def url_handler(request: CreateResponse, context: ResponseContext):
    """Echo back the file URL received from the caller."""
    items = await context.get_input_items()
    files = _extract_files(items)

    urls = [f.file_url for f in files if f.file_url]
    return TextResponse(context, request, text=f"Received {len(urls)} file URL(s): {', '.join(urls)}")


# ── Handler 3: File ID ──────────────────────────────────────────────────
@app.create("file_input.file_id")
async def file_id_handler(request: CreateResponse, context: ResponseContext):
    """Echo back the file_id received from the caller."""
    items = await context.get_input_items()
    files = _extract_files(items)

    file_ids = [f.file_id for f in files if f.file_id]
    return TextResponse(context, request, text=f"Received {len(file_ids)} file ID(s): {', '.join(file_ids)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app.build(), host="0.0.0.0", port=8088)
