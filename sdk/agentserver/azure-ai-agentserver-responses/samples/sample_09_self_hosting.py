# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 09 — Self-Hosting (mounting into an existing Starlette app).

Shows how to mount the ``ResponsesAgentServerHost`` into a parent
Starlette application so responses endpoints live under a custom
URL prefix (e.g. ``/api/responses``).

Because ``ResponsesAgentServerHost`` **is** a Starlette application,
it can be used as a sub-application via ``starlette.routing.Mount``.

Usage::

    # Start the server
    python sample_09_self_hosting.py

    # Responses are mounted under /api
    curl -X POST http://localhost:8000/api/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "test", "input": "Hello!"}'
    # -> {"output": [{"type": "message", "content":
    #     [{"type": "output_text", "text": "Self-hosted echo: Hello!"}]}]}
"""

import asyncio

from starlette.applications import Starlette
from starlette.routing import Mount

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)

# Create the responses host (it IS a Starlette app)
responses_app = ResponsesAgentServerHost()


@responses_app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Echo handler mounted under /api."""
    input_text = await context.get_input_text()
    return TextResponse(context, request, text=f"Self-hosted echo: {input_text}")


# Mount into a parent Starlette app
app = Starlette(
    routes=[
        Mount("/api", app=responses_app),
    ]
)
# Now responses are at /api/responses


def main() -> None:
    import uvicorn

    uvicorn.run(app)


if __name__ == "__main__":
    main()
