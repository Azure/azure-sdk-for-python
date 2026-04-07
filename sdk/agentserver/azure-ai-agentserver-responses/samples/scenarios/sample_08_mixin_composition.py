# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 08 — Mixin Composition (multi-protocol).

Demonstrates running both the **Invocations** and **Responses** protocols
on a single server using Python's cooperative (mixin) inheritance.

Endpoints exposed:
    POST  /invocations               — Invocation protocol
    POST  /responses                  — Responses protocol
    GET   /readiness                  — Health probe (from core)

Pattern: cooperative inheritance, dual-protocol registration.

Run:
    python samples/scenarios/sample_08_mixin_composition.py
"""

import asyncio
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    get_input_text,
)


class MyHost(InvocationAgentServerHost, ResponsesAgentServerHost):
    pass


app = MyHost()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Echo invocation: returns the message from the JSON body."""
    data = await request.json()
    invocation_id = request.state.invocation_id
    message = data.get("message", "")
    return JSONResponse({
        "invocation_id": invocation_id,
        "status": "completed",
        "output": f"[Invocation] Echo: {message}",
    })


@app.create_handler
def handle_response(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Echo response: returns the user's input text."""
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    yield from stream.output_item_message(f"[Response] Echo: {get_input_text(request)}")
    yield stream.emit_completed()


def main() -> None:
    app.run(host="127.0.0.1", port=5207)


if __name__ == "__main__":
    main()
