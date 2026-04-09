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
)

app = ResponsesAgentServerHost()


@app.create_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Echo the user's input back as a single message."""

    async def _create_text():
        return f"Echo: {await context.get_input_text()}"

    return TextResponse(
        context,
        request,
        create_text=_create_text,
    )


def main() -> None:
    app.run(host="127.0.0.1", port=5200)


if __name__ == "__main__":
    main()
