# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 01 — Getting Started (echo handler).

Simplest possible handler: reads the user's input text and echoes it back
as a single non-streaming message using ``TextResponse``.

``TextResponse`` handles the full SSE lifecycle automatically:
``response.created`` → ``response.in_progress`` → message/content events
→ ``response.completed``.

Pattern: sync handler, TextResponse with complete text.

Run:
    python samples/scenarios/sample_01_getting_started.py
"""

import asyncio

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
    get_input_text,
)

app = ResponsesAgentServerHost()


@app.create_handler
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Echo the user's input back as a single message."""
    return TextResponse(
        context,
        request,
        create_text=lambda: f"Echo: {get_input_text(request)}",
    )


def main() -> None:
    app.run(host="127.0.0.1", port=5200)


if __name__ == "__main__":
    main()
