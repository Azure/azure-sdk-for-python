# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""StreamingTextDeltas sample for azure-ai-agentserver-responses.

Shows how to stream text token-by-token using ``TextResponse``.
This is the typical pattern when your handler calls an LLM that
produces tokens incrementally.

Run:
    python samples/StreamingTextDeltas/app.py
"""

import asyncio

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)

app = ResponsesAgentServerHost()


async def _generate_tokens():
    """Simulate an LLM producing tokens one at a time."""
    tokens = ["Hello", ", ", "world", "!"]
    for token in tokens:
        await asyncio.sleep(0.1)
        yield token


@app.create_handler
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    return TextResponse(
        context,
        request,
        configure=lambda response: setattr(response, "temperature", 0.7),
        create_text_stream=_generate_tokens,
    )


def main() -> None:
    app.run(host="127.0.0.1", port=5104)


if __name__ == "__main__":
    main()
