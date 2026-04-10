# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 15 — Annotations — Attaching file references, citations, and URLs.

Messages can carry annotations that reference files, cite sources, or link
to URLs.  This sample shows how to emit ``file_path``, ``file_citation``,
and ``url_citation`` annotations using the convenience
``output_item_message(text, annotations=[...])`` API.

Usage::

    python sample_15_annotations.py

    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "annotated", "input": "Show me the sources"}'
"""

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
)
from azure.ai.agentserver.responses.models import (
    FileCitationBody,
    FilePath,
    UrlCitationBody,
)

app = ResponsesAgentServerHost()


@app.create("annotations")
async def annotations_handler(request: CreateResponse, context: ResponseContext):
    """Return a message with file_path, file_citation, and url_citation annotations."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    annotations = [
        FilePath(file_id="/reports/monthly-summary.pdf", index=0),
        FilePath(file_id="/exports/data.csv", index=1),
        FileCitationBody(file_id="/sources/research-paper.pdf", index=2, filename="research-paper.pdf"),
        UrlCitationBody(
            url="https://example.com/docs/guide",
            start_index=0,
            end_index=29,
            title="Developer Guide",
        ),
    ]

    async for event in stream.aoutput_item_message(
        "Here are your files and sources.",
        annotations=annotations,
    ):
        yield event

    yield stream.emit_completed()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app.build(), host="0.0.0.0", port=8088)
