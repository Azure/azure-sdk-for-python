# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 09 — Self-Hosting (mounting into an existing Starlette app).

Shows how to mount the ``ResponsesAgentServerHost`` into a parent
Starlette application so responses endpoints live under a custom
URL prefix (e.g. ``/api/responses``).

Because ``ResponsesAgentServerHost`` **is** a Starlette application,
it can be used as a sub-application via ``starlette.routing.Mount``.

Pattern: Starlette Mount, sub-application composition.

Run:
    python samples/scenarios/sample_09_self_hosting.py
"""

import asyncio

from starlette.applications import Starlette
from starlette.routing import Mount

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    get_input_text,
)

# Create the responses host (it IS a Starlette app)
responses_app = ResponsesAgentServerHost()


@responses_app.create_handler
def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Echo handler mounted under /api."""
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    yield from stream.output_item_message(f"Self-hosted echo: {get_input_text(request)}")
    yield stream.emit_completed()


# Mount into a parent Starlette app
app = Starlette(routes=[
    Mount("/api", app=responses_app),
])
# Now responses are at /api/responses


def main() -> None:
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5208)


if __name__ == "__main__":
    main()
