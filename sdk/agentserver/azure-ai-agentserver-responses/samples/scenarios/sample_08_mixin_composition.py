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

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
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
def handle_response(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Echo response: returns the user's input text."""
    return TextResponse(
        context,
        request,
        create_text=lambda: f"[Response] Echo: {get_input_text(request)}",
    )


def main() -> None:
    app.run(host="127.0.0.1", port=5207)


if __name__ == "__main__":
    main()
